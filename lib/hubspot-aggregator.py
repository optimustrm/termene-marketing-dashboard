#!/usr/bin/env python3
"""
HubSpot CRM Aggregator
Aggregates signups, revenue, MRR, and cohort data from HubSpot
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

def load_env():
    """Load HubSpot token from ~/.openclaw/.env"""
    env_path = Path.home() / '.openclaw' / '.env'
    token = None
    
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.startswith('HUBSPOT_PRIVATE_APP_ACCES_TOKEN='):
                    token = line.split('=', 1)[1].strip().strip('"').strip("'")
                    break
    
    if not token:
        print("ERROR: HUBSPOT_PRIVATE_APP_ACCES_TOKEN not found in ~/.openclaw/.env", file=sys.stderr)
        sys.exit(1)
    
    return token

def hubspot_api(endpoint, token, params=None, method='GET'):
    """Make HubSpot API request"""
    base_url = 'https://api.hubapi.com'
    url = f"{base_url}{endpoint}"
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=params)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"HubSpot API error: {e}", file=sys.stderr)
        return None

def get_new_signups(token, days=30):
    """Get new signups (contacts created) in the last N days"""
    
    # Calculate timestamp for N days ago (in milliseconds)
    cutoff_date = datetime.now() - timedelta(days=days)
    cutoff_timestamp = int(cutoff_date.timestamp() * 1000)
    
    # Search for contacts created after cutoff
    search_payload = {
        'filterGroups': [{
            'filters': [{
                'propertyName': 'createdate',
                'operator': 'GTE',
                'value': str(cutoff_timestamp)
            }]
        }],
        'properties': ['email', 'createdate', 'lifecyclestage'],
        'limit': 100
    }
    
    data = hubspot_api('/crm/v3/objects/contacts/search', token, search_payload, method='POST')
    
    if not data:
        return {'total': 0, 'signups_by_date': {}}
    
    total = data.get('total', 0)
    contacts = data.get('results', [])
    
    # Group by date
    signups_by_date = defaultdict(int)
    signups_by_stage = defaultdict(int)
    
    for contact in contacts:
        props = contact.get('properties', {})
        created = props.get('createdate', '')
        stage = props.get('lifecyclestage', 'unknown')
        
        # Parse date
        if created:
            date = created.split('T')[0]  # YYYY-MM-DD
            signups_by_date[date] += 1
            signups_by_stage[stage] += 1
    
    return {
        'total': total,
        'signups_by_date': dict(signups_by_date),
        'signups_by_stage': dict(signups_by_stage)
    }

def get_paid_accounts(token):
    """Get paid accounts (lifecyclestage = customer)"""
    
    search_payload = {
        'filterGroups': [{
            'filters': [{
                'propertyName': 'lifecyclestage',
                'operator': 'EQ',
                'value': 'customer'
            }]
        }],
        'properties': ['email', 'createdate', 'lifecyclestage'],
        'limit': 1  # Just need total count
    }
    
    data = hubspot_api('/crm/v3/objects/contacts/search', token, search_payload, method='POST')
    
    if not data:
        return {'total': 0}
    
    return {
        'total': data.get('total', 0)
    }

def get_revenue_mrr(token, days=30):
    """Get revenue and MRR from Deals"""
    
    # Calculate timestamp for N days ago
    cutoff_date = datetime.now() - timedelta(days=days)
    cutoff_timestamp = int(cutoff_date.timestamp() * 1000)
    
    # Search for deals closed in last N days
    search_payload = {
        'filterGroups': [{
            'filters': [{
                'propertyName': 'closedate',
                'operator': 'GTE',
                'value': str(cutoff_timestamp)
            }]
        }],
        'properties': ['dealname', 'amount', 'hs_mrr', 'closedate', 'dealstage'],
        'limit': 100
    }
    
    data = hubspot_api('/crm/v3/objects/deals/search', token, search_payload, method='POST')
    
    if not data:
        return {
            'total_revenue': 0,
            'total_mrr': 0,
            'deals_count': 0
        }
    
    deals = data.get('results', [])
    
    total_revenue = 0
    total_mrr = 0
    
    for deal in deals:
        props = deal.get('properties', {})
        amount = float(props.get('amount', 0) or 0)
        mrr = float(props.get('hs_mrr', 0) or 0)
        
        total_revenue += amount
        total_mrr += mrr
    
    return {
        'total_revenue': total_revenue,
        'total_mrr': total_mrr,
        'deals_count': len(deals),
        'avg_deal_size': total_revenue / len(deals) if deals else 0
    }

def get_cohort_analysis(token, months=12):
    """Get cohort analysis by signup month"""
    
    cohorts = {}
    
    for month_offset in range(months):
        # Calculate month start/end
        target_date = datetime.now() - timedelta(days=30 * month_offset)
        month_start = target_date.replace(day=1)
        
        # Calculate next month
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1)
        
        start_ts = int(month_start.timestamp() * 1000)
        end_ts = int(month_end.timestamp() * 1000)
        
        # Query contacts created in this month
        search_payload = {
            'filterGroups': [{
                'filters': [
                    {
                        'propertyName': 'createdate',
                        'operator': 'GTE',
                        'value': str(start_ts)
                    },
                    {
                        'propertyName': 'createdate',
                        'operator': 'LT',
                        'value': str(end_ts)
                    }
                ]
            }],
            'properties': ['createdate', 'lifecyclestage'],
            'limit': 1
        }
        
        data = hubspot_api('/crm/v3/objects/contacts/search', token, search_payload, method='POST')
        
        if data:
            cohort_key = month_start.strftime('%Y-%m')
            cohorts[cohort_key] = {
                'total_signups': data.get('total', 0),
                'month': cohort_key
            }
    
    return cohorts

def get_revenue_attribution(token, days=30):
    """Get revenue attribution by source"""
    
    # TODO: Query contacts with associated deals and Original Source property
    # This requires joining Contacts (Original Source) with Deals (Amount)
    
    return {
        'note': 'Revenue attribution by source not yet implemented',
        'sources': {}
    }

def aggregate_hubspot_data(days=30):
    """
    Main aggregation function
    Returns: Signups, revenue, MRR, cohorts, attribution
    """
    
    print(f"💼 Aggregating HubSpot data (last {days} days)...", file=sys.stderr)
    
    token = load_env()
    
    # New signups
    print("  - Fetching new signups...", file=sys.stderr)
    signups = get_new_signups(token, days)
    
    # Paid accounts
    print("  - Fetching paid accounts...", file=sys.stderr)
    paid_accounts = get_paid_accounts(token)
    
    # Revenue & MRR
    print("  - Fetching revenue & MRR...", file=sys.stderr)
    revenue = get_revenue_mrr(token, days)
    
    # Cohort analysis
    print("  - Fetching cohort data...", file=sys.stderr)
    cohorts = get_cohort_analysis(token, months=12)
    
    # Attribution
    print("  - Fetching revenue attribution...", file=sys.stderr)
    attribution = get_revenue_attribution(token, days)
    
    print("  ✅ HubSpot aggregation complete", file=sys.stderr)
    
    return {
        'generated_at': datetime.now().isoformat(),
        'period_days': days,
        'signups': signups,
        'paid_accounts': paid_accounts,
        'revenue': revenue,
        'cohorts': cohorts,
        'attribution': attribution,
        'summary': {
            'new_signups': signups['total'],
            'total_paid_accounts': paid_accounts['total'],
            'total_revenue_ron': revenue['total_revenue'],
            'total_mrr_ron': revenue['total_mrr'],
            'deals_closed': revenue['deals_count']
        }
    }

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Aggregate HubSpot CRM data')
    parser.add_argument('--days', type=int, default=30,
                        help='Number of days for historical data (default: 30)')
    parser.add_argument('--output', '-o', help='Output JSON file (default: stdout)')
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON')
    
    args = parser.parse_args()
    
    # Aggregate data
    data = aggregate_hubspot_data(args.days)
    
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
