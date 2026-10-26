import re,json,html,sys,urllib.request,datetime,concurrent.futures as cf
B='https://basketaraba.com/es/fab-online/'
def get(u):
    for _ in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read().decode('utf8','replace')
        except Exception as e: err=e
    raise err
def clean(s): return html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',re.sub(r"<span class=.tit-mobil.>.*?</span>",'',s)))).strip()
def rows(t): return [[clean(c) for c in re.findall(r'<td[^>]*>(.*?)</td>',r,flags=re.S)] for r in re.findall(r"<tr class='tm-body'>(.*?)</tr>",t,flags=re.S)]
cal='calendario-y-resultados-federacion-alavesa-de-baloncesto'; cla='clasificaciones-federacion-alavesa-de-baloncesto'
t=get(B+cla)
groups=[(a,clean(b),clean(c)) for a,b,c in re.findall(r"grupo=(\d+)&seccion=0'>\d+</a></td><td><span[^>]*>GRUPO: </span><a[^>]*>(.*?)</a></td><td><span[^>]*>CATEGOR[^<]*</span><a[^>]*>(.*?)</a>",t)]
def one(g):
    code,name,cat=g
    s=get(f'{B}{cla}?grupo={code}&seccion=0')
    st=[dict(pos=r[0],team=r[1],j=r[2],g=r[3],p=r[4],np=r[5],s=r[6],tf=r[7],tc=r[8],pts=r[9]) for r in rows(s) if len(r)>=10]
    c=get(f'{B}{cal}?grupo={code}&seccion=2')
    i0=c.find('<tbody>');i1=c.find('</tbody>',i0)
    clubs={r[0]:r[1] for r in rows(c[i0:i1]) if len(r)>=2 and r[0]!='DESCANSA'}
    rounds=[]
    for m in re.finditer(r'<th class="derecha">\s*(Jornada[^<]*)</th>\s*<th[^>]*>[^<]*</th>\s*<th class="izquierda">([^<]*)</th>(.*?)</table>',c,flags=re.S):
        ms=[dict(home=r[0],score=r[1].replace('–','-'),away=r[2]) for r in rows(m.group(3)) if len(r)>=3]
        rounds.append(dict(name=clean(m.group(1)),date=clean(m.group(2)),matches=ms))
    return dict(code=code,name=name,cat=cat,standings=st,rounds=rounds,clubs=clubs)
with cf.ThreadPoolExecutor(6) as ex: data=list(ex.map(one,groups))
# next round details (time/venue)
n=get(B+'proxima-jornada-federacion-alavesa-baloncesto')
nxt={}
for m in re.finditer(r"<table class=.fab-online.*?</table>",n,flags=re.S):
    pass
for blk in re.split(r'(?=\b\d{4}\s)',clean(n)): pass
txt=re.sub(r'\s+',' ',re.sub(r'<(?!/?(td|tr|th|table))[^>]+>','',n))
for m in re.finditer(r"<tr class='tm-body'>(.*?)</tr>",n,flags=re.S):pass
# parse sequentially with headers
pos=[(m.start(),m.group(1)) for m in re.finditer(r'<(?:h\d|div|td)[^>]*>\s*(\d{4}) ([^<]*?)\s*<',n)]
cur=None;up=[]
for m in re.finditer(r"<(?:[^>]*)>\s*(\d{4})\s+([A-Z0-9][^<]*?)\s*-\s*[^<]*<|<tr class='tm-body'>(.*?)</tr>",n,flags=re.S):
    if m.group(1): cur=m.group(1); continue
    r=rows("<tr class='tm-body'>"+m.group(3)+"</tr>")[0]
    if cur and len(r)>=7: up.append(dict(code=cur,home=r[0],away=r[1],date=r[2],time=r[3],venue=r[4],addr=r[5],town=r[6]))
out=dict(updated=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='minutes'),groups=data,upcoming=up)
json.dump(out,open('data.json','w'),ensure_ascii=False)
print(len(data),'groups',sum(len(g['standings']) for g in data),'teams',len(up),'upcoming',[g['name'] for g in data][:3])
