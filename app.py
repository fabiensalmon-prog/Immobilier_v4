import streamlit as st
from pathlib import Path
st.set_page_config(page_title='Ultimate Invest v5', layout='wide')
st.title('🏠 Ultimate Invest v5 — Chasseur d\'opportunités')
st.caption('Scraping LBC/SeLoger • Négociation auto • Encadrement • Financement • After‑tax • Alertes')
st.markdown('Allez dans **Paramètres**, puis **Dashboard**.')
for fn in ['rents_example.csv','dvf_medians_example.csv','rates_2025-08.csv']:
    p=Path('data/examples')/fn
    if p.exists(): st.download_button(f'⬇️ {fn}', data=p.read_bytes(), file_name=fn)