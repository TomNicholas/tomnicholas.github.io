---
date: "2026-06-10"
title: "Virtual chunks that just work — but securely"
description: |
  Delivering enterprise-grade access control for virtual chunks - surprisingly subtle!
thumbnail: images/cover.jpg
tags:
- arraylake
- enterprise
- icechunk
- zarr
- virtual-zarr
- virtualizarr
- security
kernelspec:
  name: python3
  display_name: 'Python 3'
---

(Originally posted on the [Earthmover blog](https://earthmover.io/blog/secure-virtual-chunks))

Tl;dr: Delivering enterprise-grade access control for [virtual chunks](https://www.earthmover.io/blog/virtual-zarr) alongside security-by-default for open-source users took some careful design.

## Virtual chunks are powerful

"Virtual chunks" allow ingesting archival data formats such as netCDF into Icechunk [without duplicating data](https://www.earthmover.io/blog/virtual-zarr).
They play a similar role that an "external table" does in more traditional databases.

A virtual chunk is really just a pointer to a arbitrary location in storage, allowing efficient fetching of that specific byte range via a single request.
In fact, here is the definition of a virtual chunk reference, from Icechunk's [source code](https://github.com/earth-mover/icechunk/blob/7562c4db9e3f002451ccc84ee2d620700740a32b/icechunk-format/src/manifest.rs#L393):

```{code-block} rust
:caption: Definition of a virtual chunk within the Icechunk format.

pub struct VirtualChunkRef {
    pub location: VirtualChunkLocation,  // string URL - location of object
    pub offset: ChunkOffset,  // int - index of first byte within the object to read
    pub length: ChunkLength,  // int - number of contiguous bytes within the object to read
    pub checksum: Option<Checksum>,  // timestamp or etag - allows later verification of the contents
}
```

This abstraction is incredibly powerful! 
We can refer to data in any bucket in the cloud, public or private, in any region, on any provider. 
It also supports referring to a HTTP url, or a local filesystem path.

## Virtual chunks are dangerous

Unfortunately in the same way that pointers can be dangerous, virtual chunks carry some risks.

A virtual chunk in Icechunk is a one-way pointer.
Icechunk stores require authentication to fetch virtual chunks, but Icechunk alone doesn't have a permissions model beyond direct authenication to storage, so the owner of the referenced data doesn't know who is requesting to fetch their data or why, and are not given the chance to deny authenticated requests.
If an adversary could create an Icechunk store with permissions to access sensitive data, they could write a virtual chunk that pointed at the location of sensitive data, then use `IcechunkStore.get()` to fetch the bytes.

Worse, since Icechunk is a purely client-side library, any credentials used are available for inspection, meaning an attacker could re-use those credentials to manually fetch anything else those credentials allow access to.

Some specific scenarios we needed to protect against here included:

1) **Users inadvertently exposing private buckets via Arraylake virtual chunk access.** 
As allowing virtual chunk access entails allowing access to an entire bucket prefix, a novice user might conceivably grant overly-broad access via Arraylake to other users outside of their organization.

2) **Adversaries weaponising an Icechunk store to steal sensitive data via malicious virtual chunks.** 
If a sneaky someone says "here, load this Icechunk store", and the store contains a virtual chunk with location `file:///your-home-dir/bitcoin-wallet`, Icechunk will dutifully try to fetch the sensitive file.
The attacker still has to convince you to send them the bytes, but they could potentially socially engineer that too.
This is particularly a concern for anyone running Icechunk server-side, as one of your users could write a malicious store, then exfiltrate sensitive data (potentially using whatever permissions the server environment has) by using your service to "helpfully" send the data back to them!

## Icechunk (over)protects

The open-source Icechunk library nips nefarious byte-nabbing in the bud by defining the concept of a "Virtual Chunk Container" (VCC), which defines an allowed location for some set of virtual chunks in the store, and requiring that all virtual chunk containers be authorized explicitly at read-time.
This creates **two layers of authorization** - the repo writer has to set VCCs, and the repo reader has to authorize them explicitly at read time.

```{code-block} python
:caption: Opening an Icechunk repository containing virtual chunks requires explicit authorization of all storage locations, specified via "virtual chunk containers".

import icechunk as ic

# credentials to access some arbitrary S3 bucket
virtual_chunk_creds = ic.credentials.S3Credentials(
    access_key_id=...,
    secret_access_key=...,
)

# This prefix-crendential pair is the virtual chunk container (VCC).
# This particular VCC explicitly authorizes reading virtual chunks from a different, private s3 bucket
safe_vcc = {"s3://somebucket/prefix/": virtual_chunk_creds}

repo = ic.Repository.open(
    # open an icechunk repo stored in an anonymous-access s3 bucket, but containing virtual chunks referring to another bucket
    storage=ic.s3_storage(bucket="my-bucket", prefix="my-prefix", region="us-east-1", anon=True),
    authorize_virtual_chunk_access=safe_vcc,
)
```

This places the burden of security on the users reading the repository - regardless of what the untrustworthy repository creator wrote, for them to steal your bitcoin wallet, you have to have knowingly run code which explicitly states the locations to which you are authorizing access:

```python
repo = ic.Repository.open(
    ...,
    # Authorizes access to anything within the path `/your-home-dir`
    authorize_virtual_chunk_access={"file:///your-home-dir": None},
)
```

Similarly, to allow reading data from a private bucket using local AWS environment variables as credentials, you would have to pass

```python
repo = ic.Repository.open(
    ...,
    # Authorizes access to any object within `s3://your-orgs-secret-bucket`, using creds found in environment vars.
    authorize_virtual_chunk_access={"s3://my-company-bucket/": icechunk.S3Credentials(from_env=True)},
)
```

(Note that you can also use `None` to mean "default", which for private buckets will also use creds found in environment vars.
But we are [deprecating](https://github.com/earth-mover/icechunk/issues/2194) that behaviour.)

This is quite a lot of boilerplate just to read data, but it's explicit by design.
For open-source Icechunk to be safe to use without any additional layers on top, it's important that we make users explicitly authorize access to potentially-sensitive storage locations.
This step is where they show they understand what they are doing, and accept any risks.
Any tacit approval - i.e. any API more convenient and "auto-magical" than this - would lower security to dangerous levels.

## Users shouldn't have to worry

From a security perspective, this works, but the user experience is not great.
Users have to authorize access at read time, every single time, even for clearly-innocuous storage locations.

Even more annoyingly, repo readers have to know something about the contents of the repo (i.e. what virtual chunk containers it uses) _before_ they open the repo.
In practice this means opening it twice: once to fetch the config to read the virtual chunk containers, and once again after explicitly authorizing those containers.

```{code-block} python
:caption: Code snippet for opening an unfamiliar Icechunk store containing virtual chunks using just the raw Icechunk library. Requires a lot of boilerplate as well as prior knowledge of the dataset.

import icechunk as ic

storage = ic.s3_storage(...)

# fetches virtual chunk container information, incurring a roundtrip to object storage
config = ic.Repository.fetch_config(storage)
vccs = config.virtual_chunk_containers

# opens the icechunk repository properly, requiring a second roundtrip to object storage
repo = ic.Repository.open(
    storage,
    authorize_virtual_chunk_access={
        # user is forced to explicitly authorize read access to each virtual chunk container
        # Note that in this specific case the bucket is anonymous-access, so doesn't even require authorization for safe usage!
        vcc.url_prefix: icechunk.S3Credentials(anon=True) for vcc in vccs
    },
)
```

For an client-side open-source library, that's pretty much the best we can do - we can't restrict the allowed types of virtual chunks as there are legitimate uses for all of them, and we can't make the user experience much better without compromising on security.

Ideally though users merely reading a repo would never have to worry about any of this - they would just call `get_repo(<identifier>)` and authorization and security would be magically handled for them...

## Reticent to give references

Arraylake can do much better than bare Icechunk.
As a client-service architecture with a bucket- and user-account-level permissions model, Arraylake can act as a trusted intermediary, brokering credentials only to authenticated users who have the correct permissions to access specific storage locations.
Arraylake therefore has enough information to provide the desired magic `get_repo()` function that handles security for the user.

However, Arraylake also has to avoid being too helpful, and becoming an unwitting accomplice to one of the attacks described above.
Just to make things even harder, since Arraylake works on a bring-your-own-bucket paradigm, where all Icechunk data lives in the customer's storage, we can't trust the repo config object either, including its virtual chunk containers.

Originally, we punted on this tricky problem.
Our initial virtual chunks auth implementation restricted virtual chunks to only be used to refer to anonymous-access buckets, and always automatically authorized just those locations, since the contents of those buckets are already exposed to the public internet anyway.
But soon users started asking for virtual chunks referring to private buckets, and we also realized that the powerful indirection of virtual chunks might be useful for implementing [other features](https://www.earthmover.io/blog/filtered-subscriptions) in our platform.

## Defense in depth

We knew that forcing all repo readers to authorize at read time was untenably inconvenient.
But we also decided that, like raw Icechunk, in order to be secure the platform needed at least _two layers_ at which access had to be explicitly granted.
Anything less would be too easy for a user to misinterpret.

The repo config formed the first layer - any user with repo writer permissions can edit this config (and they must set the config before Icechunk will allow them to write the actual virtual chunk references into the repo), and so say "I'm happy for users reading this repo to attempt to fetch data from these locations".
But as repo readers can't trust the repo config in general, we still have to validate it behind-the-scenes everytime the virtual chunk container is ever about to be used.
Amongst other things, this validation screens for virtual chunks containing local filepaths, which is how we prevent the local bitcoin wallet theft scenario described above.

As a reminder, raw Icechunk's two layers of authorization are (1) the repo writer has to set VCCs, and (2) the repo reader has to authorize them explicitly at read time.
We want a similar level of security when using Icechunk with Arraylake, but as read-time auth was ruled out for usability, for the second layer we had to invent a new concept - a "virtual chunk access policy".
This is a Arraylake-only flag set on a customer's storage bucket config, which effectively states "I am happy for other users to potentially fetch data from this specific prefix of this specific bucket".
The flag can be scoped to allow access either to anyone in arraylake, or to only members of the user's org. 

Virtual chunk access policies can only be set by org admins - this is how we protect against the "novice user accidentally grants too many permissions" scenario.

```{figure} images/cover.jpg
:alt: A muscular bouncer guarding the door to a disco club full of dancing chunks and scientists. The bouncer's t-shirt reads 'Access Policy'.
:width: 50%
:align: center

Virtual chunk access policies are the power-user feature that keeps anyone else from exfiltrating your chunks — only org admins get to decide which data can be reached from outside.
```

## Keeping it snappy

That's quite a lot of checks to perform to authorize at `client.get_repo` time.
This also needs to be fast, as `client.get_repo` is called anytime anyone fetches any repo!

As there are 3 physical locations involved (user compute, icechunk object storage, and arraylake server), making this fast mostly boils down to minimizing the number of sequential network hops.
We refactored such that everything necessary is now done just one API call to the Arraylake server, meaning that `get_repo` now makes as few network hops as this architecture allows, looking something like this overall:

```{mermaid}
sequenceDiagram
    participant User as Client User
    participant Client as Arraylake Client
    participant AL as Arraylake Service
    participant S3 as Icechunk repo in S3

    User->>Client: get_repo(repo_id)
    Client->>AL: call dedicated `get_repo` endpoint

    par Concurrent calls
            AL->>AL: Fetch credentials for repo bucket
          AL->>S3: IcechunkRepository.fetch_config_async(storage)
          S3-->>AL: Return config (with VCCs)
          AL->>AL: Inspect config for VCCs
      and
          AL->>AL: Look up relevant VCAPs
      end

      AL->>AL: Match VCCs to VCAPs
      AL->>AL: Fetch credentials for all virtual buckets
      AL-->>Client: Return all credentials

    Client->>S3: IcechunkRepository.open(storage, virtual_chunk_credentials=...)
    S3-->>Client: Repo object
    Client-->>User: Repo ready for use
```

Network flow for a `client.get_repo` call in Arraylake. Behind that single call, the Arraylake service fetches the Icechunk repo config and looks up the relevant Virtual Chunk Access Policies (VCAPs) concurrently, validates the config's Virtual Chunk Containers against those policies, and returns all required credentials in one response — so the client can open the repo without a second round-trip.

This design keeps as much validation as possible happening on the Arraylake server, minimizing overall time taken.

## Magic method

The resulting user experience makes this look simple.
As all the configuration and authorization is done in advance by the repo author (and an org admin), then regardless of the contents of the repo, the user can always simply call `get_repo`:

```{code-block} python
:caption: Code snippet for opening an Icechunk store containing virtual chunks using Arraylake. Boilerplate is minimized, and no prior knowledge of the dataset is required, as the correct virtual chunk containers are automatically detected and safely authorized.

import arraylake as al

# user logs in to their Arraylake account to verify their identity (login can also be done outside of Python)
client = al.Client().login()

# asserts that the user has authority to access all the data, including at any virtual chunk locations,
# then fetches all credentials necessary for access
repo = client.get_repo("some-org/some-repo")
```

This either succeeds, or fails with a clear error explaining what still needs to be authorized and by whom.

## Myriad uses for the general case

This design supports the fully general case: one authorized bucket containing references to any number of other authorized buckets.
Once in place, we realized this generality had several uses, both anticipated and unanticipated:

- **Private repos referencing other private repos** (the intended use case).
- [**Filtered subscriptions**](https://www.earthmover.io/blog/filtered-subscriptions), where a user's repo contains just manifests, referring back to a subset of the provider's full dataset.
- **Marketplace listings containing virtual chunks** (e.g. our [GOES-16 virtual store](https://www.earthmover.io/blog/virtual-zarr)). Note that a filtered subscription to such a listing requires two virtual chunk containers!
- **Rolling embargo**, where the lowest-latency paywalled data is stored in a private bucket, along with virtual references to the higher-latency public data in a different location. This is what we do for [Earthmover's copy of ERA5](https://www.earthmover.io/blog/low-latency-era5-icechunk-marketplace#commercial-sla-and-free-options), where we placed the public data in a bucket provided via AWS Open Data Program to minimize our storage costs.
- **Vending [generic bucket credentials](https://docs.earthmover.io/reference/client#get_obstore_for_bucket)** for other purposes, such as listing the contents of a user's bucket.

## OSS commitment

Our solution here serves both Icechunk-only and Arraylake userbases well, illustrating our commitment to supporting open-source Icechunk users as well as paying customers.

## Conclusion

Hopefully this helps you understand how much thought went into this "magical" feature, why Icechunk & Arraylake together can solve problems that Icechunk alone cannot, and the interesting use cases that can be supported by this system.
