#!/bin/bash
# Quick dashboard data update script

set -e

WORKSPACE="/home/sferal/.openclaw/workspace"
OUTPUT_DIR="$WORKSPACE/skills/marketing-intelligence-dashboard/output"

echo "🔄 Updating Marketing Intelligence Dashboard..."
echo ""

# YouTube data
echo "📥 Fetching YouTube data..."
cd "$WORKSPACE/skills/youtube-analytics/scripts"
python3 video-performance.py --days 30 2>/dev/null > "$OUTPUT_DIR/youtube-detailed.json"
python3 channel-stats.py 2>/dev/null > "$OUTPUT_DIR/channel-stats.json"
echo "✅ YouTube data updated"

# Commit & push
echo ""
echo "📤 Pushing to GitHub..."
cd "$WORKSPACE/skills/marketing-intelligence-dashboard"
git add output/*.json
git commit -m "Auto-update dashboard data - $(date +'%Y-%m-%d %H:%M')"
git push

echo ""
echo "================================="
echo "✅ Dashboard updated successfully!"
echo "================================="
echo ""
echo "🌐 Live at: https://optimustrm.github.io/termene-marketing-dashboard/"
echo "⏱️  GitHub Pages will refresh in 1-2 minutes"
echo ""

# Show summary
echo "📊 SUMMARY:"
jq '{
  videos: .video_count,
  total_views: ([.videos[].metrics.views] | add),
  avg_engagement: (([.videos[].metrics.engagement_rate] | add / length) | . * 100 | round / 100),
  updated: .timestamp
}' "$OUTPUT_DIR/youtube-detailed.json"
