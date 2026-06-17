"""Auto-aizpilda XADO produktu specifications_lv no nosaukumiem."""
import os, sys, re, django
os.environ["DJANGO_SETTINGS_MODULE"] = "xadobaltic.settings"
sys.path.insert(0, r"C:\Users\USER\xadobaltic")
sys.stdout.reconfigure(encoding="utf-8")
django.setup()
from catalog.models import Product

NAME_SPEC_MAP = [
    (r"508/509",        ["ACEA C5", "VW 508.00", "VW 509.00"]),
    (r"504/507",        ["ACEA C3", "VW 504.00", "VW 507.00"]),
    (r"\bC4\b",         ["ACEA C4"]),
    (r"\bC23\b",        ["ACEA C2", "ACEA C3"]),
    (r"\bC3\b",         ["ACEA C3"]),
    (r"\bC2\b",         ["ACEA C2"]),
    (r"A5/B5",          ["ACEA A5", "ACEA B5"]),
    (r"SN/CF",          ["API SN", "API CF"]),
    (r"SM/CF",          ["API SM", "API CF"]),
    (r"SL/CF",          ["API SL", "API CF"]),
    (r"SM/CJ-4",        ["API SM", "API CJ-4"]),
    (r"SL/CI-4",        ["API SL", "API CI-4"]),
    (r"CI-4",           ["API CI-4"]),
    (r"CJ-4",           ["API CJ-4"]),
    (r"E4/E6/E7",       ["ACEA E4", "ACEA E6", "ACEA E7"]),
    (r"E6/E9",          ["ACEA E6", "ACEA E9"]),
    (r"\bSN\b",         ["API SN"]),
    (r"\bSM\b",         ["API SM"]),
    (r"\bSL\b",         ["API SL"]),
    (r"(?<![A-Z])4T\b", ["JASO MA"]),
]

updated = 0
for p in Product.objects.all():
    name = p.name_lv or ""
    seen = []
    for pat, specs in NAME_SPEC_MAP:
        if re.search(pat, name, re.I if not pat[0].isupper() else 0):
            for s in specs:
                if s not in seen:
                    seen.append(s)

    if not seen:
        continue

    combined = ", ".join(seen)
    if p.specifications_lv == combined:
        continue

    p.specifications_lv = combined
    p.save(update_fields=["specifications_lv"])
    print(f"  {name[:50]:50} -> {combined[:60]}")
    updated += 1

print(f"\nAtjaunots: {updated}")
