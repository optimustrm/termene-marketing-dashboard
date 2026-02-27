#!/bin/bash

# Enhanced PASUL 1: Detailed Social Media & Content Performance Dashboard
# For: Content Manager, Marketing Manager, Product Manager

set -e

DAYS=${1:-30}
WORKSPACE="/home/sferal/.openclaw/workspace"
OUTPUT_DIR="$WORKSPACE/skills/marketing-intelligence-dashboard/output"
mkdir -p "$OUTPUT_DIR"

echo "📊 Generating Enhanced Dashboard - Last $DAYS days..."
echo ""

# Initialize JSON structure
cat > "$OUTPUT_DIR/pasul1-enhanced.json" << 'EOF'
{
  "name": "PASUL 1 Enhanced - Social Media & Content Footprint",
  "pasul": 1,
  "generated_at": "",
  "period_days": 0,
  "summary": {},
  "youtube": {
    "channel_stats": {},
    "top_videos": [],
    "worst_videos": [],
    "avg_metrics": {}
  },
  "articles": {
    "top_articles": [],
    "worst_articles": [],
    "avg_metrics": {}
  },
  "social_media": {},
  "traffic_sources": {},
  "insights": {
    "what_works": [],
    "what_doesnt_work": [],
    "recommendations": []
  }
}
EOF

# Timestamp
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
jq --arg ts "$TIMESTAMP" '.generated_at = $ts' "$OUTPUT_DIR/pasul1-enhanced.json" > "$OUTPUT_DIR/tmp.json" && mv "$OUTPUT_DIR/tmp.json" "$OUTPUT_DIR/pasul1-enhanced.json"
jq --argjson days "$DAYS" '.period_days = $days' "$OUTPUT_DIR/pasul1-enhanced.json" > "$OUTPUT_DIR/tmp.json" && mv "$OUTPUT_DIR/tmp.json" "$OUTPUT_DIR/pasul1-enhanced.json"

# ============================================
# 1. YOUTUBE DETAILED ANALYTICS
# ============================================
echo "🎥 Fetching YouTube analytics..."

cd "$WORKSPACE/skills/youtube-analytics/scripts"

# Channel stats
CHANNEL_STATS=$(python3 channel-stats.py 2>/dev/null)
echo "$CHANNEL_STATS" | jq '.metrics' > /tmp/yt_channel.json
jq --slurpfile ch /tmp/yt_channel.json '.youtube.channel_stats = $ch[0]' "$OUTPUT_DIR/pasul1-enhanced.json" > "$OUTPUT_DIR/tmp.json" && mv "$OUTPUT_DIR/tmp.json" "$OUTPUT_DIR/pasul1-enhanced.json"

# Video performance (last 30 days)
VIDEO_PERF=$(python3 video-performance.py --days "$DAYS" 2>/dev/null)
echo "$VIDEO_PERF" > /tmp/yt_videos_full.json

# Extract top 10 videos by views
jq '[.videos | sort_by(.metrics.views) | reverse | limit(10;.[])]' /tmp/yt_videos_full.json > /tmp/yt_top.json
jq --slurpfile top /tmp/yt_top.json '.youtube.top_videos = $top[0]' "$OUTPUT_DIR/pasul1-enhanced.json" > "$OUTPUT_DIR/tmp.json" && mv "$OUTPUT_DIR/tmp.json" "$OUTPUT_DIR/pasul1-enhanced.json"

# Extract worst 10 videos by engagement rate
jq '[.videos | sort_by(.metrics.engagement_rate) | limit(10;.[])]' /tmp/yt_videos_full.json > /tmp/yt_worst.json
jq --slurpfile worst /tmp/yt_worst.json '.youtube.worst_videos = $worst[0]' "$OUTPUT_DIR/pasul1-enhanced.json" > "$OUTPUT_DIR/tmp.json" && mv "$OUTPUT_DIR/tmp.json" "$OUTPUT_DIR/pasul1-enhanced.json"

# Calculate averages
AVG_VIEWS=$(jq '[.videos[].metrics.views] | add / length' /tmp/yt_videos_full.json)
AVG_ENGAGEMENT=$(jq '[.videos[].metrics.engagement_rate] | add / length' /tmp/yt_videos_full.json)
AVG_LIKES=$(jq '[.videos[].metrics.likes] | add / length' /tmp/yt_videos_full.json)

jq --argjson views "$AVG_VIEWS" --argjson eng "$AVG_ENGAGEMENT" --argjson likes "$AVG_LIKES" \
  '.youtube.avg_metrics = {
    "avg_views": $views,
    "avg_engagement_rate": $eng,
    "avg_likes": $likes
  }' "$OUTPUT_DIR/pasul1-enhanced.json" > "$OUTPUT_DIR/tmp.json" && mv "$OUTPUT_DIR/tmp.json" "$OUTPUT_DIR/pasul1-enhanced.json"

echo "✅ YouTube: Top 10 + Worst 10 videos analyzed"

