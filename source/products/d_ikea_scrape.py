import sys, re, urllib.request, html, json, os
url, key, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
req = urllib.request.Request(url, headers={"User-Agent": UA})
page = urllib.request.urlopen(req, timeout=30).read().decode("utf8", "replace")
open(os.path.join(outdir, f"d_{key}_page.html"), "w", encoding="utf8").write(page)
imgs = []
for m in re.findall(r'https://www\.ikea\.com/[a-z]{2}/[a-z]{2}/images/products/[a-z0-9\-_]+\.(?:jpg|png)', page):
    if m not in imgs: imgs.append(m)
for i in imgs: print(i)
# measurements
txt = html.unescape(re.sub(r'<[^>]+>', '|', page))
for m in re.finditer(r'(?i)(width|depth|height|diameter|seat|length|breite|tiefe|höhe|sitz|Durchmesser|cord|Kabel|shade|Schirm)[^|]{0,30}\|*\s*:?\|*\s*[0-9][0-9.,]*\s*(cm|mm|m|kg|W)', txt):
    print("DIM:", re.sub(r'\|+', ' ', m.group(0)))
