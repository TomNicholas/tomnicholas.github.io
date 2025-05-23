# -- Project information -----------------------------------------------------
import sys

sys.path.append("scripts")
sys.path.append(".")
from social_media import add_social_media_js, SocialPost

project = "Tom Nicholas"
copyright = "2025, Tom Nicholas"
author = "Tom Nicholas"

extensions = [
    "myst_nb",
    "ablog",
    "sphinx_design",
    "sphinx_copybutton",
    "sphinx_examples",
    "sphinxext.opengraph",
    "sphinxext.rediraffe",
]

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "*import_posts*",
    "**/pandoc_ipynb/inputs/*",
    ".nox/*",
    "README.md",
    "**/.ipynb_checkpoints/*",
]

# -- HTML output -------------------------------------------------

html_theme = "pydata_sphinx_theme"

# html_theme_options = {
#     "search_bar_text": "Search this site...",
#     "analytics": {"google_analytics_id": "UA-88310237-1"},
#     "icon_links": [
#         {
#             "name": "GitHub",
#             "url": "https://github.com/TomNicholas/",
#             "icon": "fa-brands fa-github",
#         },
#         {
#             "name": "Twitter",
#             "url": "https://twitter.com/choldgraf",
#             "icon": "fa-brands fa-twitter",
#         },
#         {
#             "name": "Mastodon",
#             "url": "https://hachyderm.io/@choldgraf",
#             "icon": "fa-brands fa-mastodon",
#             "attributes": {"rel": "me"},
#         },
#         {
#             "name": "Blog RSS feed",
#             "url": "https://chrisholdgraf.com/blog/atom.xml",
#             "icon": "fa-solid fa-rss",
#         },
#     ],
# }

html_favicon = "_static/profile-color-circle-small.png"
html_title = "Tom Nicholas"
html_static_path = ["_static"]
html_extra_path = ["feed.xml"]
html_sidebars = {
    "index": ["hello.html"],
    "about": ["hello.html"],
    "publications": ["hello.html"],
    "projects": ["hello.html"],
    "talks": ["hello.html"],
    "blog": ["ablog/categories.html", "ablog/tagcloud.html", "ablog/archives.html"],
    "blog/**": ["ablog/postcard.html", "ablog/recentposts.html", "ablog/archives.html"],
}

# OpenGraph config
ogp_site_url = "https://tom-nicholas.com"
ogp_social_cards = {
    "line_color": "#4078c0",
    "image": "_static/profile-color-circle.png",
}


rediraffe_redirects = {
    "rust-governance.md": "blog/2018/rust_governance.md",
}
# Update the posts/* section of the rediraffe redirects to find all files
redirect_folders = {
    "posts": "blog",
}
from pathlib import Path

for old, new in redirect_folders.items():
    for newpath in Path(new).rglob("**/*"):
        if newpath.suffix in [".ipynb", ".md"] and "ipynb_checkpoints" not in str(
            newpath
        ):
            oldpath = str(newpath).replace("blog/", "posts/", 1)
            # Skip pandoc because for some reason it's broken
            if "pandoc" not in str(newpath):
                rediraffe_redirects[oldpath] = str(newpath)

# -- ABlog ---------------------------------------------------

blog_baseurl = "https://tom-nicholas.com"
blog_title = "Tom Nicholas"
blog_path = "blog"
blog_post_pattern = "blog/*/*"
blog_feed_fulltext = True
blog_feed_subtitle = "Open communities, open science, communication, and data."
fontawesome_included = True
post_redirect_refresh = 1
post_auto_image = 1
post_auto_excerpt = 2

# -- MyST and MyST-NB ---------------------------------------------------

# MyST
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "html_image",
    "strikethrough",
]

# MyST-NB
# Don't execute anything by default because many old posts don't execute anymore
# and this slows down build times.
# Instead if I want something to execute, manually set it in the post's metadata.
nb_execution_mode = "off"


def setup(app):
    app.add_directive("socialpost", SocialPost)
    app.connect("html-page-context", add_social_media_js)
    app.add_css_file("custom.css")
