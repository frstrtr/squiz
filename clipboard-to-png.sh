#!/bin/bash
# Save clipboard image to PNG in assets folder
# Usage: ./clipboard-to-png.sh filename.png

# Check if filename provided
if [ -z "$1" ]; then
    echo "Usage: $0 <filename.png>"
    echo "Example: $0 question-93.png"
    exit 1
fi

# Ensure assets directory exists
mkdir -p source/assets

# Set output path
OUTPUT="assets/$1"

# Save clipboard image using xclip
xclip -selection clipboard -t image/png -o > "$OUTPUT"

# Check if successful
if [ $? -eq 0 ] && [ -s "$OUTPUT" ]; then
    echo "✓ Saved clipboard image to: $OUTPUT"
    ls -lh "$OUTPUT"
else
    echo "✗ Failed to save image. Make sure you have an image in your clipboard."
    rm -f "$OUTPUT"
    exit 1
fi
