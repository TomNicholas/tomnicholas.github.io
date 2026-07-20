#!/usr/bin/env bash
# Import a Slidev talk into this site as a browser-viewable static build plus
# a downloadable PDF, under slides/<slug>/.
#
# Usage: scripts/import-slidev-talk.sh <path-to-slidev-md> <slug>
#
#   scripts/import-slidev-talk.sh \
#       ../design/presentations/virtual-chunks-esip/virtual-chunks-esip.md \
#       virtual-chunks-esip
#
# The build runs from inside the talk's own repo so that relative theme paths
# and public/ assets resolve. The deck is built with --base /slides/<slug>/ so
# it works when served from that subpath on the site. If the talk repo's
# public/ directory bundles a large brand-kit, it is pruned down to only the
# files the built deck actually references.
#
# A PDF sitting next to the source markdown (<talk>.pdf) is copied in as the
# download; generate it first with `npx slidev export` in the talk repo.

set -euo pipefail

if [[ $# -ne 2 ]]; then
    echo "usage: $0 <path-to-slidev-md> <slug>" >&2
    exit 1
fi

SRC_MD=$(cd "$(dirname "$1")" && pwd)/$(basename "$1")
SLUG=$2
SITE_DIR=$(cd "$(dirname "$0")/.." && pwd)
DEST="$SITE_DIR/slides/$SLUG"

# Find the repo root containing the talk (where node_modules lives)
REPO_DIR=$(dirname "$SRC_MD")
while [[ ! -d "$REPO_DIR/node_modules" && "$REPO_DIR" != "/" ]]; do
    REPO_DIR=$(dirname "$REPO_DIR")
done
if [[ "$REPO_DIR" == "/" ]]; then
    echo "error: no node_modules found above $SRC_MD — run npm install in the talk repo" >&2
    exit 1
fi

BUILD_DIR=$(mktemp -d)
(cd "$REPO_DIR" && npx slidev build "$SRC_MD" --base "/slides/$SLUG/" --out "$BUILD_DIR")

# Prune a bundled brand-kit down to only the files the deck references.
if [[ -d "$BUILD_DIR/brand-kit" ]]; then
    KEEP=$(mktemp -d)
    grep -rhoE "/brand-kit/[^\"']+\.(svg|png|jpe?g|webp|gif|woff2?|ttf|otf|mp4)" \
        "$BUILD_DIR/index.html" "$BUILD_DIR/assets" "$BUILD_DIR/theme" 2>/dev/null \
        | sort -u | while IFS= read -r ref; do
        rel=${ref#/}
        if [[ -f "$BUILD_DIR/$rel" ]]; then
            mkdir -p "$KEEP/$(dirname "$rel")"
            cp "$BUILD_DIR/$rel" "$KEEP/$rel"
        fi
    done
    rm -rf "$BUILD_DIR/brand-kit"
    if [[ -d "$KEEP/brand-kit" ]]; then
        cp -R "$KEEP/brand-kit" "$BUILD_DIR/brand-kit"
    fi
    rm -rf "$KEEP"
fi

rm -rf "$DEST"
mkdir -p "$DEST"
cp -R "$BUILD_DIR/." "$DEST/"
rm -rf "$BUILD_DIR"

PDF="${SRC_MD%.md}.pdf"
if [[ -f "$PDF" ]]; then
    cp "$PDF" "$DEST/$SLUG.pdf"
else
    echo "warning: no PDF at $PDF — run 'npx slidev export' in the talk repo, then re-run" >&2
fi

echo "Imported to slides/$SLUG:"
du -sh "$DEST"
