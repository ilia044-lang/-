#!/usr/bin/env python3
"""
KDP Royalty & Pricing Calculator - US marketplace.
Rates verified against KDP help pages, September 2026.
Always re-verify against the KDP pricing page before publishing.

Usage:
    python3 kdp_calc.py --pages 120 --ink bw --trim large --price 12.99
    python3 kdp_calc.py --pages 60 --ink premium_color --trim large --breakeven
    python3 kdp_calc.py --ebook --price 9.99 --mb 2
"""
import argparse

# (min_pages, max_pages, fixed, per_page) per ink type, regular / large trim
PRINT_COST = {
    "bw":             {"regular": [(24, 110, 2.30, 0.0), (110, 828, 1.00, 0.012)],
                       "large":   [(24, 110, 2.84, 0.0), (110, 828, 1.00, 0.017)]},
    "groundwood":     {"regular": [(24, 112, 2.23, 0.0), (113, 828, 1.00, 0.0114)],
                       "large":   [(24, 112, 2.75, 0.0), (113, 828, 1.00, 0.0162)]},
    "standard_color": {"regular": [(72, 600, 1.00, 0.0255)],
                       "large":   [(72, 600, 1.00, 0.0402)]},
    "premium_color":  {"regular": [(24, 40, 3.60, 0.0), (41, 828, 1.00, 0.065)],
                       "large":   [(24, 40, 4.20, 0.0), (41, 828, 1.00, 0.08)]},
}
SPINE_PER_PAGE = {"white": 0.002252, "cream": 0.0025,
                  "groundwood": 0.00235, "color": 0.002347}

EBOOK_70_MIN, EBOOK_70_MAX = 2.99, 12.99   # US, effective 2026-07-07
EBOOK_DELIVERY_PER_MB = 0.15


def print_cost(pages, ink, trim):
    for lo, hi, fixed, per in PRINT_COST[ink][trim]:
        if lo <= pages <= hi:
            return round(fixed + per * pages, 2)
    raise ValueError(f"{pages} pages not supported for {ink} / {trim} trim")


def print_royalty(price, pages, ink, trim, expanded=False):
    cost = print_cost(pages, ink, trim)
    rate = 0.40 if expanded else (0.60 if price >= 9.99 else 0.50)
    return round(rate * price - cost, 2), rate, cost


def min_list_price(pages, ink, trim, expanded=False):
    """Smallest list price at which the royalty is still >= 0."""
    cost = print_cost(pages, ink, trim)
    if expanded:
        return round(cost / 0.40 + 0.004, 2), 0.40
    p50 = cost / 0.50                      # priced under $9.99 -> 50% rate
    if p50 < 9.99:
        return round(p50 + 0.004, 2), 0.50
    if 0.60 * 9.99 >= cost:                # 50% can't cover it, but 60% at $9.99 can
        return 9.99, 0.60
    return round(cost / 0.60 + 0.004, 2), 0.60


def ebook_royalty(price, mb):
    if EBOOK_70_MIN <= price <= EBOOK_70_MAX:
        return round(0.70 * (price - EBOOK_DELIVERY_PER_MB * mb), 2), 0.70
    return round(0.35 * price, 2), 0.35


def spine(pages, paper):
    return round(pages * SPINE_PER_PAGE[paper], 4)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int)
    ap.add_argument("--ink", default="bw", choices=list(PRINT_COST))
    ap.add_argument("--trim", default="regular", choices=["regular", "large"])
    ap.add_argument("--paper", default="white", choices=list(SPINE_PER_PAGE))
    ap.add_argument("--price", type=float)
    ap.add_argument("--expanded", action="store_true")
    ap.add_argument("--ebook", action="store_true")
    ap.add_argument("--mb", type=float, default=1.0)
    ap.add_argument("--target", type=float, help="monthly profit target in USD")
    a = ap.parse_args()

    if a.ebook:
        r, rate = ebook_royalty(a.price, a.mb)
        print(f"eBook  ${a.price:.2f}  {a.mb}MB  ->  rate {rate:.0%}  royalty ${r:.2f}")
        print(f"  note: print edition must be priced >= ${a.price / 0.8:.2f} "
              f"(eBook must sit 20% below print)")
        return

    cost = print_cost(a.pages, a.ink, a.trim)
    mn, mn_rate = min_list_price(a.pages, a.ink, a.trim, a.expanded)
    print(f"pages {a.pages} | ink {a.ink} | trim {a.trim}")
    print(f"  printing cost   : ${cost:.2f}")
    print(f"  min list price  : ${mn:.2f}  (at {mn_rate:.0%})")
    print(f"  spine width     : {spine(a.pages, a.paper)}\"  "
          f"({'spine text allowed' if a.pages > 79 else 'NO spine text (<=79pp)'})")
    if a.price:
        r, rate, _ = print_royalty(a.price, a.pages, a.ink, a.trim, a.expanded)
        print(f"  @ ${a.price:.2f}  ->  {rate:.0%} x {a.price:.2f} - {cost:.2f} "
              f"= ${r:.2f} per unit  ({r / a.price:.0%} of list)")
        if r <= 0:
            print("  !! negative royalty - price is below the KDP minimum")
        elif a.target:
            print(f"  units/month for ${a.target:.0f}: {a.target / r:.0f}")


if __name__ == "__main__":
    main()
