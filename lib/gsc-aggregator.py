#!/usr/bin/env python3
"""
Google Search Console Aggregator
Aggregates SEO data: impressions, clicks, rankings, keywords
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Paths
WORKSPACE = Path.home() / '.openclaw' / 'workspace'
GA4_SKILL = WORKSPACE / 'skills' / 'google-analytics' / 'scripts'

def run_bash_script(script_path, args=''):
    """Execute bash script and return output"""
    try:
        cmd = f"bash {script_path} {args}"
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        # Try to parse as JSON, fallback to text
        try:
            return json.loads(result.stdout) if result.stdout.strip() else {}
        except json.JSONDecodeError:
            return {'raw_output': result.stdout}
    except subprocess.CalledProcessError as e:
        print(f"ERROR running {script_path.name}: {e.stderr}", file=sys.stderr)
        return None

def get_search_console_overview(days=30):
    """Get overall Search Console metrics"""
    script = GA4_SKILL / 'search-console-bulk-2026.sh'
    # TODO: Adjust parameters based on actual script
    data = run_bash_script(script, f"{days}")
    
    if not data or 'raw_output' in data:
        return {
            'note': 'GSC data unavailable',
            'impressions': 0,
            'clicks': 0,
            'ctr': 0.0,
            'avg_position': 0.0
        }
    
    return {
        'impressions': data.get('impressions', 0),
        'clicks': data.get('clicks', 0),
        'ctr': data.get('ctr', 0.0),
        'avg_position': data.get('avg_position', 0.0)
    }

def get_top_queries(days=30, limit=50):
    """Get top search queries"""
    script = GA4_SKILL / 'search-console-queries-2026.sh'
    data = run_bash_script(script, f"{days} {limit}")
    
    if not data or 'raw_output' in data:
        return {
            'note': 'Top queries data unavailable',
            'queries': []
        }
    
    return {
        'queries': data.get('queries', [])[:limit]
    }

def get_article_seo_performance(days=30):
    """Get SEO performance for articles"""
    # TODO: Filter Search Console data for /articole/* URLs
    
    return {
        'note': 'Article SEO data will be filtered from main GSC data',
        'articles': []
    }

def aggregate_gsc_data(days=30):
    """
    Main aggregation function
    Returns: GSC overview, top queries, article SEO
    """
    
    print(f"🔍 Aggregating Google Search Console data (last {days} days)...", file=sys.stderr)
    
    # Overview
    print("  - Fetching GSC overview...", file=sys.stderr)
    overview = get_search_console_overview(days)
    
    # Top queries
    print("  - Fetching top queries...", file=sys.stderr)
    queries = get_top_queries(days, limit=50)
    
    # Article SEO
    print("  - Fetching article SEO data...", file=sys.stderr)
    articles_seo = get_article_seo_performance(days)
    
    print("  ✅ GSC aggregation complete", file=sys.stderr)
    
    return {
        'generated_at': datetime.now().isoformat(),
        'period_days': days,
        'overview': overview,
        'top_queries': queries,
        'articles_seo': articles_seo,
        'summary': {
            'total_impressions': overview.get('impressions', 0),
            'total_clicks': overview.get('clicks', 0),
            'avg_ctr': overview.get('ctr', 0.0),
            'avg_position': overview.get('avg_position', 0.0)
        }
    }

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Aggregate Google Search Console data')
    parser.add_argument('--days', type=int, default=30,
                        help='Number of days for historical data (default: 30)')
    parser.add_argument('--output', '-o', help='Output JSON file (default: stdout)')
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON')
    
    args = parser.parse_args()
    
    # Aggregate data
    data = aggregate_gsc_data(args.days)
    
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
