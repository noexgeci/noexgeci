#!/usr/bin/env python3
"""Artifact-változat az index.html-ből.

Az Artifact futtató saját <head>-et ad a laphoz, ezért a teljes dokumentumból
csak a törzs kerül át — a <title>, a betűtípus-hivatkozás és a stíluslap a
törzs elejére költözik. A képek base64 data URI-ba fordulnak, mindegyik
pontosan egyszer: a JS-ből hivatkozott példányok egy ASSETS lookupot néznek.
"""
import base64, io, re

src = io.open("index.html", encoding="utf-8").read()

def block(pattern, flags=re.S):
    m = re.search(pattern, src, flags)
    if not m:
        raise SystemExit("nem találom: " + pattern)
    return m.group(0)

title = block(r"<title>.*?</title>")
fonts = block(r'<link rel="preconnect".*?display=swap">')
style = block(r"<style>.*?</style>")
body  = block(r"<body>(.*)</body>").replace("<body>", "").replace("</body>", "")

out = "\n".join([title, fonts, style, body])

paths = sorted(set(re.findall(r"assets/[A-Za-z0-9_-]+\.jpg", out)))
uris = {}
for p in paths:
    with open(p, "rb") as fh:
        uris[p] = "data:image/jpeg;base64," + base64.b64encode(fh.read()).decode()

out = re.sub(r'src="(assets/[A-Za-z0-9_-]+\.jpg)"',
             lambda m: 'src="' + uris[m.group(1)] + '"', out)
out = re.sub(r'"(assets/[A-Za-z0-9_-]+\.jpg)"',
             lambda m: 'ASSETS["' + m.group(1) + '"]', out)

lookup = "<script>\nvar ASSETS = {\n" + ",\n".join(
    '  "%s": "%s"' % (p, uris[p]) for p in paths) + "\n};\n</script>"
out = out.replace('<a class="skip"', lookup + '\n\n<a class="skip"', 1)

io.open("artifact.html", "w", encoding="utf-8").write(out)
print("artifact.html %.2f MB (%d kép)" % (len(out) / 1024 / 1024, len(paths)))
