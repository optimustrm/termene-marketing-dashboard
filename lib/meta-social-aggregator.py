#!/usr/bin/env python3
"""
Meta Social Aggregator - Facebook & Instagram Analytics
Aggregates data from Meta Social skill for Marketing Intelligence Dashboard
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Paths
WORKSPACE = Path.home() / '.openclaw' / 'workspace'
META_SOCIAL_SCRIPT = WORKSPACE / 'skills' / 'meta-social' / 'scripts' / 'analytics.sh'

def run_command(cmd):
    """Execute shell command and return JSON output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout) if result.stdout.strip() else {}
    except subprocess.CalledProcessError as e:
        print(f"ERROR running command: {cmd}", file=sys.stderr)
        print(f"  {e.stderr}", file=sys.stderr)
        return None
    except json.JSONDecodeError:
        print(f"ERROR: Invalid JSON from command: {cmd}", file=sys.stderr)
        return None

def get_instagram_insights(period='day'):
    """Get Instagram account insights"""
    cmd = f"{META_SOCIAL_SCRIPT} --type account --platform instagram --period {period} --json"
    data = run_command(cmd)
    
    if not data or 'data' not in data:
        return None
    
    # Parse insights
    metrics = {}
    for item in data.get('data', []):
        name = item.get('name')
        values = item.get('values', [])
        if values:
            metrics[name] = values[0].get('value', 0)
    
    return {
        'followers': metrics.get('follower_count', 0),
        'impressions': metrics.get('impressions', 0),
        'reach': metrics.get('reach', 0),
        'profile_views': metrics.get('profile_views', 0),
        'period': period
    }

def get_facebook_insights(period='day'):
    """Get Facebook Page insights"""
    cmd = f"{META_SOCIAL_SCRIPT} --type account --platform facebook --period {period} --json"
    data = run_command(cmd)
    
    if not data or 'data' not in data:
        return None
    
    # Parse insights
    metrics = {}
    for item in data.get('data', []):
        name = item.get('name')
        values = item.get('values', [])
        if values:
            metrics[name] = values[0].get('value', 0)
    
    return {
        'page_impressions': metrics.get('page_impressions', 0),
        'page_engaged_users': metrics.get('page_engaged_users', 0),
        'page_fan_adds': metrics.get('page_fan_adds', 0),
        'period': period
    }

def get_instagram_posts_performance(days=30):
    """
    Get recent Instagram posts performance
    Returns: list of top performing posts
    """
    # TODO: Implement get_recent_posts from Meta Social skill
    # This will require querying /{ig-user-id}/media?fields=...
    # For now, return placeholder
    return {
        'note': 'Posts performance not yet implemented',
        'total_posts': 0,
        'top_posts': []
    }

def get_facebook_posts_performance(days=30):
    """
    Get recent Facebook posts performance
    Returns: list of top performing posts
    """
    # TODO: Implement get_recent_posts from Meta Social skill
    # This will require querying /{page-id}/published_posts?fields=...
    # For now, return placeholder
    return {
        'note': 'Posts performance not yet implemented',
        'total_posts': 0,
        'top_posts': []
    }

def calculate_engagement_rate(reach, engagements):
    """Calculate engagement rate: engagements / reach * 100"""
    if reach == 0:
        return 0.0
    return round((engagements / reach) * 100, 2)

def aggregate_meta_data(period='day'):
    """
    Main aggregation function
    Returns: Combined Facebook + Instagram analytics
    """
    
    print(f"📊 Aggregating Meta Social data (period: {period})...", file=sys.stderr)
    
    # Get Instagram data
    print("  - Fetching Instagram insights...", file=sys.stderr)
    instagram = get_instagram_insights(period)
    
    if not instagram:
        print("  ⚠️ Instagram insights failed", file=sys.stderr)
        instagram = {'error': 'Failed to fetch Instagram data'}
    
    # Get Facebook data
    print("  - Fetching Facebook insights...", file=sys.stderr)
    facebook = get_facebook_insights(period)
    
    if not facebook:
        print("  ⚠️ Facebook insights failed", file=sys.stderr)
        facebook = {'error': 'Failed to fetch Facebook data'}
    
    # Calculate aggregate metrics
    print("  - Calculating aggregates...", file=sys.stderr)
    
    result = {
        'generated_at': datetime.now().isoformat(),
        'period': period,
        'instagram': instagram,
        'facebook': facebook,
        'aggregate': {
            'total_reach': instagram.get('reach', 0) + facebook.get('page_impressions', 0),
            'total_engagement': instagram.get('profile_views', 0) + facebook.get('page_engaged_users', 0)
        }
    }
    
    # Add engagement rate if we have data
    if instagram and 'reach' in instagram:
        result['instagram']['engagement_rate'] = calculate_engagement_rate(
            instagram['reach'],
            instagram.get('profile_views', 0)
        )
    
    print("  ✅ Meta Social aggregation complete", file=sys.stderr)
    
    return result

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Aggregate Meta Social (Facebook + Instagram) analytics')
    parser.add_argument('--period', choices=['day', 'week', 'days_28'], default='day',
                        help='Time period for insights (default: day)')
    parser.add_argument('--output', '-o', help='Output JSON file (default: stdout)')
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON')
    
    args = parser.parse_args()
    
    # Aggregate data
    data = aggregate_meta_data(args.period)
    
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
