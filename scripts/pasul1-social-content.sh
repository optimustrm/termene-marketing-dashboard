#!/bin/bash
# PASUL 1: Social Media & Content Footprint Dashboard
# Aggregates data from Facebook, Instagram, YouTube, Website, Articles, SEO

set -euo pipefail

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
LIB_DIR="$SKILL_DIR/lib"
OUTPUT_DIR="$SKILL_DIR/output"

# Default parameters
DAYS=30
OUTPUT_FILE="$OUTPUT_DIR/pasul1-social-content.json"
PRETTY=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --days)
            DAYS="$2"
            shift 2
            ;;
        --output|-o)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --pretty)
            PRETTY=true
            shift
            ;;
        -h|--help)
            cat <<EOF
PASUL 1: Social Media & Content Footprint Dashboard

Usage: $0 [OPTIONS]

Options:
    --days N           Number of days for historical data (default: 30)
    --output FILE      Output JSON file (default: output/pasul1-social-content.json)
    --pretty           Pretty print JSON
    -h, --help         Show this help message

Description:
    Aggregates social media analytics (Facebook, Instagram, YouTube),
    website traffic, article performance, and SEO data.
    
    Generates transfer rates showing Social → Site conversion.

Output:
    JSON file containing:
    - Facebook & Instagram metrics (reach, engagement, followers)
    - YouTube metrics (subscribers, views, watch time)
    - Website traffic (sessions, users, pageviews)
    - Social breakdown (LinkedIn, Facebook, Instagram, TikTok, YouTube)
    - Article performance (top articles, pageviews, time on page)
    - SEO performance (impressions, clicks, CTR, rankings)
    - Transfer rates (Social → Site conversion rates)

Examples:
    # Generate last 30 days report
    $0
    
    # Last 7 days with pretty output
    $0 --days 7 --pretty
    
    # Custom output location
    $0 --output /tmp/social-report.json

EOF
            exit 0
            ;;
        *)
            echo "ERROR: Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "========================================"
echo "PASUL 1: Social Media & Content Footprint"
echo "========================================"
echo "Period: Last $DAYS days"
echo "Output: $OUTPUT_FILE"
echo ""

# Temporary files for intermediate results
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

META_DATA="$TEMP_DIR/meta-social.json"
YOUTUBE_DATA="$TEMP_DIR/youtube.json"
GA4_DATA="$TEMP_DIR/ga4.json"
GSC_DATA="$TEMP_DIR/gsc.json"

# 1. Aggregate Meta Social (Facebook + Instagram)
echo "📱 [1/4] Aggregating Meta Social (Facebook + Instagram)..."
python3 "$LIB_DIR/meta-social-aggregator-fixed.py" \
    --output "$META_DATA" \
    2>&1 | grep -v "^$" || true

# 2. Aggregate YouTube
echo ""
echo "📺 [2/4] Aggregating YouTube Analytics..."
python3 "$LIB_DIR/youtube-aggregator.py" \
    --days "$DAYS" \
    --output "$YOUTUBE_DATA" \
    2>&1 | grep -v "^$" || true

# 3. Aggregate GA4 (with transfer rates)
echo ""
echo "🌐 [3/4] Aggregating GA4 (Website + Articles)..."
python3 "$LIB_DIR/ga4-aggregator-fixed.py" \
    --days "$DAYS" \
    --output "$GA4_DATA" \
    2>&1 | grep -v "^$" || true

# 4. Aggregate GSC (SEO)
echo ""
echo "🔍 [4/4] Aggregating Google Search Console (SEO)..."
python3 "$LIB_DIR/gsc-aggregator.py" \
    --days "$DAYS" \
    --output "$GSC_DATA" \
    2>&1 | grep -v "^$" || true

# 5. Combine all data into final report
echo ""
echo "📊 Combining data..."

REPORT_JSON=$(python3 - <<PYTHON_SCRIPT
import json
import sys
from datetime import datetime

# Load all data
with open('$META_DATA') as f:
    meta = json.load(f)

with open('$YOUTUBE_DATA') as f:
    youtube = json.load(f)

with open('$GA4_DATA') as f:
    ga4 = json.load(f)

with open('$GSC_DATA') as f:
    gsc = json.load(f)

# Combine into PASUL 1 structure
report = {
    'generated_at': datetime.now().isoformat(),
    'period_days': $DAYS,
    'pasul': 1,
    'name': 'Social Media & Content Footprint Dashboard',
    'social_media': {
        'facebook': meta.get('facebook', {}),
        'instagram': meta.get('instagram', {}),
        'youtube': youtube.get('summary', {}),
        'linkedin': {
            'note': 'Native metrics unavailable (LinkedIn API needed)',
            'sessions_to_site': ga4.get('social_breakdown', {}).get('linkedin', {}).get('sessions', 0)
        },
        'tiktok': {
            'note': 'Native metrics unavailable (TikTok API needed)',
            'sessions_to_site': ga4.get('social_breakdown', {}).get('tiktok', {}).get('sessions', 0)
        }
    },
    'website_traffic': ga4.get('website_overview', {}),
    'traffic_sources': ga4.get('traffic_sources', {}),
    'social_breakdown': ga4.get('social_breakdown', {}),
    'articles': ga4.get('articles', {}),
    'seo': gsc.get('summary', {}),
    'transfer_rates': ga4.get('transfer_rates', {}),
    'summary': {
        'total_social_followers': (
            meta.get('instagram', {}).get('followers', 0) + 
            youtube.get('summary', {}).get('subscribers', 0)
        ),
        'total_social_reach': meta.get('aggregate', {}).get('total_reach', 0),
        'total_website_sessions': ga4.get('website_overview', {}).get('sessions', 0),
        'total_article_pageviews': ga4.get('articles', {}).get('total_pageviews', 0),
        'total_seo_impressions': gsc.get('summary', {}).get('total_impressions', 0),
        'total_seo_clicks': gsc.get('summary', {}).get('total_clicks', 0)
    }
}

# Output
indent = 2 if '$PRETTY' == 'true' else None
print(json.dumps(report, indent=indent))
PYTHON_SCRIPT
)

echo "$REPORT_JSON" > "$OUTPUT_FILE"

echo ""
echo "========================================"
echo "✅ PASUL 1 Complete!"
echo "========================================"
echo "Report saved to: $OUTPUT_FILE"
echo ""

# Show summary
echo "📊 SUMMARY:"
jq -r '
"  Total Social Followers: \(.summary.total_social_followers)"
, "  Total Social Reach: \(.summary.total_social_reach)"
, "  Website Sessions: \(.summary.total_website_sessions)"
, "  Article Pageviews: \(.summary.total_article_pageviews)"
, "  SEO Impressions: \(.summary.total_seo_impressions)"
, "  SEO Clicks: \(.summary.total_seo_clicks)"
' "$OUTPUT_FILE" 2>/dev/null || echo "  (JSON parsing failed, see $OUTPUT_FILE)"

echo ""
echo "📈 TRANSFER RATES:"
jq -r '.transfer_rates | to_entries[] | "  \(.key): \(.value // "N/A")"' "$OUTPUT_FILE" 2>/dev/null || echo "  (No transfer rates data)"

echo ""
echo "Next: Run pasul2-product-traffic.sh for Product Traffic Dashboard"
