# US Big Tech: Headcount vs. Per-Employee Efficiency (2021–2025)

An interactive connected scatter plot comparing **7 major US tech companies** across headcount and per-employee financial efficiency from 2021 to 2025 — inspired by a similar visualization for Chinese internet companies published by LatePost / 晚点小数据.

**Data is fetched live from the [SEC EDGAR XBRL API](https://www.sec.gov/edgar/sec-api-documentation) — no third-party aggregators, straight from primary 10-K filings.**

## Live demo

Open `index.html` locally (see instructions below), or enable GitHub Pages for a public URL.

## What the chart shows

Each dot = one company in one year.

| Axis | Meaning |
|---|---|
| X | Total headcount (log scale, from 10-K filings) |
| Y | Annual revenue **or** operating income ÷ headcount (USD thousands) |

Lines connect each company's dots chronologically (2021 → 2025), revealing how both size and efficiency evolved together.

## Data source: SEC EDGAR XBRL API

All data is fetched at runtime directly from `data.sec.gov` — the SEC's official machine-readable API. No API key required.

| Company | Ticker | CIK | FY End | EDGAR filings |
|---|---|---|---|---|
| Nvidia | NVDA | 1045810 | January | [10-Ks](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001045810&type=10-K) |
| Meta | META | 1326801 | December | [10-Ks](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001326801&type=10-K) |
| Microsoft | MSFT | 789019 | June | [10-Ks](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000789019&type=10-K) |
| Alphabet | GOOGL | 1652044 | December | [10-Ks](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001652044&type=10-K) |
| Apple | AAPL | 320193 | September | [10-Ks](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000320193&type=10-K) |
| Netflix | NFLX | 1065280 | December | [10-Ks](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001065280&type=10-K) |
| Amazon | AMZN | 1018724 | December | [10-Ks](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001018724&type=10-K) |

### XBRL concepts used

```
Revenue:          us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax
                  us-gaap/Revenues  (fallback)
Operating income: us-gaap/OperatingIncomeLoss
Headcount:        dei/EntityNumberOfEmployees
```

The chart tries each tag in order and uses the first one that returns 10-K annual data for the target fiscal year.

## Key stories in the data

| Company | Story |
|---|---|
| **Nvidia** | The sharpest trajectory in the dataset. Revenue/employee went from ~$850K (FY2021) to ~$3.6M (FY2025) as AI chip demand exploded — on only modest headcount growth. |
| **Meta** | The "Year of Efficiency" is visible: headcount dropped 22% from 2022→2023 while revenue recovered, sending the line sharply up-and-left. |
| **Apple** | Remarkably stable — high absolute efficiency (~$2.4M revenue/employee) with almost no headcount swings across five years. |
| **Amazon** | Far right on the X-axis (~1.5M+ employees including part-time). Low per-employee figures reflect the cost structure of physical logistics, not just software. |
| **Netflix** | Small, stable team (11K→16K) generating steady per-employee growth — a lean software-company efficiency profile. |
| **Alphabet & Microsoft** | Steady climbers with controlled headcount. Both crossed $1M revenue/employee by 2022–2023. |

## Comparison: Chinese internet companies

Inspired by an equivalent chart for Chinese tech (Pinduoduo, Tencent, Alibaba, Meituan, Baidu, NetEase, Kuaishou, JD) from LatePost. Key cross-market parallels:

- **Pinduoduo ↔ Nvidia** — the outlier in each market; tiny team, explosive per-employee productivity
- **JD.com ↔ Amazon** — massive logistics headcount depresses per-employee metrics despite large revenues
- US companies generally operate at higher absolute per-employee revenue, partly reflecting higher prevailing compensation

## How to run locally

```bash
git clone https://github.com/<your-username>/tech-efficiency-analysis.git
cd tech-efficiency-analysis

# Option 1 — Python (recommended, avoids CORS issues)
python -m http.server 8000
# then open http://localhost:8000

# Option 2 — Node
npx serve .

# Option 3 — Just open index.html in Chrome/Firefox directly
# (CORS may block the SEC API on some setups; use a local server if you see errors)
```

## GitHub Pages (live public URL)

1. Push to GitHub
2. Repo Settings → Pages → Deploy from branch → `main` / root
3. Your chart will be live at `https://<username>.github.io/tech-efficiency-analysis/`

Since the chart fetches from `data.sec.gov` at page load, GitHub Pages always serves the most current SEC data — no rebuild needed when companies file new 10-Ks.

## Repo structure

```
tech-efficiency-analysis/
├── index.html                          # Self-contained interactive chart
├── data/
│   └── us_tech_efficiency_2021_2025.csv   # Snapshot of data (cross-reference)
└── README.md
```

## Notes

- **Amazon headcount** includes part-time workers (~25%), which depresses per-employee figures vs. software-only peers
- **Fiscal year labels** follow each company's reported FY: Apple FY2024 ended Sep 2024, Microsoft FY2024 ended Jun 2024, Nvidia FY2025 ended Jan 2025
- The SEC EDGAR API enforces **10 requests/second** rate limit; the chart fetches ~21 concepts sequentially to stay well under this
- The `User-Agent` header is required by the SEC — it is set to a generic research identifier in the code; update it to your own name/email per [SEC guidelines](https://www.sec.gov/os/accessing-edgar-data)

## License

Code: MIT. Data: public SEC EDGAR filings (public domain).
