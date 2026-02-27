# Marketing Intelligence Dashboard - Implementation Plan
**Start Date:** 2026-02-26  
**Target:** FAZA 1 (70% Coverage) - 1 săptămână  
**Status:** 🚀 IN PROGRESS

---

## 🎯 SCOPE FAZA 1

### ✅ CE LIVRĂM:

**PASUL 1 - Social Media & Content Footprint (70%):**
- ✅ Facebook Analytics Complete (Meta Social skill)
- ✅ Instagram Analytics Complete (Meta Social skill)
- ✅ YouTube Analytics Complete (YouTube Analytics skill)
- ✅ Website Traffic Complete (Google Analytics 4 skill)
- ✅ Articole Performance Complete (GA4 + GSC)
- ✅ SEO Performance Complete (GSC skill)
- ✅ Transfer Rates pentru Facebook, Instagram, YouTube, Organic
- ⚠️ LinkedIn & TikTok: doar trafic → site (fără native metrics)

**PASUL 2 - Product Traffic Dashboard (80%):**
- ✅ Metrici per pagină de produs (GA4)
- ✅ Matrice conversie Social/Website → Produs
- ✅ Attribution First-Touch & Last-Touch
- ❌ Multi-Touch Attribution (necesită BigQuery - FAZA 2)

**PASUL 3 - Paid Accounts & Revenue (40%):**
- ✅ New Signups tracking (HubSpot)
- ✅ Revenue & MRR reporting (HubSpot Deals)
- ✅ Cohort Analysis by signup date
- ✅ Revenue Attribution by channel
- ❌ DAU/WAU/MAU (necesită clarificare source - FAZA 2)
- ⚠️ CAC (necesită ad spend input manual)

---

## 📁 STRUCTURĂ SKILL

```
skills/marketing-intelligence-dashboard/
├── SKILL.md                          # Documentație master
├── IMPLEMENTATION-PLAN.md            # Acest fișier
├── scripts/
│   ├── pasul1-social-content.sh      # Agregare PASUL 1
│   ├── pasul2-product-traffic.sh     # Agregare PASUL 2
│   ├── pasul3-revenue.sh             # Agregare PASUL 3
│   ├── generate-full-report.sh       # Raport complet
│   └── dashboard-summary.sh          # Summary quick view
├── lib/
│   ├── meta-social-aggregator.py     # Facebook + Instagram
│   ├── youtube-aggregator.py         # YouTube data
│   ├── ga4-aggregator.py             # Google Analytics 4
│   ├── gsc-aggregator.py             # Google Search Console
│   ├── hubspot-aggregator.py         # HubSpot CRM
│   └── sankey-generator.py           # Sankey diagram data
├── output/
│   ├── pasul1-social-content.json    # PASUL 1 output
│   ├── pasul2-product-traffic.json   # PASUL 2 output
│   ├── pasul3-revenue.json           # PASUL 3 output
│   └── full-dashboard-report.json    # Combined report
├── config/
│   └── products.json                 # Lista produse Termene.ro
└── examples/
    ├── weekly-report.sh              # Weekly automated report
    └── monthly-deep-dive.sh          # Monthly analysis
```

---

## 🛠️ DEVELOPMENT STEPS

### STEP 1: Setup Structure (NOW) ✅
- [x] Create skill directory
- [x] Create implementation plan
- [ ] Create config files
- [ ] Create output directories

### STEP 2: Data Aggregators (Day 1-2)
- [ ] **meta-social-aggregator.py** - Facebook + Instagram
  - Followers, Reach, Engagement per post
  - Top performing posts
  - Transfer rate to site (+ GA4)
- [ ] **youtube-aggregator.py** - YouTube
  - Subscribers, Views, Watch Time
  - Video performance
  - Transfer rate to site (+ GA4)
- [ ] **ga4-aggregator.py** - Website Traffic
  - Sessions, Users, Pageviews
  - Traffic by source (Social breakdown)
  - Article performance
  - Product page performance
- [ ] **gsc-aggregator.py** - SEO
  - Impressions, Clicks, CTR
  - Keyword rankings
  - Organic traffic to articles
- [ ] **hubspot-aggregator.py** - CRM & Revenue
  - New signups
  - Paid accounts
  - Revenue, MRR
  - Cohort analysis

### STEP 3: Main Scripts (Day 3-4)
- [ ] **pasul1-social-content.sh**
  - Aggregate Facebook, Instagram, YouTube
  - Aggregate GA4 website traffic
  - Aggregate GSC SEO data
  - Calculate transfer rates
  - Generate JSON report
- [ ] **pasul2-product-traffic.sh**
  - Aggregate GA4 product pages
  - Calculate source → product matrix
  - Calculate conversion rates
  - Attribution models (First/Last Touch)
  - Generate JSON report
- [ ] **pasul3-revenue.sh**
  - Aggregate HubSpot signups & revenue
  - Calculate MRR & growth
  - Cohort analysis
  - Attribution by source
  - Generate JSON report

