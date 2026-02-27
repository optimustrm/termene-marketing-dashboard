#!/usr/bin/env python3
"""
Google Analytics 4 Aggregator - FIXED VERSION
Uses existing analyze.sh script that already works
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Paths
WORKSPACE = Path.home() / '.openclaw' / 'workspace'
GA4_SKILL = WORKSPACE / 'skills' / 'google-analytics' / 'scripts'

def run_ga4_script(days=7):
    """Run existing GA4 analyze.sh script"""
    try:
        cmd = f"cd {GA4_SKILL} && bash analyze.sh termene {days}"
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse the text output
        output = result.stdout
        
        # Extract key metrics (basic parsing)
        data = {
            'users': 0,
            'sessions': 0,
            'pageviews': 0,
            'bounce_rate': 0.0,
            'avg_session_duration': 0,
            'new_users': 0
        }
        
        for line in output.split('\n'):
            if 'Active Users:' in line:
                data['users'] = int(line.split(':')[1].strip())
            elif 'Sessions:' in line:
                data['sessions'] = int(line.split(':')[1].strip())
            elif 'Page Views:' in line:
                data['pageviews'] = int(line.split(':')[1].strip())
            elif 'Bounce Rate:' in line:
                data['bounce_rate'] = float(line.split(':')[1].strip().rstrip('%'))
            elif 'New Users:' in line:
                data['new_users'] = int(line.split(':')[1].strip())
        
        # GSC data
        gsc_data = {
            'clicks': 0,
            'impressions': 0,
            'ctr': 0.0,
            'avg_position': 0.0
        }
        
        for line in output.split('\n'):
            if '- Clicks:' in line:
                gsc_data['clicks'] = int(line.split(':')[1].strip())
            elif '- Impressions:' in line:
                gsc_data['impressions'] = int(line.split(':')[1].strip())
            elif '- CTR:' in line:
                gsc_data['ctr'] = float(line.split(':')[1].strip().rstrip('%'))
            elif '- Avg Position:' in line:
                gsc_data['avg_position'] = float(line.split(':')[1].strip())
        
        return {
            'website_overview': data,
            'gsc': gsc_data,
            'raw_output': output
        }
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR running GA4 script: {e.stderr}", file=sys.stderr)
        return None

def aggregate_ga4_data(days=30):
    """
    Main aggregation function
    """
    
    print(f"🌐 Aggregating GA4 data (last {days} days)...", file=sys.stderr)
    
    # Run GA4 script
    print("  - Running GA4 analyze.sh...", file=sys.stderr)
    ga4_data = run_ga4_script(days)
    
    if not ga4_data:
        return {
            'error': 'Failed to fetch GA4 data',
            'website_overview': {},
            'gsc': {}
        }
    
    # Placeholder social breakdown (will be populated by actual GA4 API later)
    social_breakdown = {
        'linkedin': {'sessions': 0, 'users': 0, 'bounce_rate': 0.0},
        'facebook': {'sessions': 0, 'users': 0, 'bounce_rate': 0.0},
        'instagram': {'sessions': 0, 'users': 0, 'bounce_rate': 0.0},
        'tiktok': {'sessions': 0, 'users': 0, 'bounce_rate': 0.0},
        'youtube': {'sessions': 0, 'users': 0, 'bounce_rate': 0.0},
        'twitter': {'sessions': 0, 'users': 0, 'bounce_rate': 0.0}
    }
    
    print("  ✅ GA4 aggregation complete", file=sys.stderr)
    
    return {
        'generated_at': datetime.now().isoformat(),
        'period_days': days,
        'website_overview': ga4_data['website_overview'],
        'gsc': ga4_data['gsc'],
        'social_breakdown': social_breakdown,
        'articles': {
            'note': 'Article performance available in raw output',
            'total_articles': 0
        },
        'transfer_rates': {}
    }

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Aggregate GA4 analytics - FIXED')
    parser.add_argument('--days', type=int, default=30)
    parser.add_argument('--output', '-o', help='Output JSON file')
    parser.add_argument('--pretty', action='store_true')
    
    args = parser.parse_args()
    
    data = aggregate_ga4_data(args.days)
    
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
