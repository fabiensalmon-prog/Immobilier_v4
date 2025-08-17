import numpy as np, pandas as pd
from .rents import estimate_rent_per_m2, apply_rent_cap
def compute_scores(df, params, strategy='meuble'):
    df=df.copy(); cols={c.lower():c for c in df.columns}
    price=cols.get('price') or cols.get('prix'); surf=cols.get('surface_m2') or cols.get('surface'); city=cols.get('city') or cols.get('ville'); dom=cols.get('days_on_market'); url=cols.get('url')
    base=params['base_neg']; extra30=params['extra_per_30d']; negmax=params['neg_max']
    extra=(df[dom].fillna(0).astype(float)/30.0)*extra30 if dom and dom in df.columns else 0.0
    df['neg_bonus_dvf']=(df['price_gap_vs_dvf_%']>10).astype(float)*0.02 if 'price_gap_vs_dvf_%' in df.columns else 0.0
    neg=(base+extra+df['neg_bonus_dvf']).clip(0, negmax)
    df['expected_price']=df[price].astype(float)*(1-neg)
    df['notary_fees']=df['expected_price']*params['frais_notaires']; df['travaux']=params['travaux']; df['apport']=params['apport']
    years=params['duree_annees']; r=params['taux']/12.0; n=int(years*12)
    def pmt(rate,n,p): 
        if p<=0: return 0.0
        if rate==0: return p/n
        return p*(rate*(1+rate)**n)/(((1+rate)**n)-1)
    df['to_finance']=(df['expected_price']+df['notary_fees']+df['travaux']-df['apport']).clip(lower=0)
    df['monthly_payment']=df['to_finance'].apply(lambda p: pmt(r,n,p)); df['insurance_monthly']=df['to_finance']*(params['assurance']/12.0)
    rpm2=params['rpm2_fallback']; bench=params.get('rent_bench_df'); cap=params['apply_cap']; cap_m2=params['cap_per_m2']; enc=params['rent_control_cities']; mult=1.1 if strategy=='meuble' else 1.4 if strategy=='colocation' else 1.0
    def row_rent(row):
        if pd.isna(row[surf]): return None
        est=float(row[surf])*estimate_rent_per_m2(row[city],'all',bench,rpm2)*mult
        return apply_rent_cap(est, float(row[surf]), cap_m2, cap and str(row[city]).lower() in enc)
    df['rent_est_monthly']=df.apply(row_rent, axis=1)
    tf_tbl=params.get('tf_per_city', {})
    def tfm(row):
        ck=str(row[city]).lower(); rate=tf_tbl.get(ck, None)
        if rate and pd.notna(row[surf]): return float(row[surf])*rate
        return params['taxe_fonciere_monthly']
    df['tf_m_est']=df.apply(tfm, axis=1)
    vac=params['vacancy_rate']; mg=params['mgmt_rate']; nonr=params['nonrecup_rate']; capex=params['capex_rate']; gli=params['gli_rate']; pno=params['pno_monthly']; comp=params['compta_monthly']
    df['net_rent_oper_monthly']=df['rent_est_monthly'].apply(lambda r: None if r is None else r*(1-max(0,min(0.95,vac+mg+nonr+capex+gli)))-(pno+comp))
    df['net_rent_monthly']=df['net_rent_oper_monthly']-df['tf_m_est']
    df['cashflow_monthly']=df['net_rent_monthly']-df['monthly_payment']-df['insurance_monthly']
    df['gross_yield_%']=(df['rent_est_monthly']*12.0)/df['expected_price']*100.0
    denom=(df['expected_price']+df['notary_fees']+df['travaux']).replace(0,np.nan)
    df['net_yield_%']=((df['net_rent_monthly']-df['insurance_monthly'])*12.0)/denom*100.0
    out=[city,'source' if 'source' in df.columns else None, surf, price, 'expected_price','rent_est_monthly','net_rent_monthly','monthly_payment','insurance_monthly','cashflow_monthly','gross_yield_%','net_yield_%','tf_m_est']
    if dom in df.columns: out.insert(3, dom)
    if url in df.columns: out.append(url)
    out=[c for c in out if c is not None]
    for c in out:
        if c not in df.columns: df[c]=None
    return df[out].sort_values(['cashflow_monthly'], ascending=[False])