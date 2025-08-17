import streamlit as st, pandas as pd
from core.scraper import get_listings
from core.dedup import soft_dedup
from core.scoring import compute_scores
from core.aftertax import compute_after_tax
from core.dvf import load_dvf_medians, price_gap_vs_dvf
st.header('📊 Dashboard — scoring + after‑tax')
params=st.session_state.get('params'); 
if params is None: st.warning('Passe par **Paramètres**'); st.stop()
@st.cache_data(ttl=600, show_spinner=False)
def cached_search(cities, max_price, min_surface, per_city, sources):
    return get_listings(cities, max_price=max_price, min_surface=min_surface, limit_per_city=int(per_city), sources=tuple(sources))
c1,c2,c3,c4=st.columns([3,1,1,1])
with c1: cities_txt=st.text_input('Villes', 'Brest, Paris')
with c2: max_price=st.number_input('Prix max (€)', 0, value=300000, step=5000)
with c3: min_surface=st.number_input('Surface min (m²)', 0, value=18, step=2)
with c4: per_city=st.number_input('Nb/ville', 10, 60, 30, 5)
sources=st.multiselect('Sources', ['leboncoin','seloger'], default=['leboncoin','seloger'])
dvf_file=st.file_uploader('DVF médian €/m² (CSV)', type=['csv'])
dvf_df=load_dvf_medians(pd.read_csv(dvf_file)) if dvf_file is not None else None
if st.button('🔎 Chercher et scorer', type='primary'):
    cities=[c.strip() for c in cities_txt.split(',') if c.strip()]
    with st.spinner('Scraping…'): raw=cached_search(cities, max_price, min_surface, per_city, sources)
    if raw.empty: st.error('Aucune annonce (anti‑bot possible).'); st.stop()
    raw=soft_dedup(raw); base=compute_scores(raw, params, strategy=params.get('strategy','meuble'))
    if dvf_df is not None:
        cols={c.lower():c for c in raw.columns}; price=cols.get('price') or cols.get('prix'); surf=cols.get('surface_m2') or cols.get('surface'); city=cols.get('city') or cols.get('ville')
        base['price_gap_vs_dvf_%']=[price_gap_vs_dvf(r[price], r[surf], r[city], dvf_df) for _,r in base.iterrows()]
    full=compute_after_tax(base, params)
    st.dataframe(full.sort_values('cf_after_tax_best', ascending=False), use_container_width=True)
    if not full.empty and 'url' in full.columns:
        idx=st.selectbox('Détail', options=full.index.tolist(), format_func=lambda i: f"{full.loc[i,'city']} — CF after-tax €{full.loc[i,'cf_after_tax_best']:.0f}/mois")
        r=full.loc[idx]; st.metric('Prix négocié', f"€{r['expected_price']:,.0f}"); st.metric('CF after-tax', f"€{r['cf_after_tax_best']:,.0f}/mois"); st.write(f"[Voir l'annonce]({r['url']})")