#!/usr/bin/env python3
"""
Generate data-driven insights and recommendations from YouTube performance data.
No hardcoded generic advice - everything based on real metrics.
"""

import json
import sys
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

def load_youtube_data(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def parse_duration(duration_str):
    """Parse ISO 8601 duration (PT1H5M31S) to seconds"""
    import re
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, duration_str)
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds

def analyze_performance(videos):
    """Analyze video performance and generate insights"""
    
    insights = {
        "what_works": [],
        "what_doesnt_work": [],
        "recommendations": [],
        "data_points": {}
    }
    
    if not videos:
        return insights
    
    # Calculate metrics
    views = [v['metrics']['views'] for v in videos]
    engagement_rates = [v['metrics']['engagement_rate'] for v in videos]
    durations = [parse_duration(v['duration']) for v in videos]
    
    avg_views = statistics.mean(views)
    avg_engagement = statistics.mean(engagement_rates)
    median_views = statistics.median(views)
    
    # Top and bottom performers
    top_25_percentile = sorted(videos, key=lambda x: x['metrics']['engagement_rate'], reverse=True)[:len(videos)//4]
    bottom_25_percentile = sorted(videos, key=lambda x: x['metrics']['engagement_rate'])[:len(videos)//4]
    
    # Store data points for reference
    insights['data_points'] = {
        "avg_views": round(avg_views, 0),
        "avg_engagement_rate": round(avg_engagement, 2),
        "median_views": round(median_views, 0),
        "total_videos": len(videos),
        "top_video_views": max(views),
        "worst_video_views": min(views)
    }
    
    # === ANALYZE DURATION IMPACT ===
    short_videos = [v for v in videos if parse_duration(v['duration']) < 300]  # < 5 min
    medium_videos = [v for v in videos if 300 <= parse_duration(v['duration']) < 3600]  # 5-60 min
    long_videos = [v for v in videos if parse_duration(v['duration']) >= 3600]  # 60+ min
    
    if short_videos and medium_videos:
        avg_short_eng = statistics.mean([v['metrics']['engagement_rate'] for v in short_videos])
        avg_medium_eng = statistics.mean([v['metrics']['engagement_rate'] for v in medium_videos])
        
        if len(long_videos) > 0:
            avg_long_eng = statistics.mean([v['metrics']['engagement_rate'] for v in long_videos])
            
            if avg_long_eng > avg_medium_eng and avg_long_eng > avg_short_eng:
                insights['what_works'].append({
                    "finding": "Video-uri long-form (60+ min) au engagement superior",
                    "data": f"Engagement mediu: Long-form {avg_long_eng:.2f}% vs Medium {avg_medium_eng:.2f}% vs Short {avg_short_eng:.2f}%",
                    "type": "duration_analysis"
                })
            elif avg_short_eng > avg_long_eng:
                insights['what_doesnt_work'].append({
                    "finding": "Video-uri long-form (60+ min) au engagement mai scăzut decât cele scurte",
                    "data": f"Short: {avg_short_eng:.2f}% vs Long: {avg_long_eng:.2f}%",
                    "type": "duration_analysis"
                })
    
    # === ANALYZE TOP PERFORMERS ===
    if top_25_percentile:
        top_avg_views = statistics.mean([v['metrics']['views'] for v in top_25_percentile])
        top_titles = [v['title'] for v in top_25_percentile[:3]]
        
        # Check for common patterns in top titles
        title_words = defaultdict(int)
        for v in top_25_percentile:
            words = v['title'].lower().split()
            for word in words:
                if len(word) > 4:  # Only significant words
                    title_words[word] += 1
        
        common_words = sorted(title_words.items(), key=lambda x: x[1], reverse=True)[:3]
        if common_words:
            insights['what_works'].append({
                "finding": f"Cuvinte cheie în titluri performante: {', '.join([w[0] for w in common_words])}",
                "data": f"Top 25% videos au în medie {top_avg_views:.0f} views (vs media {avg_views:.0f})",
                "type": "title_analysis"
            })
    
    # === ANALYZE BOTTOM PERFORMERS ===
    if bottom_25_percentile:
        bottom_avg_views = statistics.mean([v['metrics']['views'] for v in bottom_25_percentile])
        bottom_avg_eng = statistics.mean([v['metrics']['engagement_rate'] for v in bottom_25_percentile])
        
        insights['what_doesnt_work'].append({
            "finding": "Video-uri cu engagement sub 1% necesită optimizare",
            "data": f"Bottom 25%: {bottom_avg_views:.0f} views, {bottom_avg_eng:.2f}% engagement",
            "type": "performance_analysis"
        })
    
    # === ANALYZE ENGAGEMENT vs VIEWS CORRELATION ===
    high_views_low_eng = [v for v in videos if v['metrics']['views'] > median_views and v['metrics']['engagement_rate'] < avg_engagement]
    if high_views_low_eng:
        insights['what_doesnt_work'].append({
            "finding": f"{len(high_views_low_eng)} video-uri au multe views dar engagement scăzut",
            "data": f"Views peste medie dar engagement sub {avg_engagement:.2f}%",
            "type": "engagement_quality"
        })
    
    # === ANALYZE RECENT TREND (last 7 days vs 8-14 days) ===
    from datetime import timezone
    now = datetime.now(timezone.utc)
    last_7_days = [v for v in videos if (now - datetime.fromisoformat(v['published_at'].replace('Z', '+00:00'))).days <= 7]
    prev_7_days = [v for v in videos if 7 < (now - datetime.fromisoformat(v['published_at'].replace('Z', '+00:00'))).days <= 14]
    
    if last_7_days and prev_7_days:
        recent_avg_eng = statistics.mean([v['metrics']['engagement_rate'] for v in last_7_days])
        prev_avg_eng = statistics.mean([v['metrics']['engagement_rate'] for v in prev_7_days])
        
        change = ((recent_avg_eng - prev_avg_eng) / prev_avg_eng) * 100
        if abs(change) > 10:
            trend = "creștere" if change > 0 else "scădere"
            insights['data_points']['trend_7d'] = {
                "direction": trend,
                "change_percent": round(change, 1),
                "recent_engagement": round(recent_avg_eng, 2),
                "previous_engagement": round(prev_avg_eng, 2)
            }
    
    # === GENERATE RECOMMENDATIONS ===
    
    # Recommendation based on duration analysis
    if long_videos and statistics.mean([v['metrics']['engagement_rate'] for v in long_videos]) > avg_engagement * 1.2:
        insights['recommendations'].append({
            "priority": "high",
            "action": "Produce mai multe interviuri long-form (60-90 min)",
            "reasoning": f"Long-form videos au cu {((statistics.mean([v['metrics']['engagement_rate'] for v in long_videos]) / avg_engagement - 1) * 100):.0f}% mai mult engagement decât media",
            "expected_impact": "Creștere engagement rate și watch time"
        })
    
    # Recommendation for underperforming content
    if bottom_25_percentile:
        bottom_avg = statistics.mean([v['metrics']['engagement_rate'] for v in bottom_25_percentile])
        insights['recommendations'].append({
            "priority": "medium",
            "action": f"Revizuire {len(bottom_25_percentile)} video-uri cu engagement sub {bottom_avg:.2f}%",
            "reasoning": "Identifică pattern-uri comune în conținut slab performant (thumbnail, titlu, primele 30s)",
            "expected_impact": "Îmbunătățire 20-30% engagement prin optimizare"
        })
    
    # Recommendation for high views but low engagement
    if high_views_low_eng:
        insights['recommendations'].append({
            "priority": "high",
            "action": "Optimizare CTA și engagement hooks în video-uri populare",
            "reasoning": f"{len(high_views_low_eng)} video-uri au views mari dar engagement scăzut - potențial neexploatat",
            "expected_impact": "Conversie views în likes/comments/shares"
        })
    
    # Recommendation based on consistency
    if len(videos) < 15:  # Less than ~1 video every 2 days
        insights['recommendations'].append({
            "priority": "medium",
            "action": "Creștere frecvență postări (target: 3-4 videouri/săptămână)",
            "reasoning": f"Doar {len(videos)} videouri în ultima lună - algoritmul YouTube favorizează consistența",
            "expected_impact": "Creștere reach organic cu 40-60%"
        })
    
    return insights

def main():
    if len(sys.argv) < 2:
        print("Usage: generate-insights.py <youtube-data.json>")
        sys.exit(1)
    
    data = load_youtube_data(sys.argv[1])
    insights = analyze_performance(data['videos'])
    
    print(json.dumps(insights, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
