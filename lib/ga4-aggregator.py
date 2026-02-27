#!/usr/bin/env python3
"""
Google Analytics 4 Aggregator
Aggregates website traffic, article performance, and product page data
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
CONFIG_PATH = WORKSPACE / 'skills' / 'marketing-intelligence-dashboard' / 'config' / 'products.json'

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

def load_products_config():
    """Load products configuration"""
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️ Products config not found: {CONFIG_PATH}", file=sys.stderr)
        return {'products': []}

def get_website_overview(days=30):
    """Get overall website traffic metrics"""
    script = GA4_SKILL / 'analyze.sh'
    # TODO: Adjust parameters based on actual script
    data = run_bash_script(script, f"--days {days}")
    
    if not data:
        return {
            'error': 'Failed to fetch website overview',
            'sessions': 0,
            'users': 0,
            'pageviews': 0
        }
    
    return {
        'sessions': data.get('sessions', 0),
        'users': data.get('users', 0),
        'new_users': data.get('new_users', 0),
        'pageviews': data.get('pageviews', 0),
        'bounce_rate': data.get('bounce_rate', 0.0),
        'avg_session_duration': data.get('avg_session_duration', 0),
        'pages_per_session': data.get('pages_per_session', 0.0)
    }

def get_traffic_by_source(days=30):
    """Get traffic breakdown by source (Direct, Organic, Social, etc.)"""
    script = GA4_SKILL / 'analyze.sh'
    # TODO: Query for traffic acquisition by source
    
    # Placeholder structure
    return {
        'direct': {'sessions': 0, 'users': 0, 'bounce_rate': 0.0},
        'organic_search': {'sessions': 0, 'users': 0, 'bounce_rate': 0.0},
        'paid_search': {'sessions': 0, 'users': 0, 'bounce_rate': 0.0},
        'social': {'sessions': 0, 'users': 0, 'bounce_rate': 0.0},
        'referral': {'sessions': 0, 'users': 0, 'bounce_rate': 0.0},
        'email': {'sessions': 0, 'users': 0, 'bounce_rate': 0.0},
        'display': {'sessions': 0, 'users': 0, 'bounce_rate': 0.0}
    }

def get_social_breakdown(days=30):
    """Get detailed social media traffic breakdown"""
    # TODO: Query GA4 for social source breakdown
    # LinkedIn, Facebook, Instagram, TikTok, YouTube, Twitter
    
    return {
        'linkedin': {'sessions': 0, 'users': 0, 'bounce_rate': 0.0, 'conversion_rate': 0.0},
        'facebook': {'sessions': 0, 'users': 0, 'bounce_rate': 0.0, 'conversion_rate': 0.0},
        'instagram': {'sessions': 0, 'users': 0, 'bounce_rate': 0.0, 'conversion_rate': 0.0},
        'tiktok': {'sessions': 0, 'users': 0, 'bounce_rate': 0.0, 'conversion_rate': 0.0},
        'youtube': {'sessions': 0, 'users': 0, 'bounce_rate': 0.0, 'conversion_rate': 0.0},
        'twitter': {'sessions': 0, 'users': 0, 'bounce_rate': 0.0, 'conversion_rate': 0.0}
    }

def get_articles_performance(days=30):
    """Get article performance metrics"""
    script = GA4_SKILL / 'article-analysis-2026.py'
    # Use existing article analysis script
    data = run_bash_script(script, f"--days {days}")
    
    if not data or 'raw_output' in data:
        return {
            'note': 'Article performance unavailable',
            'total_articles': 0,
            'top_articles': []
        }
    
    return {
        'total_articles': len(data.get('articles', [])),
        'total_pageviews': sum(a.get('pageviews', 0) for a in data.get('articles', [])),
        'top_articles': data.get('top_articles', [])[:10]
    }

def get_product_pages_performance(days=30):
    """Get product pages performance based on config"""
    products_config = load_products_config()
    products = products_config.get('products', [])
    
    product_data = []
    
    for product in products:
        # TODO: Query GA4 for each product page
        # Use page-analysis.sh with product URL pattern
        script = GA4_SKILL / 'page-analysis.sh'
        
        product_data.append({
            'product_id': product['id'],
            'product_name': product['name'],
            'category': product['category'],
            'pageviews': 0,  # TODO: Get from GA4
            'unique_visitors': 0,
            'avg_time_on_page': 0,
            'bounce_rate': 0.0,
            'cta_clicks': 0,  # TODO: Get from GA4 events
            'form_starts': 0,
            'form_completions': 0
        })
    
    return {
        'products': product_data,
        'total_product_pageviews': sum(p['pageviews'] for p in product_data)
    }

def calculate_transfer_rates(social_data, ga4_social_traffic):
    """
    Calculate Social → Site transfer rates
    transfer_rate = (GA4 sessions from social) / (Social platform reach) × 100
    """
    
    transfer_rates = {}
    
    # Facebook
    fb_reach = social_data.get('facebook', {}).get('page_impressions', 0)
    fb_sessions = ga4_social_traffic.get('facebook', {}).get('sessions', 0)
    transfer_rates['facebook'] = round((fb_sessions / fb_reach * 100), 2) if fb_reach > 0 else 0.0
    
    # Instagram
    ig_reach = social_data.get('instagram', {}).get('reach', 0)
    ig_sessions = ga4_social_traffic.get('instagram', {}).get('sessions', 0)
    transfer_rates['instagram'] = round((ig_sessions / ig_reach * 100), 2) if ig_reach > 0 else 0.0
    
    # YouTube
    yt_views = social_data.get('youtube', {}).get('total_views', 0)
    yt_sessions = ga4_social_traffic.get('youtube', {}).get('sessions', 0)
    transfer_rates['youtube'] = round((yt_sessions / yt_views * 100), 2) if yt_views > 0 else 0.0
    
    # LinkedIn & TikTok (GA4 only, no native reach data)
    transfer_rates['linkedin'] = {
        'note': 'Native reach data not available (LinkedIn API needed)',
        'sessions_to_site': ga4_social_traffic.get('linkedin', {}).get('sessions', 0)
    }
    
    transfer_rates['tiktok'] = {
        'note': 'Native views data not available (TikTok API needed)',
        'sessions_to_site': ga4_social_traffic.get('tiktok', {}).get('sessions', 0)
    }
    
    return transfer_rates

def aggregate_ga4_data(days=30, social_data=None, youtube_data=None):
    """
    Main aggregation function
    Returns: Website traffic, articles, products, transfer rates
    """
    
    print(f"🌐 Aggregating GA4 data (last {days} days)...", file=sys.stderr)
    
    # Website overview
    print("  - Fetching website overview...", file=sys.stderr)
    overview = get_website_overview(days)
    
    # Traffic by source
    print("  - Fetching traffic by source...", file=sys.stderr)
    traffic_sources = get_traffic_by_source(days)
    
    # Social breakdown
    print("  - Fetching social media breakdown...", file=sys.stderr)
    social_breakdown = get_social_breakdown(days)
    
    # Articles performance
    print("  - Fetching articles performance...", file=sys.stderr)
    articles = get_articles_performance(days)
    
    # Product pages
    print("  - Fetching product pages performance...", file=sys.stderr)
    products = get_product_pages_performance(days)
    
    # Transfer rates (if social data provided)
    transfer_rates = {}
    if social_data and youtube_data:
        print("  - Calculating transfer rates...", file=sys.stderr)
        combined_social = {
            'facebook': social_data.get('facebook', {}),
            'instagram': social_data.get('instagram', {}),
            'youtube': youtube_data.get('summary', {})
        }
        transfer_rates = calculate_transfer_rates(combined_social, social_breakdown)
    
    print("  ✅ GA4 aggregation complete", file=sys.stderr)
    
    return {
        'generated_at': datetime.now().isoformat(),
        'period_days': days,
        'website_overview': overview,
        'traffic_sources': traffic_sources,
        'social_breakdown': social_breakdown,
        'articles': articles,
        'products': products,
        'transfer_rates': transfer_rates
    }

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Aggregate GA4 analytics')
    parser.add_argument('--days', type=int, default=30,
                        help='Number of days for historical data (default: 30)')
    parser.add_argument('--social-data', help='Path to social data JSON (for transfer rates)')
    parser.add_argument('--youtube-data', help='Path to YouTube data JSON (for transfer rates)')
    parser.add_argument('--output', '-o', help='Output JSON file (default: stdout)')
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON')
    
    args = parser.parse_args()
    
    # Load social/youtube data if provided
    social_data = None
    youtube_data = None
    
    if args.social_data:
        with open(args.social_data) as f:
            social_data = json.load(f)
    
    if args.youtube_data:
        with open(args.youtube_data) as f:
            youtube_data = json.load(f)
    
    # Aggregate data
    data = aggregate_ga4_data(args.days, social_data, youtube_data)
    
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
