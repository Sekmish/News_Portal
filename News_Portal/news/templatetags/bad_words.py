from django import template
import re
register = template.Library()

UNWANTED_WORDS = {'пись', 'какаш', 'истор', 'хрень'}

UNWANTED_WORDS_PATTERN = re.compile(r'\b(?:\w*' + '\w*\w*\w*|\w*'.join(UNWANTED_WORDS) + r'\w*)\b', re.IGNORECASE)


@register.filter
def censor(value):
    try:
        return UNWANTED_WORDS_PATTERN.sub(lambda match: match.group()[0] + '*' * (len(match.group()) - 1), value)
    except Exception as e:
        print(f"Error in censor filter: {e}")
        return value


register.filter('censor', censor)