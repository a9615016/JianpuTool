# CLEAN MUSICXML V34 (template)
from lxml import etree
from copy import deepcopy
import sys

if len(sys.argv)<3:
    print("python clean_musicxml_v34.py input.musicxml output.musicxml")
    raise SystemExit

inp,out=sys.argv[1],sys.argv[2]
tree=etree.parse(inp); root=tree.getroot()

for tag in ("chord","beam","tie","backup","forward","voice"):
    for e in root.xpath(f".//{tag}"):
        p=e.getparent()
        if p is not None: p.remove(e)

BAR=64
for measure in root.xpath(".//measure"):
    cur=0
    notes=list(measure.xpath("./note"))
    for n in notes:
        d=n.find("duration")
        if d is None: continue
        try:l=int(d.text)
        except:continue
        while cur+l>BAR:
            first=max(0,BAR-cur)
            overflow=l-first
            d.text=str(first)
            second=deepcopy(n)
            second.find("duration").text=str(overflow)
            nm=measure.getnext()
            while nm is not None and etree.QName(nm).localname!="measure":
                nm=nm.getnext()
            if nm is None:
                nm=etree.Element("measure")
                nm.set("number",str(int(measure.get("number","0"))+1))
                measure.addnext(nm)
            nm.insert(0,second)
            cur=0
            measure=nm
            n=second
            d=second.find("duration")
            l=overflow
        cur+=l
tree.write(out,encoding="utf-8",xml_declaration=True)
print("DONE",out)
