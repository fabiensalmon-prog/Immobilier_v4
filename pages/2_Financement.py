import streamlit as st, pandas as pd
from core.finance import build_financing_table, amortization_schedule
st.header('💶 Financement')
rates = st.file_uploader('Taux (CSV: duration_years, rate_percent)', type=['csv'])
rates = pd.DataFrame({'duration_years':[15,20,25], 'rate_percent':[2.99,3.05,3.11]}) if rates is None else pd.read_csv(rates)
principal=st.number_input('Montant (€)', 0, value=250000, step=5000)
insurance=st.number_input('Assurance (% capital annuel)', 0.30)/100.0
rates_by={int(r.duration_years): float(r.rate_percent)/100.0 for _,r in rates.iterrows()}
table=build_financing_table(principal, rates_by, insurance_rate_annual=insurance, stress_bp=[0,100])
st.dataframe(table, use_container_width=True)
yrs=st.selectbox('Durée', sorted(rates_by.keys())); rate=st.number_input('Taux (%)', value=float(rates_by[yrs]*100), step=0.01)
st.dataframe(amortization_schedule(principal, rate/100.0, yrs, insurance).head(24), use_container_width=True)