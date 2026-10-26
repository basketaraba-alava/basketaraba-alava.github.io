import json,sys
d=json.load(open(sys.argv[1]));g=d['groups'];h=len(g)//2
w=lambda n,o:open(n,'w',encoding='utf-8').write(json.dumps(o,separators=(',',':'),ensure_ascii=False))
w('data-1.json',{'updated':d['updated'],'upcoming':d['upcoming'],'groups':g[:h]});w('data-2.json',{'groups':g[h:]})
