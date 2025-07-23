---
date: "2021-06-29"
title: "Science needs a social network for sharing big data"
description: |
  Imagine being able to visit one website, search for any scientific dataset from any institution in the world, preview it, then stream the data out at high speed, in the format you prefer. We have the technology - here's what we should build.
tags:
- open-science
- frost
kernelspec:
  name: python3
  display_name: 'Python 3'
---

## Science needs a social network for sharing big data

Tom Nicholas, 18th Jan 2025

**Context:** This post was originally published just as a [HackMD doc](https://hackmd.io/@TomNicholas/H1KzoYrPJe). 
On the back of that post I gave to give a talk & hosted a discussion about this at the [Pangeo Showcase](https://discourse.pangeo.io/t/pangeo-showcase-frost-federated-registry-of-scientific-things-feb-12-2025/4861) ([recording here](https://youtu.be/GZvJ0H89G0A)). If you are interested in helping build the thing please [fill out this form](https://forms.gle/t3bE3xDRijKntBa88)!

**tl;dr: Science is missing a crucial data sharing network. We have the technology - here's what we should build.**

### Data sharing sucks

Sharing large scientific datasets is a pain in the ass, and finding them is even worse. There are myriad portals and tools and APIs and bucket URLs and crappy catalogs that are split across arbitrary geographic and institutional lines, which are often slow or have gone down, or will only give you part of the data or in a suboptimal pattern or in a format you've never heard of. Crucial datasets aren't easy to find by Googling, and because you don't know where they live (or even if what you want exists anywhere) you don't know which institutions' catalog to comb through. That's if anyone even bothered to put the data online, rather than just fobbing you off with "available upon request" and a gesture towards an out-of-date email address.

Imagine instead simply being able to visit one website, search for any scientific dataset from any institution in the world, preview it, then stream the data out at high speed, in the format you prefer. A true "scientific data commons".

### Scientists love GitHub

For sharing code, this commons already exists: it's called [GitHub](https://github.com/). "Just put it on GitHub" has become the "Open Science" community’s mantra. As well as being the de facto way to share code underlying individual scientific papers, GitHub has enabled open collaboration on impactful scientific software projects (including true inter-disciplinary collaboration between otherwise unrelated fields). Despite being privately-owned, we regularly champion its use under the "Open science” banner, as it is an enormous boon for open science worldwide.

### GitHub is a centralized social network

GitHub is a version-controlled code hosting site with easy local backups, but it's also arguably a social network - upon launch in 2008 their strapline was ["Social Code Hosting"](https://web.archive.org/web/20080828150139/http://github.com/). You can like, comment, subscribe, and follow users, repositories, and organisations.

Note that whilst the source code they host is distributed (via backing up by everyone that clones a repository) their social network is completely centralized. All the issues, comments, followers etc. live in GitHub's servers, are not automatically backed up by any other organisation, and are only acessible through the GitHub web platform or official API.

### GitHub for data?

Most modern scientific works are really composed of up to 3 artifacts: the manuscript, data, and code. Science is currently often done by disseminating the manuscript alone via a journal, but efficient sharing of all three is necessary to have any hope of reproducibility of scientific results.

Manuscript sharing networks exist but are hamstrung by publicly-funded content being brutally paywalled by parasitic for-profit organisations (otherwise known as "Scientific Publishers"). But that shitshow deserves discussion in a separate post.

GitHub is designed specifically for sharing code - using it to share data is really misusing the platform. The fact that people do still share (small) data this way regularly shows there is an unfullfilled need.

What we still need is a _global social network for sharing big scientific datasets_, or a "GitHub for data".

### Goal of “FAIR” scientific data

To imagine something new, let's keep in mind the oft-cited (but rarely achieved) ["FAIR data principles"](https://www.go-fair.org/fair-principles/). These state that scientific data assets should be _Findable_, _Accessible_, _Interoperable_, and _Reproducible_.

### What would the ideal data-sharing service look like?

The ideal data-sharing service would have a number of important properties:

1. **Unified**
  
    A catalog of all scientific data in the world should have global search and connections across all projects, regardless of instutition or academic subfield.
  
    This feature of GitHub is what allows true interdisciplinary collaboration within [foundational software projects](https://www.statnews.com/sponsor/2024/11/26/new-report-highlights-the-scientific-impact-of-open-source-software/). Any other approach causes fragmentation and artifical boundaries between hazily-defined fields of science, and wastes effort through re-inventing unnecessarily bespoke solutions for generic data engineering problems.

2. **Open to anyone**

    Anyone should be able to create a public catalog entry for their dataset on the platform. 
    
    This doesn't mean it necessarily has to be free to upload data to the catalog, but it should be possible for anyone who can pay a reasonable hosting fee to do so (like the commercial cloud, dropbox, or website hosting). This means that no institutional login should be required, no requirement for a `.edu` email address, no requirement to be in a specific country, etc.

3. **Free to browse**

    Anyone should be able to use the platform to browse and discover public datasets, without them being paywalled.
  
    Downloading the actual data doesn't need to be free (and shouldn't be - bandwidth for big data is expensive so downloading it unnecessarily should be disincentivised), but viewing enough metadata to decide if you want to get the actual contents should be free. This is especially important for crucial public data such as real-time satellite imagery of wildfires - which infuriatingly is not necessarily findable [even by experts](https://bsky.app/profile/briannaritapagan.bsky.social/post/3lfpp3nnalc2m).

4. **Scalable to massive datasets**

    The platform should be able to handle the biggest datasets in science.

    In many fields the largest datasets are some of the most important. That's especially true in physical sciences such as climate science, meteorology, neuroscience, and genomics. For example [ERA5](https://cloud.google.com/storage/docs/public-datasets/era5) is effectively our best guess as to the Earth's weather over the last 80 years, and as such it's the starting point for a huge amount of climate / meteorology / hazard & energy forecasting research. Unfortunately it's about 5 _Peta_-Bytes in size, so could only be hosted by a system that can handle arbitrarily large datasets.

    As the [Pangeo project](https://www.pangeo.io/) in big data geoscience has shown, this can't be an afterthought, because sharing big data requires fundamentally different architectures (i.e. [cloud-native data repositories](https://medium.com/pangeo/step-by-step-guide-to-building-a-big-data-portal-e262af1c2977)). Luckily placing data in S3-compatible public-facing cloud storage also solves the problem of ensuring open accessibility and scalable computing resources for data analysis. Agencies like NASA are already catching on to this whole cloud idea, but not to the full potential that this infrastructure technology enables.

5. **Globally available**

    The same data should be available to anyone in the world.
    
    Cloud storage allows large datasets to be available to anyone within a [cloud region](https://www.cloudinfrastructuremap.com/), but the technical challenge is guarantee that copies of data stored in different cloud regions are consistent with one another. One approach is to do this at the level of the storage itself (e.g. [Tigris](https://docs.earthmover.io/integrations/storage/tigris)), but another is to have automatic methods of [guaranteeing consistency](https://discourse.pangeo.io/t/conflict-free-replicated-zarr/4261) between copies.

6. **Common data models**

    The vast majority of scientific data can be represented via one of 2 or 3 common data models. Particularly Tabular data (rows and columns, think spreadsheets), and Multi-dimensional Array (or "Tensor") data (grids of values, think latitude-longitude). Many fields of physical science are naturally described via Multi-dimensional Arrays, because the universe we live in is 4-dimensional. For example climate/weather simulations, microscope imagery, but also more abstract dimensions such as DNA base pairs in genomics.

    Recognising this (still extremely general) structure allows for plugging in to all the existing tools in the world designed to process, analyse, and visualize data. For example, adopting common tabular data formats allows the use of off-the-shelf [data processing technologies](https://howqueryengineswork.com/01-what-is-a-query-engine.html), so is really required to achieve the FAIR principle of [Interoperability](https://en.wikipedia.org/wiki/FAIR_data#:~:text=no%20longer%20available-,Interoperable,-The%20data%20usually). This idea is so useful that platforms for managing Tabular data specifically for e-commerce businesses are themselves worth [billions of dollars](https://en.wikipedia.org/wiki/Snowflake_Inc.).
    
    In the world of Tabular data [common models](https://parquet.apache.org/) are well-established, and in the world of array data the [Zarr model](https://zarr.dev/) is general enough to abstract over many existing scientific array data formats, often [without even altering](https://github.com/zarr-developers/VirtualiZarr/issues/218) the original data format.

7. **Version-controlled**
  
    The key value-add of git is the way it tracks every change to your source code. A robust version control system is crucial to have any hope of reproducibility, and that's true also for data. Luckily open-source systems such as [Apache Iceberg](https://iceberg.apache.org/) (Tabular) and [Earthmover's recent release](https://earthmover.io/blog/icechunk/) of [Icechunk](https://icechunk.io/) (Arrays) both allow users to rollback to old versions of data to reproduce results.
    
    Without this crucial building block previous attempts to create an updateable version-controlled catalog have often become mired in all the complexity needed to make up for the lack of intrinsically version-controlled data models.

8. **Data ownership**

    Using the platform should not require you to relinquish legal or technical control over your data. (This is how the the scientific publishing industry really screwed us all over.) 
  
    This requires openly-licensed data formats (which Iceberg and Icechunk both are), as well as the option for data to reside on your own infrastructure. The platform then merely catalogs references to data that actually still lives on other systems. The cloud works well for this - data can live in one bucket but be referenced from anywhere, and data consumers don't necessarily have to know the difference.

9. **Citable dependency networks**

    Datasets in the catalog should be citable, and it should be possible to see which datasets are derived from which others.
    
    The [DOI system](https://www.doi.org/) makes this technically pretty straightforward, but it's sociologically crucial for scientists to be able gain career credit for non-manuscript contributions (such as widely-used datasets and open-source code). The fact this kind of credit currently is both difficult to obtain and undervalued by tenure committees is a major source of misaligned career incentives in science.

10. **Subscribable**

    Many scientific datasets are not just derived from upstream data, they should actually be updated every time the upstream data is updated.
    
    A [Publisher-Subscriber model](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern) (think RSS blog feeds) would allow recomputing derived data upon updates to upstream data. For example, imagine recomputing a metric of wildfire risk whenever new satellite imagery becomes available.

11. **Social**

    Science progresses through debate, and so the data catalog should include spaces for debate.

    This could take the form of public comments, or GitHub-like issue raising. Version-control also theoretically allows public submission of data corrections (i.e. Pull Requests that update data). Whilst this brings up the spectre of Moderation, at least moderation here would be federated in that each data project's owners would have the power and incentive to moderate their own space. This approach scales with the number of datasets, and seems to work relatively well for GitHub.
    
    Scientists also have professional social networks, and users being able to follow specific scientists, datasets, or data providers would simply formalize and streamline data-sharing networks which already exist informally.

12. **Sustainably-fundable**

    Something of this scope would cost _someone_ [millions of dollars](https://lu.is/2025/01/social-network-costs/) every year to build and maintain. Ideally the project would generate this funding itself.
    
    There's no way around that figure - it requires hosting infrastructure (servers) and staff (expensive software engineers) - decentralizing the project would just split the same cost among more institutions. If you want it to actually work anywhere near as well as GitHub it would cost even more than that, to pay for expensive industry-grade UX designers and site reliability engineers and so on.
    
    The funding mechanism also needs to scale up proportionally to the size of the user base - and it's important that the project is actually incentivised to provide a good service. GitHub handles these problems by being a private company offering a useful service to businesses, with a free tier for public repositories but a paid tier for private ones.

13. **Right to Exit**

    It's important that a global network of scientific knowledge is not beholden to any one institution or company. However it would be hard to build the unified search and dependency/social network features, use common data models, and get economies of scale without some degree of centralization.

    This is a similar problem to social media: users want to be on the same network, accessed via a platform with a high-quality interface. But they also want to be able to leave without losing their personal/professional network if there is an ["Elon Musk Event"](https://bsky.app/profile/joshuajfriedman.com/post/3l6opxixk2c2d) threatening trust in the platform. For social networks this ["Right of Exit"](https://www.eff.org/deeplinks/2023/04/platforms-decay-lets-put-users-first#:~:text=Principle%202%3A%20Right%20of%20Exit%3A%20Treating%20Bad%20Platforms%20As%20Damage%20and%20Routing%20Around%20Them) is harder to achieve than simply having multiple platform vendors or open data formats, because an alternative service doesn't automatically come with [your follower network](https://www.eff.org/deeplinks/2022/09/how-ditch-facebook-without-losing-your-friends-or-family-customers-or-communities) on it.

    One idea for avoiding being locked-in to a social network is _decentralization_. Mastodon and Bluesky both _claim_ to be decentralized in a way that safeguards your Right to Exit. Their solution is to **separate the network from the platform** used to interact with the network, and make the network layer an open protocol. Think of email: while no-one owns the "email network", there are many platforms you can use to send and receive emails (Outlook, GMail, Thunderbird etc.), and you can switch between them. This is possible because there is a public email protocol which every email provider uses to send messages between them.
    
    Decentralizing an entire social network turns out to be [incredibly challenging](https://dustycloud.org/blog/how-decentralized-is-bluesky/#:~:text=ATProto%27s%20portable%20identity%20challenges). A more tractable idea that could still help alleviate lock-in would be a decentralized catalog protocol. That would at least allow multiple institutions / other companies to host their own data catalogs, and have them integrate fully, with shared global search and dependency networks. To be more concrete, imagine NASA hosts a catalog of Icechunk repositories on the platform `IceHub`, whilst NOAA hosts some others on a different platform `IceBucket`. A shared decentralized network using a public protocol would allow the NASA data repositories to subscribe to updates from the NOAA datasets, with bi-directional linking, despite being on different platforms. It would also allow either platform to easily provide a search index that covers all public datasets on both platforms. One naive way to do this is would be to simply have the full public network be stored on both platform's servers (somewhat like [NNTP](https://en.wikipedia.org/wiki/Network_News_Transfer_Protocol)), which also means that if `IceHub` disappeared then `IceBucket` could expand to serve the same institutions without losing the record of the dataset dependency network.
    
    A major high-quality platform can still exist - this just allows other platforms to potentially also exist, whilst being connected to the same network. Such decentralization combined with open data formats and data ownership should allow the development of such a high-quality platform whilst minimizing risk of data or network lock-in. It would also aid the switch to whatever future scientific infrastructure we realise we need _after_ this platform, assuming we're all still around by then.
    
    _To be clear, of all the requirements, this last one is the only one that I'm not actually sure is even **technically** possible. It would be [awesome](https://medium.com/@npfoss/the-case-for-a-decentralized-social-network-2683b727abf5) though, so I would love it if someone who knows more than I about networking protocols could weigh in. [Here's a place for brainstorming ideas](https://github.com/TomNicholas/FROST)._

### Surely this exists already?

Whilst various initiatives (federal, non-profit, and for-profit) aim to solve some of these problems, as far as I am aware nothing currently exists which meets all of the criteria above simultaneously. Let's briefly discuss where major existing efforts fall short.

**Not even trying** - the vast majority of scientific data is only available "upon request", which is to say, not openly available at all. Given that this data was created with public money, and the public would benefit from it being openly accessible, this is unacceptable.

**Rolling-their-own** catalogs and data portals is currently most large institutions' approach (e.g. [[1]](https://data.nasa.gov/browse) [[2]](https://cmr.earthdata.nasa.gov/search/) [[3]](https://data.usgs.gov/datacatalog/) [[4]](https://cds.climate.copernicus.eu/) [[5]](https://catalog.leap.columbia.edu/) [[6]](https://www.sentinel-hub.com/explore/data/)), if they bother with a unified data catalog at all. This leads to massive waste through duplication of effort and difficulty finding relevant data outside of that one institution, only to end up with a mess of services which don't generalize, interoperate, or even necessarily work very well. These existing services also are not open to anyone - they very much care [who you are](https://www.ecmwf.int/en/forecasts/accessing-forecasts) - which limits the practice of data-driven science to a [subset of society](https://www.experimental-history.com/p/an-invitation-to-a-secret-society). Worse, many institutions such as universities and national labs actively make it _harder_ to access data instead of easier, by requiring strict affiliation and access controls to be permitted behind the walls of their "data fortress", then making it very hard to free the data even once you have access.

[**STAC**](https://stacspec.org/en), which stands for Spatio-Temporal Asset Catalog, is an open specification providing a common structure for describing and cataloging geospatial datasets. STAC is extremely cool, but it isn't quite what we need. Firstly, the data model is not general enough - it's intimately tied to [geospatial-specific concepts](https://geojson.org/). There is plenty of scientific data that is multidimensional arrays but nothing to do with the earth's surface, e.g. [statistical genetics data](https://sgkit-dev.github.io/sgkit/latest/getting_started.html#data-structures) and [microscope imaging data](https://github.com/ome/ome-zarr-py). Secondly, because STAC's core is a static catalog and API specification, not a network protocol, it's not designed to faciliate dynamic updates or global connectivity. (This is different to STAC's idea of a ["Dynamic Catalog"](https://stacspec.org/en/about/stac-spec/#:~:text=of%20common%20metadata.-,Dynamic%20and%20Static%20Catalogs,-The%20final%20bit), which is better understood as a static catalog created on-demand.) Some groups have built tooling on top to provide a [unified STAC catalog](https://stacindex.org/catalogs), a [searchable index](https://discover.maap-project.org/) and [publish update notifications](https://github.com/Element84/earth-search?tab=readme-ov-file#sns-notifications-of-items), but they must step outside the STAC specification to do so and hence lose some of the decentralization. Nevertheless this is all great inspiration, and a general cataloging protocol should play nicely with STAC in an extensible way, as the core spec is a perfect example of the domain-specific metadata conventions that each field of science should organize amongst themselves.

[**Intake**](https://github.com/intake/intake) is another open-source data catalog project from within the scientific python ecosystem. An Intake Catalog is in theory a little bit like a STAC catalog, but more general. Unfortunately Intake also tries to solve several other problems at the same time, including data loading, transformation, and processing. The result is that the [catalog definitions](https://github.com/intake/intake/blob/fa82a972164bfebe4d9efb4e72878510038e7691/docs/source/catalog.rst) are python-specific, and hence not interoperable.

[**Zenodo**](https://zenodo.org/) and [**Dataverse**](https://dataverse.org/) are science-oriented hosting services. Whilst great initiatives, they aren't designed to share big data or to exploit common scientific data models. For example Zenodo has a max dataset size of 50GB, whilst crucial climate science datasets can be many PetaBytes in size - at least 5 orders of magnitude larger! A service which doesn't take advantage of the fact that the vast majority of scientific data is either multidimensional arrays or tabular (i.e. they treat all data as unstructured) from a user perspective is not really that different from just putting raw binary files into GitHub - i.e. the repository doesn't understand that your data has any useful common structure. The funding model of these services also appears to be entirely based on public grants. (I must say Dataverse is pretty impressive, and perhaps the closest existing design I've seen to being capable of hitting all the technical requirements on this list.)

[**GitHub**](https://github.com/) being mis-used as a file sharing service does fulfil several of these properties, including being sustainably-funded. But again it's not Scalable nor does it use Common Data Models, and it can't really be made so (because GitHub and git itself were designed for something completely different: handling small text files containing source code). It's also not decentralized - whilst [GitHub's package dependency graph](https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/about-the-dependency-graph) is publicly available, it arguably does not fulfil the "Credible Exit" criteria according to BlueSky's definition, because you cannot simply switch over to another provider like GitLab whilst retaining your network connections.

[**Wikipedia**](https://www.wikipedia.org/) is another existing example of a commons, a _knowledge commons_. It is fully open-source, unified, open, federated, and sustainably-funded. It also hosts data through [WikiData](https://www.wikidata.org/wiki/Wikidata:Main_Page), so could we just put our scientific data there? Unfortunately whilst the size of the work to create and maintain Wikipedia is incredible, the actual amount of data stored is smaller than you might think. Once compressed, the size of all the English text on Wikipedia is a miniscule [24 GB!](https://en.wikipedia.org/wiki/Wikipedia:Size_of_Wikipedia#:~:text=The%20total%20number%20of%20pages,about%2024.05%20GB%20without%20media.) Even downloading all the images and so on only requires [about 25TB](https://meta.m.wikimedia.org/wiki/Mirroring_Wikimedia_project_XML_dumps#Space) - that fits on one big external hard drive. Again this is not the required scale of data hosting, which would require a completely different architecture (i.e. a cloud-native one). Also note that the majority of funding comes from [individual public donations](https://en.wikipedia.org/wiki/Wikimedia_Foundation#:~:text=The%20foundation%20finances%20itself%20mainly%20through%20millions%20of%20small%20donations%20from%20readers%20and%20editors%2C%20collected%20through%20email%20campaigns%20and%20annual%20fundraising%20banners%20placed%20on%20Wikipedia%20and%20its%20sister%20projects.) (I donate - you should too). That's awesome, but doesn't seem like an approach that would work for a scientific data platform invisible to most of the public.

[**Snowflake**](https://www.snowflake.com/en/) is a commercial product: a proprietary cloud data platform that's widely used by the private sector. It's extremely scalable as it's designed for big (business) data, and sustainably-funded in the sense of being very profitable. However it doesn't recognise anything other than Tabular data, because almost all business data is Tabular. A platform set up to manage companies' private data also has little need for a public global data catalog, as unlike scientists, businesses don't tend to openly share data with one another.

[**Hugging Face Hub**](https://huggingface.co/) is another platform from another private company, but for sharing Machine Learning training datasets and model weights. It works well for that community, but again it is not truly Scalable (because your data has to be uploaded to [their storage](https://huggingface.co/docs/hub/en/storage-limits#sharing-large-datasets-on-the-hub)) nor does it use a Common Data Model (though [it could](https://github.com/zarr-developers/VirtualiZarr/issues/367)), and is ML-specific. [**DagsHub**](https://dagshub.com/) is very similar, except that it lets you connect your own storage bucket, and has version-control. However, the version-control system assumes unstructured data. It's also worth noting that the stupid amounts of money being poured into the ML sphere incentivises the founding of multiple companies trying to provide data-sharing services, whereas in science there are far fewer, even though there is no fundamental difference between ML "tensor" model weights and scientific multidimensional array data.

[**Source Cooperative**](https://source.coop/) is a non-profit data-sharing utility that basically wraps cloud storage buckets provided by the [AWS Open data program](https://aws.amazon.com/opendata/open-data-sponsorship-program/), so is Free to Browse and Scalable to large datasets. In theory Source could evolve to meet many of the criteria above, but note that one big missing requirement that would be hard to add later is Common Data Models - Source is essentially just a catalog of buckets, each full of potentially inconsistent and unrelated objects. For now it's still in beta, so has few features, is effectively invite-only, and does not yet have a clear sustainable funding mechanism in place.

[**Google Earth Engine**](https://earthengine.google.com/) is scalable, and does understand the raster data model (2D arrays of geospatial imagery). However, it's geoscience-specific, doesn't respect Data Ownership and is completely Centralized - as all the data lives on Google machines. Crucially it's also not sustainably-funded - Google runs it at a loss, and have only recently started trying to monetize it. Nevertheless Earth Engine is widely used, meaning that an alarming number of environmental non-profits completely depend on the charity of a big corporation, who have no obvious reason beyond PR to keep funding the service for free, and could [pull the plug](https://www.theverge.com/23778253/google-reader-death-2013-rss-social) at literally any time.

_EDIT: Every time I show someone new this post they suggest another hosting service that I hadn't heard of. So far none of them meet all the 13 criteria above, and most of them fall down on Scalability or Common data models._

### Conclusion

There's a major missing link in the way the world shares scientific data. Until we build it we cannot reasonably expect results from data-intensive science to be truly Findable, Accessible, Interoperable, or Reproducible. Though still a major effort, luckily cloud computing and recent advances in key open-source software libraries bring the idea within reach.
