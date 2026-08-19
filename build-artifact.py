#!/usr/bin/env python3
"""Self-contained változat az Artifact publikáláshoz.

Az assets/ képeket base64 data URI-ba forgatja. Minden kép csak egyszer
kerül be: a JS-ből hivatkozott példányok egy ASSETS lookupon keresztül
érik el ugyanazt a stringet.
"""
import base64, io, re

src = io.open("index.html", encoding="utf-8").read()
paths = sorted(set(re.findall(r'assets/[A-Za-z0-9_-]+\.jpg', src)))

def datauri(p):
    with open(p, "rb") as fh:
        return "data:image/jpeg;base64," + base64.b64encode(fh.read()).decode()

uris = {p: datauri(p) for p in paths}

# 1. HTML attribútumok: közvetlen behelyettesítés
out = re.sub(r'src="(assets/[A-Za-z0-9_-]+\.jpg)"',
             lambda m: 'src="' + uris[m.group(1)] + '"', src)

# 2. JS stringliterálok: lookupra cserélve, hogy ne duplikálódjon a base64
out = re.sub(r'"(assets/[A-Za-z0-9_-]+\.jpg)"',
             lambda m: 'ASSETS["' + m.group(1) + '"]', out)

lookup = "<script>\nvar ASSETS = {\n" + ",\n".join(
    '  "%s": "%s"' % (p, uris[p]) for p in paths) + "\n};\n</script>\n"
out = out.replace("<nav class=\"nav\"", lookup + "\n<nav class=\"nav\"", 1)

io.open("artifact.html", "w", encoding="utf-8").write(out)
print("artifact.html %.2f MB (%d kép)" % (len(out) / 1024 / 1024, len(paths)))
