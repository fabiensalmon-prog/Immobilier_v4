
def lmnp_micro_bic(receipts_year, tmi=0.30, ps=0.172): return max(0.0, 0.5*receipts_year)*(tmi+ps)
def lmnp_reel(receipts_year, charges_year, interets_year, amort_year, tmi=0.30, ps=0.172): return max(0.0, receipts_year-charges_year-interets_year-amort_year)*(tmi+ps)
def nu_micro_foncier(receipts_year, tmi=0.30, ps=0.172): return max(0.0, 0.7*receipts_year)*(tmi+ps)
def nu_reel(receipts_year, charges_year, interets_year, tmi=0.30, ps=0.172): return max(0.0, receipts_year-charges_year-interets_year)*(tmi+ps)
