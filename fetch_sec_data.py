"""
fetch_sec_data.py
-----------------
Fetches revenue, operating income, and headcount from the SEC EDGAR XBRL API
for 7 major US tech companies and writes a clean CSV snapshot.

Usage:
    pip install requests
    python fetch_sec_data.py

Outputs:
    data/us_tech_efficiency_2021_2025.csv

SEC EDGAR API docs: https://www.sec.gov/edgar/sec-api-documentation
Rate limit: 10 requests/second — this script sleeps 0.15s between calls.
"""

import requests
import time
import csv
import os
from datetime import datetime

# ── Configuration ─────────────────────────────────────────────────────────────

HEADERS = {
    # Required by SEC. Replace with your name and email.
    "User-Agent": "DataVisualization research@example.com",
    "Accept": "application/json",
}

BASE = "https://data.sec.gov/api/xbrl/companyconcept"

COMPANIES = [
    {
        "name": "Nvidia", "cik": "1045810", "ticker": "NVDA", "fy_end": "January",
        "rev_tags":  ["Revenues"],
        "op_tags":   ["OperatingIncomeLoss"],
        "emp_tags":  ["EntityNumberOfEmployees"],
    },
    {
        "name": "Meta", "cik": "1326801", "ticker": "META", "fy_end": "December",
        "rev_tags":  ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"],
        "op_tags":   ["OperatingIncomeLoss"],
        "emp_tags":  ["EntityNumberOfEmployees"],
    },
    {
        "name": "Microsoft", "cik": "789019", "ticker": "MSFT", "fy_end": "June",
        "rev_tags":  ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"],
        "op_tags":   ["OperatingIncomeLoss"],
        "emp_tags":  ["EntityNumberOfEmployees"],
    },
    {
        "name": "Alphabet", "cik": "1652044", "ticker": "GOOGL", "fy_end": "December",
        "rev_tags":  ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"],
        "op_tags":   ["OperatingIncomeLoss"],
        "emp_tags":  ["EntityNumberOfEmployees"],
    },
    {
        "name": "Apple", "cik": "320193", "ticker": "AAPL", "fy_end": "September",
        "rev_tags":  ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"],
        "op_tags":   ["OperatingIncomeLoss"],
        "emp_tags":  ["EntityNumberOfEmployees"],
    },
    {
        "name": "Netflix", "cik": "1065280", "ticker": "NFLX", "fy_end": "December",
        "rev_tags":  ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"],
        "op_tags":   ["OperatingIncomeLoss"],
        "emp_tags":  ["EntityNumberOfEmployees"],
    },
    {
        "name": "Amazon", "cik": "1018724", "ticker": "AMZN", "fy_end": "December",
        "rev_tags":  ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"],
        "op_tags":   ["OperatingIncomeLoss"],
        "emp_tags":  ["EntityNumberOfEmployees"],
    },
]

YEARS = [2021, 2022, 2023, 2024, 2025]

# ── Fetch helpers ─────────────────────────────────────────────────────────────

def fetch_concept(cik: str, taxonomy: str, tag: str) -> dict | None:
    """Fetch one XBRL concept for a company. Returns parsed JSON or None."""
    cik_padded = cik.zfill(10)
    url = f"{BASE}/CIK{cik_padded}/{taxonomy}/{tag}.json"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        time.sleep(0.15)  # stay well under 10 req/s
        if r.status_code == 200:
            return r.json()
        return None
    except requests.RequestException:
        return None


def pick_annual_fy(units: list, target_fy: int) -> int | None:
    """
    From a list of XBRL unit entries, find the 10-K annual value for the
    target fiscal year. Returns the value in raw units (USD, not millions).
    """
    candidates = [
        d for d in units
        if d.get("form") in ("10-K", "10-K/A")
        and d.get("fp") == "FY"
        and d.get("fy") == target_fy
    ]
    if not candidates:
        return None
    # Prefer the most recently filed entry to avoid amended duplicates
    candidates.sort(key=lambda d: d.get("filed", ""), reverse=True)
    return candidates[0]["val"]


def fetch_metric(cik: str, tags: list[str], taxonomy: str, target_fy: int):
    """Try each tag in order until one returns a value. Returns (value, tag) or (None, None)."""
    for tag in tags:
        data = fetch_concept(cik, taxonomy, tag)
        if not data:
            continue
        units = (
            data.get("units", {}).get("USD")
            or data.get("units", {}).get("pure")
        )
        if not units:
            continue
        val = pick_annual_fy(units, target_fy)
        if val is not None:
            return val, tag
    return None, None

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    rows = []
    print(f"Fetching from SEC EDGAR XBRL API — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    for co in COMPANIES:
        print(f"  {co['name']} (CIK {co['cik']})…")
        for year in YEARS:
            rev, rev_tag   = fetch_metric(co["cik"], co["rev_tags"], "us-gaap", year)
            op,  op_tag    = fetch_metric(co["cik"], co["op_tags"],  "us-gaap", year)
            emp, emp_tag   = fetch_metric(co["cik"], co["emp_tags"], "dei",     year)

            rev_m  = round(rev / 1e6)  if rev  is not None else None
            op_m   = round(op  / 1e6)  if op   is not None else None
            rpe    = round(rev / emp / 1000) if rev  and emp else None
            ope    = round(op  / emp / 1000) if op   and emp else None

            rows.append({
                "company":                  co["name"],
                "ticker":                   co["ticker"],
                "fiscal_year_end":          co["fy_end"],
                "year":                     year,
                "employees":                emp,
                "revenue_usd_m":            rev_m,
                "operating_income_usd_m":   op_m,
                "revenue_per_employee_usd_k":   rpe,
                "op_income_per_employee_usd_k": ope,
                "revenue_xbrl_tag":         rev_tag,
                "op_income_xbrl_tag":       op_tag,
                "headcount_xbrl_tag":       emp_tag,
                "sec_10k_url": (
                    f"https://www.sec.gov/cgi-bin/browse-edgar"
                    f"?action=getcompany&CIK={co['cik'].zfill(10)}&type=10-K"
                ),
            })

            status = f"    FY{year}: employees={emp:,} | rev=${rev_m}M | op_inc=${op_m}M" if emp else f"    FY{year}: no data"
            print(status)

    # Write CSV
    os.makedirs("data", exist_ok=True)
    out_path = "data/us_tech_efficiency_2021_2025.csv"
    fieldnames = [
        "company", "ticker", "fiscal_year_end", "year",
        "employees", "revenue_usd_m", "operating_income_usd_m",
        "revenue_per_employee_usd_k", "op_income_per_employee_usd_k",
        "revenue_xbrl_tag", "op_income_xbrl_tag", "headcount_xbrl_tag",
        "sec_10k_url",
    ]
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✓ Saved {len(rows)} rows → {out_path}")
    print(f"  Fetched at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
