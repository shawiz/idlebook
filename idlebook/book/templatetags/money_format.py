from django import template
register = template.Library()

@register.filter
def money(value):
    """
    format the money from interger to a money unit
    """
    if value == None:
        return ''
    value = str(value)
    sign = ''
    if value.startswith('-'):
        value = value[1:]
        sign = '-'
    elif value.startswith('+'):
        value = value[1:]
        sign = '+'
    while len(value) < 3:
        value = '0' + value
    return sign + '$' + value[:-2] + '.' + value[-2:]


@register.filter
def price(value):
    """
    format price from interger to a money unit
    it also converts 0 to free
    """
    if value == 0:
        return 'Free'
    value = str(value)
    sign = ''
    if value.startswith('-'):
        value = value[1:]
        sign = '-'
    while len(value) < 3:
        value = '0' + value
    return sign + '$' + value[:-2] + '.' + value[-2:]
