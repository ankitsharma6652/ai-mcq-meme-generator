#!/bin/bash

# Check if ModelScope model is fully downloaded

echo "🔍 Checking ModelScope model download status..."
echo ""

CACHE_DIR="$HOME/.cache/huggingface"
MODEL_DIR="$CACHE_DIR/hub/models--damo-vilab--text-to-video-ms-1.7b"

if [ ! -d "$MODEL_DIR" ]; then
    echo "❌ Model not found. Download hasn't started yet."
    exit 1
fi

# Check total size
TOTAL_SIZE=$(du -sh "$CACHE_DIR" | cut -f1)
echo "📦 Total cache size: $TOTAL_SIZE"

# Check for incomplete files
INCOMPLETE_COUNT=$(find "$MODEL_DIR" -name "*.incomplete" | wc -l | tr -d ' ')

if [ "$INCOMPLETE_COUNT" -eq 0 ]; then
    echo "✅ Model download COMPLETE!"
    echo "🎉 You can now use local AI video generation!"
    echo ""
    echo "To test:"
    echo "1. Refresh your browser"
    echo "2. Generate a video meme"
    echo "3. Should complete in 10-20 seconds"
else
    echo "⏳ Model download IN PROGRESS..."
    echo "📊 Incomplete files: $INCOMPLETE_COUNT"
    echo ""
    echo "Incomplete file sizes:"
    find "$MODEL_DIR" -name "*.incomplete" -exec ls -lh {} \; | awk '{print "  - " $5}'
    echo ""
    echo "💡 Tip: Run this script again in a few minutes to check progress"
fi

echo ""
echo "Expected total size: ~4GB"
echo "Current size: $TOTAL_SIZE"
