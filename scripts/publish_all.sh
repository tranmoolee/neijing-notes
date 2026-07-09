#!/bin/bash
# Batch publish all remaining articles to Ghost
GHOST_KEY="69710b1b1d33160001ed6220:de9b656a3dffda964a5ed7d59a946676590851c800000439aa5597e8a148b44b"
BASE="/Users/tranmoo/neijing-notes"
SRC_JS="$BASE/17-阴中有阴/ghost-publish.js"

for dir in 01-法于阴阳 02-古人骂街 03-女七男八 04-四种人 09-圣人治未病 12-风邪百病 13-煎厥与薄厥; do
  echo ""
  echo "======================================================"
  echo "📦 $dir"

  # Setup xhs-publish-pack/images/
  mkdir -p "$BASE/$dir/xhs-publish-pack/images"
  for f in cover.jpg card-01.jpg card-02.jpg card-03.jpg card-04.jpg card-05.jpg card-06.jpg card-07.jpg card-08.jpg; do
    if [ -f "$BASE/$dir/img-temp/$f" ]; then
      cp "$BASE/$dir/img-temp/$f" "$BASE/$dir/xhs-publish-pack/images/$f"
    fi
  done
  echo "  Images: $(ls $BASE/$dir/xhs-publish-pack/images/*.jpg 2>/dev/null | wc -l)"

  # Copy ghost-publish.js if needed
  [ ! -f "$BASE/$dir/ghost-publish.js" ] && cp "$SRC_JS" "$BASE/$dir/ghost-publish.js"

  # Publish
  echo "  Publishing..."
  cd "$BASE/$dir"
  GHOST_ADMIN_API_KEY="$GHOST_KEY" GHOST_URL="https://www.ileemoo.com" node ghost-publish.js 2>&1 | grep -E "✅|❌|📝|📤|Created|Updated|Total"
done

echo ""
echo "✅ All done!"
