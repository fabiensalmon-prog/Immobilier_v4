import pandas as pd
def normalize_cols(df): return {c.lower(): c for c in df.columns}
def estimate_rent_per_m2(city, property_type, bench_df, fallback):
    ck=str(city).lower().strip(); pt=(property_type or 'all').lower().strip()
    if bench_df is None or bench_df.empty: return float(fallback.get(ck, fallback.get('default', 20.0)))
    cols=normalize_cols(bench_df); cc=cols.get('city'); ptc=cols.get('property_type'); rc=cols.get('rent_per_m2')
    if not cc or not rc: return float(fallback.get(ck, fallback.get('default', 20.0)))
    d=bench_df[bench_df[cc].str.lower()==ck]
    if ptc and pt: 
        dt=d[d[ptc].str.lower()==pt]
        if not dt.empty: return float(dt.iloc[0][rc])
    if not d.empty: return float(d.iloc[0][rc])
    return float(fallback.get(ck, fallback.get('default', 20.0)))
def apply_rent_cap(total_rent, surface_m2, cap_per_m2=None, apply_cap=False):
    if not apply_cap or not cap_per_m2 or cap_per_m2<=0: return total_rent
    return min(total_rent, cap_per_m2*surface_m2)