#!/usr/bin/env python3
import argparse
import json
import sys
from yaml import safe_load
from pathlib import Path
import pandas as pd
from feedgen.feed import FeedGenerator
import unist as u

DEFAULTS = {"number": 10}

root = Path(__file__).parent.parent

# Aggregate all posts from the markdown and ipynb files
posts = []
for ifile in root.rglob("blog/**/*.md"):
    if "drafts" in str(ifile):
        continue

    text = ifile.read_text()
    try:
        _, meta, content = text.split("---", 2)
    except Exception:
        print(f"Skipping file with error: {ifile}", file=sys.stderr)
        continue

    # Load in YAML metadata
    meta = safe_load(meta)
    meta["path"] = ifile.relative_to(root).with_suffix("")
    if "title" not in meta:
        lines = text.splitlines()
        for ii in lines:
            if ii.strip().startswith("#"):
                meta["title"] = ii.replace("#", "").strip()
                break

    # Summarize content
    skip_lines = ["#", "--", "%", "++"]
    content = "\n".join(ii for ii in content.splitlines() if not any(ii.startswith(char) for char in skip_lines))
    N_WORDS = 50
    words = " ".join(content.split(" ")[:N_WORDS])
    if not "author" in meta or not meta["author"]:
        meta["author"] = "Tom Nicholas"
    meta["content"] = meta.get("description", words)
    posts.append(meta)

posts = pd.DataFrame(posts)
posts["date"] = pd.to_datetime(posts["date"]).dt.tz_localize("US/Eastern")
posts = posts.dropna(subset=["date"])
posts = posts.sort_values("date", ascending=False)

# Generate an RSS feed
fg = FeedGenerator()
fg.id("http://tom-nicholas.com")
fg.title("Tom Nicholas' blog")
fg.author({"name": "Tom Nicholas", "email": "tomnicholas1@gmail.com"})
fg.link(href="http://tom-nicholas.com", rel="alternate")
fg.logo("http://tom-nicholas.com/_static/profile.jpg")
fg.subtitle("Tom's personal blog!")
fg.link(href="http://tom-nicholas.com/rss.xml", rel="self")
fg.language("en")

# Add all my posts to it
for ix, irow in posts.iterrows():
    fe = fg.add_entry()
    fe.id(f"http://tom-nicholas.com/{irow['path']}")
    fe.published(irow["date"])
    fe.title(irow["title"])
    fe.link(href=f"http://tom-nicholas.com/{irow['path']}")
    fe.content(content=irow["content"])

# Write an RSS feed with latest posts
fg.atom_file(root / "atom.xml", pretty=True)
fg.rss_file(root / "rss.xml", pretty=True)

plugin = {
    "name": "Blog Post list",
    "directives": [
        {
            "name": "postlist",
            "doc": "An example directive for showing a nice random image at a custom size.",
            "alias": ["bloglist"],
            "arg": {},
            "options": {
                "number": {
                    "type": "int",
                    "doc": "The number of posts to include",
                }
            },
        }
    ],
}


def thumbnail(irow) -> list[dict[str, str]]:
    return [
        {
            "type": "image",
            "url": irow['thumbnail'],
        }
    ]


children = []
for ix, irow in posts.iterrows():
    title = [
        {
            "type": "cardTitle",
            "children": [u.text(irow["title"])]
        },
    ]
    text = [
        {
            "type": "paragraph",
            "children": [u.text(irow['content'])]
        },
        {
            "type": "footer",
            "children": [
            u.strong([u.text("Date: ")]), u.text(f"{irow['date']:%B %d, %Y} | "),
            u.strong([u.text("Author: ")]), u.text(f"{irow['author']} | "),
            u.strong([u.text("Tags: ")]), u.text(f"{", ".join(irow['tags'])}"),
            ]
        },
    ]
    card_contents = (title + thumbnail(irow) + text) if "thumbnail" in irow else (title + text)
    children.append(
        {
          "type": "card",
          "url": f"/{irow['path'].with_suffix('')}",
          "children": card_contents
        }
    )


def declare_result(content):
    """Declare result as JSON to stdout

    :param content: content to declare as the result
    """

    # Format result and write to stdout
    json.dump(content, sys.stdout, indent=2)
    # Successfully exit
    raise SystemExit(0)


def run_directive(name, data):
    """Execute a directive with the given name and data

    :param name: name of the directive to run
    :param data: data of the directive to run
    """
    assert name == "postlist"
    opts = data["node"].get("options", {})
    number = int(opts.get("number", DEFAULTS["number"]))
    output = children[:number]
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--role")
    group.add_argument("--directive")
    group.add_argument("--transform")
    args = parser.parse_args()

    if args.directive:
        data = json.load(sys.stdin)
        declare_result(run_directive(args.directive, data))
    elif args.transform:
        raise NotImplementedError
    elif args.role:
        raise NotImplementedError
    else:
        declare_result(plugin)
