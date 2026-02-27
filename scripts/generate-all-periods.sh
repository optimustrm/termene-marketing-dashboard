#!/bin/bash
# Generate data for multiple time periods

set -e

WORKSPACE="/home/sferal/.openclaw/workspace"
YT_SCRIPTS="$WORKSPACE/skills/youtube-analytics/scripts"
OUTPUT_DIR="$WORKSPACE/skills/marketing-intelligence-dashboard/output"
INSIGHTS_SCRIPT="$WORKSPACE/skills/marketing-intelligence-dashboard/scripts/generate-insights.py"

echo "📊 Generating multi-period analytics..."
echo ""

mkdir -p "$OUTPUT_DIR"

# Generate for different periods
for DAYS in 1 7 30 90 365; do
    echo "📥 Fetching $DAYS days data..."
    
    python3 "$YT_SCRIPTS/video-performance.py" --days "$DAYS" 2>/dev/null > "$OUTPUT_DIR/youtube-${DAYS}d.json"
    
    # Generate insights for this period
    echo "💡 Generating insights for $DAYS days..."
    python3 "$INSIGHTS_SCRIPT" "$OUTPUT_DIR/youtube-${DAYS}d.json" > "$OUTPUT_DIR/insights-${DAYS}d.json" 2>/dev/null || echo "{}" > "$OUTPUT_DIR/insights-${DAYS}d.json"
    
    echo "✅ ${DAYS}d data generated"
    echo ""
done

# Channel stats (always current)
echo "📊 Fetching channel stats..."
python3 "$YT_SCRIPTS/channel-stats.py" 2>/dev/null > "$OUTPUT_DIR/channel-stats.json"

echo ""
echo "================================="
echo "✅ All periods generated!"
echo "================================="
echo ""
echo "Available periods:"
echo "  - 1 day:    youtube-1d.json + insights-1d.json"
echo "  - 7 days:   youtube-7d.json + insights-7d.json"
echo "  - 30 days:  youtube-30d.json + insights-30d.json"
echo "  - 90 days:  youtube-90d.json + insights-90d.json"
echo "  - 365 days: youtube-365d.json + insights-365d.json"
echo ""
