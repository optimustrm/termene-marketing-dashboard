#!/usr/bin/env python3
"""
Meta Social Aggregator - FIXED VERSION
Uses direct API calls instead of analytics.sh script
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

def load_env():
    """Load credentials from ~/.openclaw/.env"""
    env_path = Path.home() / '.openclaw' / '.env'
    creds = {}
    
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    creds[key] = value.strip('"').strip("'")
    
    return creds

def get_instagram_insights(token, ig_id):
    """Get Instagram account insights"""
    
    # Basic metrics (doesn't require time period)
    url = f"https://graph.facebook.com/v18.0/{ig_id}"
    params = {
        'fields': 'username,followers_count,media_count,profile_picture_url',
        'access_token': token
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        return {
            'username': data.get('username'),
            'followers': data.get('followers_count', 0),
            'media_count': data.get('media_count', 0),
            'profile_picture': data.get('profile_picture_url'),
            'note': 'Real-time follower count'
        }
    except requests.exceptions.RequestException as e:
        print(f"Instagram API error: {e}", file=sys.stderr)
        return {'error': str(e)}

def get_facebook_page_info(token, page_id):
    """Get Facebook Page basic info"""
    
    url = f"https://graph.facebook.com/v18.0/{page_id}"
    params = {
        'fields': 'name,followers_count,fan_count,talking_about_count',
        'access_token': token
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        return {
            'name': data.get('name'),
            'followers': data.get('followers_count', 0),
            'likes': data.get('fan_count', 0),
            'talking_about': data.get('talking_about_count', 0),
            'note': 'Real-time follower count'
        }
    except requests.exceptions.RequestException as e:
        print(f"Facebook API error: {e}", file=sys.stderr)
        return {'error': str(e)}

def aggregate_meta_data():
    """
    Main aggregation function
    Returns: Combined Facebook + Instagram data
    """
    
    print(f"📱 Aggregating Meta Social data (direct API)...", file=sys.stderr)
    
    creds = load_env()
    token = creds.get('FACEBOOK_PAGE_ACCESS_TOKEN')
    page_id = creds.get('FACEBOOK_PAGE_ID')
    ig_id = creds.get('INSTAGRAM_BUSINESS_ACCOUNT_ID')
    
    if not token:
        return {'error': 'FACEBOOK_PAGE_ACCESS_TOKEN not found in .env'}
    
    # Get Instagram data
    print("  - Fetching Instagram data...", file=sys.stderr)
    instagram = get_instagram_insights(token, ig_id) if ig_id else {'error': 'No Instagram ID'}
    
    # Get Facebook data
    print("  - Fetching Facebook data...", file=sys.stderr)
    facebook = get_facebook_page_info(token, page_id) if page_id else {'error': 'No Page ID'}
    
    print("  ✅ Meta Social aggregation complete", file=sys.stderr)
    
    return {
        'generated_at': datetime.now().isoformat(),
        'instagram': instagram,
        'facebook': facebook,
        'aggregate': {
            'total_followers': (
                instagram.get('followers', 0) + 
                facebook.get('followers', 0)
            )
        }
    }

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Aggregate Meta Social (Facebook + Instagram) - FIXED')
    parser.add_argument('--output', '-o', help='Output JSON file (default: stdout)')
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON')
    
    args = parser.parse_args()
    
    # Aggregate data
    data = aggregate_meta_data()
    
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
