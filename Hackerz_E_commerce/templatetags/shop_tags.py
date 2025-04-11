from django import template

register = template.Library()

@register.filter
def mult(value, arg):
    """Multiplies the arg and the value"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0 