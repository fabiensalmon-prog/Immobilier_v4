import pandas as pd
def load_dvf_medians(dvf_df):
    if dvf_df is None or dvf_df.empty: return None
    cols={c.lower():c for c in dvf_df.columns}; 
    if not cols.get('city') or not cols.get('median_price_sqm'): raise ValueError('DVF medians CSV: city, median_price_sqm')
    return dvf_df
def price_gap_vs_dvf(price, surface_m2, city, dvf_df):
    if dvf_df is None or dvf_df.empty or not surface_m2: return None
    cols={c.lower():c for c in dvf_df.columns}; cc=cols.get('city'); mc=cols.get('median_price_sqm')
    sub=dvf_df[dvf_df[cc].str.lower()==str(city).lower()]; 
    if sub.empty: return None
    med=float(sub.iloc[0][mc]); 
    if med<=0: return None
    ppm2=price/surface_m2; return (ppm2-med)/med*100.0