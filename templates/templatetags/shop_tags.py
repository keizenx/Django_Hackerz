from django import template

register = template.Library()
 
@register.filter
def mult(value, arg):
    """Multiplies the arg and the value"""
    return float(value) * float(arg) 