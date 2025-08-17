import pandas as pd
def soft_dedup(df):
    if df.empty: return df
    df=df.drop_duplicates(subset=[c for c in df.columns if c.lower()=='url']).copy()
    if 'price' in df.columns and 'surface_m2' in df.columns:
        df['_pr']=df['price'].round(-3); df['_su']=df['surface_m2'].round(0)
        df=df.sort_values(['_pr','_su']).drop_duplicates(['_pr','_su','city'], keep='first').drop(columns=['_pr','_su'], errors='ignore')
    return df