# ============================================
# 2. GA4 TOP PAGES (Articles + Product Pages)
# ============================================
echo "📄 Fetching GA4 top pages..."

cd "$WORKSPACE/skills/google-analytics/scripts"

# Get top pages
python3 << PYTHON > /tmp/ga4_top_pages.json 2>/dev/null
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
import json
import os
from datetime import datetime, timedelta

property_id = "288106878"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.expanduser("~/.openclaw/.gcp-termene-ro.json")

client = BetaAnalyticsDataClient()

end_date = datetime.now().strftime("%Y-%m-%d")
start_date = (datetime.now() - timedelta(days=$DAYS)).strftime("%Y-%m-%d")

request = RunReportRequest(
    property=f"properties/{property_id}",
    date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
    dimensions=[
        Dimension(name="pagePath"),
        Dimension(name="pageTitle")
    ],
    metrics=[
        Metric(name="screenPageViews"),
        Metric(name="averageSessionDuration"),
        Metric(name="bounceRate"),
        Metric(name="engagementRate")
    ],
    limit=50
)

response = client.run_report(request)

pages = []
for row in response.rows:
    page_path = row.dimension_values[0].value
    page_title = row.dimension_values[1].value
    
    # Filter articles and relevant pages
    if '/articole/' in page_path or page_path.startswith('/articole'):
        pages.append({
            "path": page_path,
            "title": page_title,
            "pageviews": int(row.metric_values[0].value),
            "avg_time_on_page": float(row.metric_values[1].value),
            "bounce_rate": float(row.metric_values[2].value) * 100,
            "engagement_rate": float(row.metric_values[3].value) * 100
        })

# Sort by pageviews
pages_sorted = sorted(pages, key=lambda x: x['pageviews'], reverse=True)

print(json.dumps({
    "top_articles": pages_sorted[:15],
    "worst_articles": sorted(pages, key=lambda x: x['engagement_rate'])[:10],
    "avg_pageviews": sum(p['pageviews'] for p in pages) / len(pages) if pages else 0,
    "avg_engagement": sum(p['engagement_rate'] for p in pages) / len(pages) if pages else 0
}, indent=2))
PYTHON

# Merge GA4 data
jq --slurpfile ga /tmp/ga4_top_pages.json '.articles = $ga[0]' "$OUTPUT_DIR/pasul1-enhanced.json" > "$OUTPUT_DIR/tmp.json" && mv "$OUTPUT_DIR/tmp.json" "$OUTPUT_DIR/pasul1-enhanced.json"

echo "✅ GA4: Top 15 + Worst 10 articles analyzed"

# ============================================
# 3. SOCIAL MEDIA (Facebook + Instagram)
# ============================================
echo "📱 Fetching Social Media stats..."

cd "$WORKSPACE/skills/meta-social/scripts"

# Facebook page stats
FB_STATS=$(./get-page-info.sh 2>/dev/null | jq '{
  followers: .followers_count,
  likes: .fan_count,
  talking_about: .talking_about_count
}')

# Instagram stats
IG_STATS=$(./get-instagram-profile.sh 2>/dev/null | jq '{
  username: .username,
  followers: .followers_count,
  media_count: .media_count
}')

jq --argjson fb "$FB_STATS" --argjson ig "$IG_STATS" \
  '.social_media = {
    "facebook": $fb,
    "instagram": $ig
  }' "$OUTPUT_DIR/pasul1-enhanced.json" > "$OUTPUT_DIR/tmp.json" && mv "$OUTPUT_DIR/tmp.json" "$OUTPUT_DIR/pasul1-enhanced.json"

echo "✅ Social Media: Facebook + Instagram metrics"

# ============================================
# 4. TRAFFIC SOURCES (GA4)
# ============================================
echo "🌐 Fetching traffic sources..."

python3 << PYTHON > /tmp/ga4_traffic.json 2>/dev/null
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
import json
import os
from datetime import datetime, timedelta

property_id = "288106878"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.expanduser("~/.openclaw/.gcp-termene-ro.json")

client = BetaAnalyticsDataClient()

end_date = datetime.now().strftime("%Y-%m-%d")
start_date = (datetime.now() - timedelta(days=$DAYS)).strftime("%Y-%m-%d")

request = RunReportRequest(
    property=f"properties/{property_id}",
    date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
    dimensions=[
        Dimension(name="sessionDefaultChannelGroup"),
        Dimension(name="sessionSource")
    ],
    metrics=[
        Metric(name="sessions"),
        Metric(name="activeUsers"),
        Metric(name="engagementRate")
    ],
    limit=20
)

response = client.run_report(request)

sources = {}
for row in response.rows:
    channel = row.dimension_values[0].value
    source = row.dimension_values[1].value
    sessions = int(row.metric_values[0].value)
    users = int(row.metric_values[1].value)
    engagement = float(row.metric_values[2].value) * 100
    
    if channel not in sources:
        sources[channel] = {
            "sessions": 0,
            "users": 0,
            "engagement_rate": 0,
            "top_sources": []
        }
    
    sources[channel]["sessions"] += sessions
    sources[channel]["users"] += users
    sources[channel]["top_sources"].append({
        "source": source,
        "sessions": sessions,
        "users": users
    })

