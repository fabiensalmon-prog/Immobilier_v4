import pandas as pd
from .finance import amortization_schedule
from .fiscalite import lmnp_micro_bic, lmnp_reel, nu_micro_foncier, nu_reel
def estimate_interest_year(v, annual_rate, years): 
    if not v or v<=0: return 0.0
    df=amortization_schedule(v, annual_rate, years, 0.0); return float(df.head(12)['interest'].sum())
def compute_after_tax(df, params):
    df=df.copy(); tmi=float(params.get('tmi',0.30)); ps=float(params.get('ps',0.172))
    years=int(params.get('duree_annees',25)); rate=float(params.get('taux',0.0305))
    vac=float(params.get('vacancy_rate',0.08)); mg=float(params.get('mgmt_rate',0.07)); nonr=float(params.get('nonrecup_rate',0.05)); gli=float(params.get('gli_rate',0.025))
    pno=float(params.get('pno_monthly',12.0)); tf_f=float(params.get('taxe_fonciere_monthly',60.0)); comp=float(params.get('compta_monthly',40.0))
    bshare=float(params.get('building_share',0.80)); amort=float(params.get('amortization_rate_building',0.025))
    receipts_year=(df['rent_est_monthly'].fillna(0)*(1-vac)*12.0)
    charges_year=(receipts_year*(mg+nonr+gli)+(df.get('tf_m_est',tf_f).fillna(tf_f)*12.0)+(pno+comp)*12.0)
    to_finance=(df['expected_price']+df.get('notary_fees',0)+df.get('travaux',0)-df.get('apport',0)).clip(lower=0)
    interest_year=to_finance.apply(lambda x: estimate_interest_year(x, rate, years))
    base_amort=((df['expected_price'].fillna(0)+df.get('notary_fees',0)+df.get('travaux',0))*bshare); amort_year=base_amort*amort
    tax_lmnp_micro=receipts_year.apply(lambda r: lmnp_micro_bic(r,tmi=tmi,ps=ps))
    tax_lmnp_reel=[lmnp_reel(r,c,i,a,tmi=tmi,ps=ps) for r,c,i,a in zip(receipts_year,charges_year,interest_year,amort_year)]
    tax_nu_micro=receipts_year.apply(lambda r: nu_micro_foncier(r,tmi=tmi,ps=ps))
    tax_nu_reel=[nu_reel(r,c,i,tmi=tmi,ps=ps) for r,c,i in zip(receipts_year,charges_year,interest_year)]
    df['tax_lmnp_micro_m']=pd.Series(tax_lmnp_micro)/12.0; df['tax_lmnp_reel_m']=pd.Series(tax_lmnp_reel)/12.0
    df['tax_nu_micro_m']=pd.Series(tax_nu_micro)/12.0; df['tax_nu_reel_m']=pd.Series(tax_nu_reel)/12.0
    cf=df['cashflow_monthly'].fillna(0)
    df['cf_after_tax_lmnp_micro']=cf-df['tax_lmnp_micro_m']; df['cf_after_tax_lmnp_reel']=cf-df['tax_lmnp_reel_m']
    df['cf_after_tax_nu_micro']=cf-df['tax_nu_micro_m']; df['cf_after_tax_nu_reel']=cf-df['tax_nu_reel_m']
    cols=['cf_after_tax_lmnp_micro','cf_after_tax_lmnp_reel','cf_after_tax_nu_micro','cf_after_tax_nu_reel']
    df['cf_after_tax_best']=df[cols].max(axis=1); df['best_scheme']=df[cols].idxmax(axis=1).str.replace('cf_after_tax_','')
    return df