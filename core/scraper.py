import re, json, time, requests, pandas as pd
from bs4 import BeautifulSoup
UA={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116 Safari/537.36'}
SESSION=requests.Session(); SESSION.headers.update(UA); TO=12
def _clean_int(t):
    if t is None: return None
    import re
    s=str(t).replace('\xa0',' ').replace('€','').replace('m²','').replace(',','.'); s=re.sub(r'[^0-9\.\-]','',s)
    try: return int(float(s))
    except: return None
def _dom(txt):
    if not txt: return None
    t=str(txt).lower()
    if 'aujourd' in t: return 1
    if 'hier' in t: return 2
    import re
    m=re.search(r'(\d+)\s*jour',t); w=re.search(r'(\d+)\s*sem',t); mo=re.search(r'(\d+)\s*mois',t)
    if m: return int(m.group(1))
    if w: return int(w.group(1))*7
    if mo: return int(mo.group(1))*30
    return None
def search_leboncoin(city, limit=30, max_price=None, min_surface=None):
    from urllib.parse import quote
    url=f'https://www.leboncoin.fr/recherche?category=9&locations={quote(city)}'
    if max_price: url+=f'&price=min-{int(max_price)}'
    r=SESSION.get(url, timeout=TO); r.raise_for_status(); soup=BeautifulSoup(r.text,'html.parser'); out=[]
    try:
        for s in soup.find_all('script'):
            if s.string and '__PRELOADED_STATE__' in s.string:
                import re, json
                m=re.search(r'__PRELOADED_STATE__\s*=\s*(\{.*\});', s.string, re.S)
                if m:
                    data=json.loads(m.group(1)); ads=data.get('search',{}).get('ads',[])
                    for a in ads[:limit]:
                        price=a.get('price',{}).get('value'); attr=a.get('attributes',{})
                        surf=attr.get('surface',{}).get('value'); rooms=attr.get('rooms',{}).get('value')
                        city_name=a.get('location',{}).get('city_label') or city; link='https://www.leboncoin.fr'+a.get('url','')
                        title=a.get('subject'); dom=_dom(a.get('index_date_human_readable') or '')
                        out.append({'source':'LBC','id':a.get('list_id'),'title':title,'city':city_name,'price':price,'surface_m2':surf,'rooms':rooms,'url':link,'days_on_market':dom})
                break
    except Exception: pass
    if not out:
        for a in soup.select("a[data-test-id='ad']")[:limit]:
            link=a.get('href'); link=('https://www.leboncoin.fr'+link) if link and link.startswith('/') else link
            title=a.get_text(' ', strip=True)[:120]; price_tag=a.find('span', {'data-qa-id':'aditem_price'}); price=_clean_int(price_tag.text if price_tag else None)
            info=a.get_text(' ', strip=True); import re; m=re.search(r'(\d+)\s?m²',info); surf=int(m.group(1)) if m else None
            out.append({'source':'LBC','id':link,'title':title,'city':city,'price':price,'surface_m2':surf,'rooms':None,'url':link,'days_on_market':None})
    df=pd.DataFrame(out)
    if min_surface is not None: df=df[(df['surface_m2'].fillna(0)>=min_surface)]
    if max_price is not None: df=df[(df['price'].fillna(0)<=max_price)]
    return df.reset_index(drop=True)
def search_seloger(city, limit=30, max_price=None, min_surface=None):
    from urllib.parse import quote
    url=f'https://www.seloger.com/list.htm?projects=2&types=1&places=[{{co:{quote(city)}}}]'
    r=SESSION.get(url, timeout=TO); 
    if r.status_code!=200: return pd.DataFrame()
    soup=BeautifulSoup(r.text,'html.parser'); res=[]
    for li in soup.select('div[class*=Card_c-]')[:limit]:
        title=li.get_text(' ', strip=True)[:120]; a=li.find('a', href=True); link=a['href'] if a else None
        if link and link.startswith('//'): link='https:'+link
        txt=li.get_text(' ', strip=True); import re
        mp=re.search(r'(\d[\d\s\u00A0]+)\s*€',txt); price=_clean_int(mp.group(1)) if mp else None
        ms=re.search(r'(\d+)\s*m²',txt); surf=int(ms.group(1)) if ms else None
        res.append({'source':'SLG','id':link or title,'title':title,'city':city,'price':price,'surface_m2':surf,'rooms':None,'url':link,'days_on_market':None})
    df=pd.DataFrame(res)
    if min_surface is not None: df=df[(df['surface_m2'].fillna(0)>=min_surface)]
    if max_price is not None: df=df[(df['price'].fillna(0)<=max_price)]
    return df.reset_index(drop=True)
def get_listings_for_city(city, max_price=None, min_surface=None, limit=40, sources=('leboncoin','seloger')):
    import pandas as pd
    frames=[]
    if 'leboncoin' in sources: frames.append(search_leboncoin(city, limit, max_price, min_surface))
    if 'seloger' in sources: frames.append(search_seloger(city, limit, max_price, min_surface))
    frames=[f for f in frames if isinstance(f, pd.DataFrame) and not f.empty]
    if not frames: return pd.DataFrame(columns=['title','city','price','surface_m2','rooms','url','days_on_market','source'])
    df=pd.concat(frames, ignore_index=True).drop_duplicates(subset=['url']).reset_index(drop=True)
    for c in ['price','surface_m2']: 
        if c in df.columns: df[c]=pd.to_numeric(df[c], errors='coerce')
    return df
def get_listings(cities, max_price=None, min_surface=None, limit_per_city=40, sources=('leboncoin','seloger')):
    import pandas as pd, time
    all_frames=[]; cities=[c.strip() for c in cities if c.strip()]
    for city in cities:
        df=get_listings_for_city(city, max_price, min_surface, limit_per_city, sources)
        if isinstance(df, pd.DataFrame) and not df.empty: all_frames.append(df)
        time.sleep(0.5)
    if not all_frames: return pd.DataFrame(columns=['title','city','price','surface_m2','rooms','url','days_on_market','source'])
    return pd.concat(all_frames, ignore_index=True).drop_duplicates(subset=['url']).reset_index(drop=True)