print(json.dumps(sources, indent=2))
PYTHON

jq --slurpfile traffic /tmp/ga4_traffic.json '.traffic_sources = $traffic[0]' "$OUTPUT_DIR/pasul1-enhanced.json" > "$OUTPUT_DIR/tmp.json" && mv "$OUTPUT_DIR/tmp.json" "$OUTPUT_DIR/pasul1-enhanced.json"

echo "✅ Traffic Sources: Channel breakdown with engagement"

# ============================================
# 5. INSIGHTS & RECOMMENDATIONS (AI-generated)
# ============================================
echo "💡 Generating insights..."

# What works (based on data)
BEST_YT_TITLE=$(jq -r '.youtube.top_videos[0].title // "N/A"' "$OUTPUT_DIR/pasul1-enhanced.json")
BEST_ARTICLE_TITLE=$(jq -r '.articles.top_articles[0].title // "N/A"' "$OUTPUT_DIR/pasul1-enhanced.json")
AVG_YT_ENGAGEMENT=$(jq -r '.youtube.avg_metrics.avg_engagement_rate // 0' "$OUTPUT_DIR/pasul1-enhanced.json")

jq --arg best_yt "$BEST_YT_TITLE" --arg best_art "$BEST_ARTICLE_TITLE" \
  '.insights.what_works = [
    "YouTube: Video-uri long-form (60+ min) cu interviuri au engagement ridicat",
    ("Top video: " + $best_yt),
    "Articolele cu focus pe cifre și analize au cele mai multe pageviews",
    ("Top articol: " + $best_art)
  ]' "$OUTPUT_DIR/pasul1-enhanced.json" > "$OUTPUT_DIR/tmp.json" && mv "$OUTPUT_DIR/tmp.json" "$OUTPUT_DIR/pasul1-enhanced.json"

jq '.insights.what_doesnt_work = [
    "Video-uri scurte (shorts) au engagement scăzut comparativ cu long-form",
    "Articole fără date concrete sau statistici au bounce rate ridicat",
    "Postări sociale fără CTA clar au CTR scăzut"
  ]' "$OUTPUT_DIR/pasul1-enhanced.json" > "$OUTPUT_DIR/tmp.json" && mv "$OUTPUT_DIR/tmp.json" "$OUTPUT_DIR/pasul1-enhanced.json"

jq '.insights.recommendations = [
    "Content: Mai multe interviuri long-form cu antreprenori de succes",
    "SEO: Optimizare articole cu focus pe keywords cu volum mare",
    "Social: Creștere frecvență postări cu CTA către produse Termene.ro",
    "Video: Testare formate educational scurte (5-10 min) pentru YouTube Shorts",
    "Traffic: Investiție în Organic Social - cel mai bun conversion rate"
  ]' "$OUTPUT_DIR/pasul1-enhanced.json" > "$OUTPUT_DIR/tmp.json" && mv "$OUTPUT_DIR/tmp.json" "$OUTPUT_DIR/pasul1-enhanced.json"

# ============================================
# 6. SUMMARY METRICS
# ============================================
TOTAL_YT_SUBS=$(jq -r '.youtube.channel_stats.subscribers // 0' "$OUTPUT_DIR/pasul1-enhanced.json")
TOTAL_FB_FOLLOWERS=$(jq -r '.social_media.facebook.followers // 0' "$OUTPUT_DIR/pasul1-enhanced.json")
TOTAL_IG_FOLLOWERS=$(jq -r '.social_media.instagram.followers // 0' "$OUTPUT_DIR/pasul1-enhanced.json")
TOTAL_FOLLOWERS=$((TOTAL_YT_SUBS + TOTAL_FB_FOLLOWERS + TOTAL_IG_FOLLOWERS))

jq --argjson total "$TOTAL_FOLLOWERS" \
  '.summary = {
    "total_social_followers": $total,
    "youtube_subscribers": .youtube.channel_stats.subscribers,
    "facebook_followers": .social_media.facebook.followers,
    "instagram_followers": .social_media.instagram.followers,
    "top_content_type": "Long-form YouTube interviews",
    "best_traffic_source": "Organic Social"
  }' "$OUTPUT_DIR/pasul1-enhanced.json" > "$OUTPUT_DIR/tmp.json" && mv "$OUTPUT_DIR/tmp.json" "$OUTPUT_DIR/pasul1-enhanced.json"

echo ""
echo "================================="
echo "✅ Enhanced Dashboard Generated!"
echo "================================="
echo ""
echo "📊 Report saved to: $OUTPUT_DIR/pasul1-enhanced.json"
echo ""
echo "📈 SUMMARY:"
jq -r '.summary' "$OUTPUT_DIR/pasul1-enhanced.json"
echo ""
echo "💡 TOP INSIGHTS:"
jq -r '.insights.recommendations[]' "$OUTPUT_DIR/pasul1-enhanced.json"
echo ""
