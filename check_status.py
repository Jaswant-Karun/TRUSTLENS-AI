import urllib.request
import re

endpoints = [
    'http://localhost:3000/investigations/INV-2026-0881',
    'http://localhost:3000/dashboard',
    'http://localhost:3000/threat-library',
    'http://localhost:3000/analytics',
]

for ep in endpoints:
    try:
        res = urllib.request.urlopen(ep)
        html = res.read().decode('utf-8')
        css_links = re.findall(r'<link[^>]+rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)["\']', html)
        print(f"{ep} -> HTTP {res.status}, {len(html)} bytes, CSS: {len(css_links)} files")
        for c in css_links:
            curl = 'http://localhost:3000' + c if c.startswith('/') else c
            cres = urllib.request.urlopen(curl)
            css_data = cres.read()
            print(f"   CSS {c} -> {cres.status} ({len(css_data)} bytes)")
    except Exception as e:
        print(f"{ep} -> ERROR: {e}")
