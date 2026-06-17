import re
from html import unescape
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(is_safe=True)
def clean_html(value):
    if not value:
        return ''
    html = str(value)

    # Ja teksts satur &lt; — tas ir double-escaped, atšifrē
    if '&lt;' in html:
        html = unescape(html)

    # Noņem inline style= atribūtus
    html = re.sub(r'\s+style\s*=\s*"[^"]*"', '', html)
    html = re.sub(r"\s+style\s*=\s*'[^']*'", '', html)

    # Noņem vecā HTML atribūtus
    html = re.sub(r'\s+(?:color|face|size|bgcolor|align|valign|width|height)\s*=\s*"[^"]*"', '', html)

    # Noņem klases
    html = re.sub(r'\s+class\s*=\s*"[^"]*"', '', html)

    # Noņem tukšus span tagus
    html = re.sub(r'<span\s*>(.*?)</span>', r'\1', html, flags=re.S)
    html = re.sub(r'</?span>', '', html)

    # Attīra tukšas rindkopas
    html = re.sub(r'<p>\s*(&nbsp;|\s)*\s*</p>', '', html)

    # Noņem &nbsp; ķēdes
    html = re.sub(r'(&nbsp;\s*){3,}', ' ', html)

    return mark_safe(html.strip())