### STEP 4: Sankey Diagram Generator (Day 4-5)
- [ ] **sankey-generator.py**
  - Parse PASUL 1, 2, 3 outputs
  - Build flow: Social → Site → Products → Signups → Paid
  - Generate Sankey JSON for visualization
  - Identify bottlenecks (where flow "thins")

### STEP 5: Master Report Generator (Day 5-6)
- [ ] **generate-full-report.sh**
  - Run all 3 pasul scripts
  - Aggregate outputs
  - Generate Sankey diagram
  - Create markdown summary
  - Create JSON for dashboard tools (Grafana/Metabase)

### STEP 6: Quick View & Examples (Day 6-7)
- [ ] **dashboard-summary.sh**
  - Hero metrics display
  - Key insights
  - Week-over-week changes
- [ ] **weekly-report.sh**
  - Automated weekly run (cron)
  - Slack notification with summary
- [ ] **monthly-deep-dive.sh**
  - Extended analysis
  - Month-over-month trends

### STEP 7: Testing & Documentation (Day 7)
- [ ] Test all scripts with real data
- [ ] Write SKILL.md documentation
- [ ] Create usage examples
- [ ] Document limitations (LinkedIn/TikTok/DAU)

---

## 🔧 DEPENDENCIES

### Existing Skills (READY):
- ✅ `meta-social/` - Facebook + Instagram
- ✅ `youtube-analytics/` - YouTube
- ✅ `google-analytics/` - GA4 (verificăm dacă există, altfel creăm)
- ⚠️ GSC skill? (verificăm)
- ✅ HubSpot API access (verified)

### To Create:
- [ ] Google Analytics 4 skill (dacă nu există)
- [ ] Google Search Console skill (dacă nu există complet)

### External:
- Python 3.8+
- jq, curl
- Google Analytics API credentials
- Meta Graph API credentials
- YouTube Analytics API credentials
- HubSpot API token

---

## 📊 OUTPUT FORMAT

### JSON Structure:

```json
{
  "generated_at": "2026-02-26T23:45:00Z",
  "period": {
    "start": "2026-02-01",
    "end": "2026-02-26"
  },
  "pasul1": {
    "social_media": {
      "facebook": { ... },
      "instagram": { ... },
      "youtube": { ... },
      "linkedin": { "reach": null, "sessions_to_site": 1234 },
      "tiktok": { "views": null, "sessions_to_site": 567 }
    },
    "website": { ... },
    "articles": { ... },
    "transfer_rates": { ... }
  },
  "pasul2": {
    "products": [ ... ],
    "conversion_matrix": { ... },
    "attribution": { ... }
  },
  "pasul3": {
    "signups": { ... },
    "revenue": { ... },
    "cohorts": { ... },
    "attribution": { ... }
  },
  "sankey": {
    "nodes": [ ... ],
    "links": [ ... ]
  },
  "insights": [
    "Top performing channel: Instagram (transfer rate 2.3%)",
    "Bottleneck identified: Product pages → Signups (1.2% conversion)",
    "..."
  ]
}
```

---

## ⚠️ LIMITATIONS FAZA 1

**LinkedIn:**
- ❌ No native metrics (followers, reach, engagement)
- ✅ Only traffic to site from GA4

**TikTok:**
- ❌ No native metrics (followers, views, engagement)
- ✅ Only traffic to site from GA4

**DAU/WAU/MAU:**
- ❌ Not available (source unclear)
- 💡 Placeholder in report with note "Data source needed"

**Multi-Touch Attribution:**
- ❌ Not available (requires BigQuery export)
- ✅ First-Touch & Last-Touch only

**CAC:**
- ⚠️ Structure ready, requires manual ad spend input

---

## 🚀 NEXT STEPS (POST-FAZA 1)

**FAZA 2 (Completitudine 90%):**
1. LinkedIn Marketing API integration
2. TikTok for Business API integration
3. DAU/WAU/MAU tracking (after source clarification)
4. GA4 BigQuery export for Multi-Touch Attribution

**FAZA 3 (Automation & Alerts):**
1. Automated daily/weekly reports
2. Slack/Email notifications
3. Anomaly detection (sudden drops/spikes)
4. Benchmark tracking over time

---

## 📅 TIMELINE

| Day | Task | Status |
|-----|------|--------|
| Day 1 | Setup + Meta Social aggregator | 🔵 TODO |
| Day 2 | YouTube + GA4 aggregators | 🔵 TODO |
| Day 3 | GSC + HubSpot aggregators | 🔵 TODO |
| Day 4 | PASUL 1 & 2 scripts | 🔵 TODO |
| Day 5 | PASUL 3 script + Sankey | 🔵 TODO |
| Day 6 | Full report generator + examples | 🔵 TODO |
| Day 7 | Testing + documentation | 🔵 TODO |

**Target Completion:** 2026-03-05 (1 săptămână)

---

**Status:** 🚀 Development started 2026-02-26 23:45  
**Next:** Create directory structure + config files
