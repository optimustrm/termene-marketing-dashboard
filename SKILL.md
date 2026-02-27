---
name: marketing-intelligence-dashboard
description: Complete marketing intelligence dashboard for Termene.ro - tracks social media performance, website traffic, article engagement, product page conversions, revenue, and full funnel from Social → Paid Accounts. Provides actionable insights for marketing optimization.
---

# Marketing Intelligence Dashboard

**Complete analytics system tracking the full marketing funnel: Social Media → Website → Products → Signups → Revenue**

## 📊 What It Does

Aggregates data from:
- 📱 **Social Media**: Facebook, Instagram, YouTube (+ LinkedIn/TikTok traffic via GA4)
- 🌐 **Website**: GA4 traffic, article performance, product pages
- 🔍 **SEO**: Google Search Console (impressions, clicks, rankings)
- 💼 **Revenue**: HubSpot CRM (signups, MRR, cohorts)

Generates:
- **PASUL 1**: Social Media & Content Footprint Dashboard
- **PASUL 2**: Product Traffic Dashboard (Source → Product conversion matrix)
- **PASUL 3**: Paid Accounts & Revenue Dashboard
- **Sankey Diagram**: Visual funnel flow from reach to revenue

---

## 🚀 Quick Start

### Generate Complete Report (All 3 Steps)

```bash
cd ~/.openclaw/workspace/skills/marketing-intelligence-dashboard

# Run all 3 pasul scripts
./scripts/pasul1-social-content.sh --days 30
./scripts/pasul2-product-traffic.sh --days 30
./scripts/pasul3-revenue.sh --days 30

# Or use the master script (coming soon)
./scripts/generate-full-report.sh --days 30
```

### PASUL 1: Social Media & Content Footprint

```bash
./scripts/pasul1-social-content.sh --days 30

# Output: output/pasul1-social-content.json
```

**Includes:**
- Facebook & Instagram analytics (reach, engagement, followers)
- YouTube analytics (subscribers, views, watch time)
- Website traffic breakdown by source
- Social → Site transfer rates
- Article performance (top 10, pageviews, time on page)
- SEO performance (impressions, clicks, CTR)

---

## 📁 Structure

```
marketing-intelligence-dashboard/
├── SKILL.md                          # This file
├── IMPLEMENTATION-PLAN.md            # Development roadmap
├── scripts/
│   ├── pasul1-social-content.sh      # ✅ PASUL 1 aggregator
│   ├── pasul2-product-traffic.sh     # 🔵 TODO
│   ├── pasul3-revenue.sh             # 🔵 TODO
│   └── generate-full-report.sh       # 🔵 TODO
├── lib/
│   ├── meta-social-aggregator.py     # ✅ Facebook + Instagram
│   ├── youtube-aggregator.py         # ✅ YouTube
│   ├── ga4-aggregator.py             # ✅ Website + Articles + Products
│   ├── hubspot-aggregator.py         # ✅ HubSpot CRM
│   ├── gsc-aggregator.py             # ✅ Google Search Console
│   └── sankey-generator.py           # 🔵 TODO
├── output/                           # Generated reports
├── config/
│   └── products.json                 # ✅ Product list configuration
└── examples/                         # Usage examples
```

---

## 🔧 Prerequisites

### API Credentials (in `~/.openclaw/.env`)

```bash
# Meta (Facebook + Instagram)
FACEBOOK_PAGE_ID=...
FACEBOOK_PAGE_ACCESS_TOKEN=...
INSTAGRAM_BUSINESS_ACCOUNT_ID=...

# Google (YouTube + GA4 + GSC)
YOUTUBE_API_KEY=...
# GA4 credentials (TODO: document)
# GSC credentials (TODO: document)

# HubSpot
HUBSPOT_PRIVATE_APP_ACCES_TOKEN=...
```

### Existing Skills (Dependencies)
- ✅ `meta-social/` - Facebook & Instagram automation
- ✅ `youtube-analytics/` - YouTube data
- ✅ `google-analytics/` - GA4 (needs verification)
- ✅ HubSpot API access (verified working)

---

## 📊 Output Format

### PASUL 1 JSON Structure

```json
{
  "generated_at": "2026-02-26T23:45:00Z",
  "period_days": 30,
  "pasul": 1,
  "name": "Social Media & Content Footprint Dashboard",
  "social_media": {
    "facebook": { "page_impressions": X, "page_engaged_users": X },
    "instagram": { "followers": X, "reach": X, "impressions": X },
    "youtube": { "subscribers": X, "total_views": X, "total_videos": X },
    "linkedin": { "note": "Native metrics unavailable", "sessions_to_site": X },
    "tiktok": { "note": "Native metrics unavailable", "sessions_to_site": X }
  },
  "website_traffic": {
    "sessions": X,
    "users": X,
    "pageviews": X,
    "bounce_rate": X,
    "avg_session_duration": X
  },
  "social_breakdown": {
    "linkedin": { "sessions": X, "bounce_rate": X },
    "facebook": { "sessions": X, "bounce_rate": X },
    "instagram": { "sessions": X, "bounce_rate": X },
    "tiktok": { "sessions": X, "bounce_rate": X },
    "youtube": { "sessions": X, "bounce_rate": X }
  },
  "articles": {
    "total_articles": X,
    "total_pageviews": X,
    "top_articles": [ ... ]
  },
  "seo": {
    "total_impressions": X,
    "total_clicks": X,
    "avg_ctr": X,
    "avg_position": X
  },
  "transfer_rates": {
    "facebook": X.XX,
    "instagram": X.XX,
    "youtube": X.XX,
    "linkedin": { "note": "...", "sessions_to_site": X },
    "tiktok": { "note": "...", "sessions_to_site": X }
  },
  "summary": {
    "total_social_followers": X,
    "total_social_reach": X,
    "total_website_sessions": X,
    "total_article_pageviews": X
  }
}
```

