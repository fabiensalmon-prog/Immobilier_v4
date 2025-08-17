import pandas as pd
def pmt(rate_m, n, p):
    if p <= 0: return 0.0
    if rate_m == 0: return p / n
    return p * (rate_m * (1 + rate_m) ** n) / ((1 + rate_m) ** n - 1)
def amortization_schedule(principal, annual_rate, years, insurance_rate_annual=0.0, start_month=1, start_year=2025):
    months = int(years*12); r = annual_rate/12.0; ins = insurance_rate_annual/12.0
    ann = pmt(r, months, principal); bal = principal; y, m = start_year, start_month; rows = []
    for i in range(1, months+1):
        interest = bal*r; principal_paid = ann - interest; bal = max(0.0, bal - principal_paid)
        rows.append({'period': i, 'year': y, 'month': m, 'payment_annuity': ann, 'interest': interest,
                     'principal_paid': principal_paid, 'insurance': principal*ins, 'payment_total': ann + principal*ins, 'balance': bal})
        m += 1;  m, y = (1, y+1) if m>12 else (m, y)
    return pd.DataFrame(rows)
def scenario_monthly_payment(principal, rate_annual, years, insurance_rate_annual=0.0):
    n=int(years*12); r=rate_annual/12.0; ann=pmt(r,n,principal); ins=principal*(insurance_rate_annual/12.0); return ann, ins, ann+ins
def build_financing_table(principal, rates_by_years, insurance_rate_annual=0.0, stress_bp=[0,50,100]):
    rows=[]
    for yrs, base in rates_by_years.items():
        for bp in stress_bp:
            rate = base + bp/10000.0; ann, ins, tot = scenario_monthly_payment(principal, rate, yrs, insurance_rate_annual)
            rows.append({'duration_years':yrs,'rate_%':round(rate*100,3),'annuity':ann,'insurance':ins,'monthly_payment_total':tot,'stress_bp':bp})
    return pd.DataFrame(rows).sort_values(['duration_years','stress_bp'])