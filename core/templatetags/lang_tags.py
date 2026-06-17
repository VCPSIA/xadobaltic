from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def lang_url(context, lang_code):
    request = context.get('request')
    if not request:
        return '/'

    path = request.get_full_path()
    default = settings.LANGUAGE_CODE

    # Noņem pašreizējo valodas prefiksu (ne-default valodām ir /{code}/ prefikss)
    clean = path
    for code, _ in settings.LANGUAGES:
        if code == default:
            continue
        if path.startswith(f'/{code}/'):
            clean = path[len(f'/{code}'):]
            break
        elif path == f'/{code}':
            clean = '/'
            break

    # Pievieno mērķa valodas prefiksu
    if lang_code == default:
        return clean
    return f'/{lang_code}{clean}'