---

## ⚙️ Configuration

### Products List (`config/products.json`)

Define product pages to track in PASUL 2:

```json
{
  "products": [
    {
      "id": "verifica-firme-ro",
      "name": "Verifică Firme - România",
      "category": "company_verification",
      "url_pattern": "/verifica-firme-romania*",
      "ga4_path_filter": "pagePath=~/verifica.*romania"
    },
    ...
  ]
}
```

**Note:** URL patterns are placeholders - update after analyzing real site structure.

---

## 🎯 Use Cases

### Weekly Marketing Review

```bash
# Generate last 7 days report
./scripts/pasul1-social-content.sh --days 7 --output reports/weekly-$(date +%Y-%m-%d).json
```

### Monthly Deep Dive

```bash
# Full 30-day analysis
./scripts/generate-full-report.sh --days 30
```

### Compare Weeks

```bash
# Week 1
./scripts/pasul1-social-content.sh --days 7 --output week1.json

# Week 2 (7 days ago)
# TODO: Add date range support
```

---

## ⚠️ Limitations (FAZA 1 - 70% Coverage)

### LinkedIn
- ❌ No native metrics (followers, reach, engagement)
- ✅ Only traffic to site from GA4

### TikTok
- ❌ No native metrics (followers, views, engagement)
- ✅ Only traffic to site from GA4

### DAU/WAU/MAU
- ❌ Not available (source unclear)
- 💡 Placeholder in report with note "Data source needed"

### Multi-Touch Attribution
- ❌ Not available (requires BigQuery export)
- ✅ First-Touch & Last-Touch only

### CAC Calculation
- ⚠️ Structure ready, requires manual ad spend input

**For 100% coverage:** See `IMPLEMENTATION-PLAN.md` FAZA 2 (LinkedIn API, TikTok API, DAU tracking)

---

## 🔄 Automation

### Daily Reports (Cron)

```bash
# Add to crontab
0 9 * * * cd ~/.openclaw/workspace/skills/marketing-intelligence-dashboard && ./scripts/pasul1-social-content.sh --days 1 --output output/daily-$(date +\%Y-\%m-\%d).json
```

### Weekly Slack Notification

```bash
# TODO: Integrate with OpenClaw cron + Slack
```

---

## 🐛 Troubleshooting

### "Instagram insights failed"
- Check `FACEBOOK_PAGE_ACCESS_TOKEN` in `~/.openclaw/.env`
- Verify token has `instagram_basic`, `instagram_manage_insights` permissions
- Check Instagram Business Account is linked to Facebook Page

### "HubSpot API error"
- Verify `HUBSPOT_PRIVATE_APP_ACCES_TOKEN` in `~/.openclaw/.env`
- Check token has `crm.objects.contacts.read`, `crm.objects.deals.read` scopes

### "GA4 data unavailable"
- TODO: Document GA4 setup (service account or OAuth)
- Check Google Analytics skill configuration

---

## 📈 Roadmap

### ✅ FAZA 1 (Current - 70% Coverage)
- [x] Meta Social aggregator (Facebook + Instagram)
- [x] YouTube aggregator
- [x] GA4 aggregator (Website + Articles)
- [x] HubSpot aggregator (Revenue + Signups)
- [x] GSC aggregator (SEO)
- [x] PASUL 1 script
- [ ] PASUL 2 script (Product Traffic)
- [ ] PASUL 3 script (Revenue)
- [ ] Sankey diagram generator
- [ ] Full report generator

### 🔜 FAZA 2 (100% Coverage)
- [ ] LinkedIn Marketing API integration
- [ ] TikTok for Business API integration
- [ ] DAU/WAU/MAU tracking (source TBD)
- [ ] Multi-Touch Attribution (GA4 BigQuery)
- [ ] Ad spend tracking for CAC calculation

### 🔮 FAZA 3 (Automation & Alerts)
- [ ] Automated daily/weekly/monthly reports
- [ ] Slack/Email notifications
- [ ] Anomaly detection (sudden drops/spikes)
- [ ] Benchmark tracking over time
- [ ] Grafana/Metabase dashboard integration

---

## 🤝 Contributing

This skill is under active development. See `IMPLEMENTATION-PLAN.md` for current status and next steps.

**Current Status:** 🚀 FAZA 1 in progress (5 aggregators complete, PASUL 1 script complete)

---

## 📞 Support

For issues or questions:
1. Check `IMPLEMENTATION-PLAN.md` for known limitations
2. Review skill logs in `output/` directory
3. Test individual aggregators: `python3 lib/<aggregator>.py --help`

---

**Last Updated:** 2026-02-26  
**Version:** 0.1.0 (FAZA 1 - 70%)
