from django.utils import timezone
from django import template
import locale
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

register = template.Library()

@register.simple_tag()
def current_time(format_string='%d %B %Y %A'):
    return timezone.now().strftime(format_string)


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    return d.urlencode()