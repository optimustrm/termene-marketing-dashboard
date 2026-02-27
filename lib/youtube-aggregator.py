#!/usr/bin/env python3
"""
YouTube Analytics Aggregator
Aggregates data from YouTube Analytics skill for Marketing Intelligence Dashboard
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Paths
WORKSPACE = Path.home() / '.openclaw' / 'workspace'
YOUTUBE_SKILL = WORKSPACE / 'skills' / 'youtube-analytics' / 'scripts'

def run_python_script(script_path, args=[]):
    """Execute Python script and return JSON output"""
    try:
        cmd = ['python3', str(script_path)] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout) if result.stdout.strip() else {}
    except subprocess.CalledProcessError as e:
        print(f"ERROR running {script_path.name}: {e.stderr}", file=sys.stderr)
        return None
    except json.JSONDecodeError:
        print(f"ERROR: Invalid JSON from {script_path.name}", file=sys.stderr)
        print(f"Output: {result.stdout[:200]}", file=sys.stderr)
        return None

def get_channel_stats():
    """Get basic channel statistics"""
    script = YOUTUBE_SKILL / 'channel-stats.py'
    data = run_python_script(script)
    
    if not data:
        return {'error': 'Failed to fetch channel stats'}
    
    return {
        'channel_id': data.get('channel_id'),
        'channel_name': data.get('channel_name'),
        'subscribers': data.get('subscribers', 0),
        'total_views': data.get('total_views', 0),
        'total_videos': data.get('total_videos', 0)
    }

def get_video_performance(days=30):
    """Get recent video performance"""
    script = YOUTUBE_SKILL / 'video-performance.py'
    # TODO: Add date range parameters when implementing
    data = run_python_script(script, ['--days', str(days)])
    
    if not data:
        return {
            'note': 'Video performance data unavailable',
            'total_videos': 0,
            'top_videos': []
        }
    
    return data

def get_traffic_sources():
    """Get traffic source breakdown"""
    script = YOUTUBE_SKILL / 'traffic-sources.py'
    data = run_python_script(script)
    
    if not data:
        return {
            'note': 'Traffic sources unavailable',
            'sources': []
        }
    
    return data

def get_audience_retention():
    """Get average audience retention"""
    script = YOUTUBE_SKILL / 'audience-retention.py'
    data = run_python_script(script)
    
    if not data:
        return {
            'note': 'Retention data unavailable',
            'average_retention': 0
        }
    
    return data

def get_daily_metrics(days=30):
    """Get daily metrics for the period"""
    script = YOUTUBE_SKILL / 'daily-report.py'
    # TODO: Add date range when implementing
    data = run_python_script(script)
    
    if not data:
        return {
            'note': 'Daily metrics unavailable',
            'views': 0,
            'watch_time_hours': 0,
            'subscribers_gained': 0
        }
    
    return data

def aggregate_youtube_data(days=30):
    """
    Main aggregation function
    Returns: Combined YouTube analytics
    """
    
    print(f"📺 Aggregating YouTube data (last {days} days)...", file=sys.stderr)
    
    # Get channel stats
    print("  - Fetching channel stats...", file=sys.stderr)
    channel_stats = get_channel_stats()
    
    # Get video performance
    print("  - Fetching video performance...", file=sys.stderr)
    video_performance = get_video_performance(days)
    
    # Get traffic sources
    print("  - Fetching traffic sources...", file=sys.stderr)
    traffic_sources = get_traffic_sources()
    
    # Get audience retention
    print("  - Fetching audience retention...", file=sys.stderr)
    retention = get_audience_retention()
    
    # Get daily metrics
    print("  - Fetching daily metrics...", file=sys.stderr)
    daily_metrics = get_daily_metrics(days)
    
    print("  ✅ YouTube aggregation complete", file=sys.stderr)
    
    return {
        'generated_at': datetime.now().isoformat(),
        'period_days': days,
        'channel': channel_stats,
        'video_performance': video_performance,
        'traffic_sources': traffic_sources,
        'audience_retention': retention,
        'daily_metrics': daily_metrics,
        'summary': {
            'subscribers': channel_stats.get('subscribers', 0),
            'total_views': channel_stats.get('total_views', 0),
            'total_videos': channel_stats.get('total_videos', 0),
            'avg_retention': retention.get('average_retention', 0)
        }
    }

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Aggregate YouTube analytics')
    parser.add_argument('--days', type=int, default=30,
                        help='Number of days for historical data (default: 30)')
    parser.add_argument('--output', '-o', help='Output JSON file (default: stdout)')
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON')
    
    args = parser.parse_args()
    
    # Aggregate data
    data = aggregate_youtube_data(args.days)
    
    # Output
    indent = 2 if args.pretty else None
    json_output = json.dumps(data, indent=indent)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(json_output)
        print(f"✅ Data saved to {args.output}", file=sys.stderr)
    else:
        print(json_output)

if __name__ == '__main__':
    main()
