import streamlit as st, pandas as pd
from core.scraper import get_listings
from core.dedup import soft_dedup
from core.scoring import compute_scores
from core.aftertax import compute_after_tax
st.header('🔔 Alertes — scan à la demande')
params=st.session_state.get('params'); 
if params is None: st.warning('Passe par **Paramètres**'); st.stop()
cities=st.text_input('Villes', 'Brest, Paris'); max_price=st.number_input('Prix max (€)', 0, value=300000, step=5000); min_surface=st.number_input('Surface min (m²)', 0, value=18, step=2)
sources=st.multiselect('Sources', ['leboncoin','seloger'], default=['leboncoin','seloger']); per_city=st.number_input('Nb/ville', 10, 60, 30, 5)
cf_min=st.number_input('CF after‑tax min (€/mois)', -500, 2000, 0, 50)
if st.button('🚀 Scanner maintenant', type='primary'):
    raw=get_listings([c.strip() for c in cities.split(',') if c.strip()], max_price=max_price, min_surface=min_surface, limit_per_city=int(per_city), sources=tuple(sources))
    if raw.empty: st.warning('Aucune annonce'); st.stop()
    base=compute_scores(soft_dedup(raw), params, strategy=params.get('strategy','meuble'))
    full=compute_after_tax(base, params)
    res=full[full['cf_after_tax_best']>=cf_min].sort_values('cf_after_tax_best', ascending=False)
    st.success(f'{len(res)} opportunités'); st.dataframe(res, use_container_width=True)
    st.download_button('⬇️ Export CSV', data=res.to_csv(index=False).encode('utf-8'), file_name='alertes_resultats.csv')