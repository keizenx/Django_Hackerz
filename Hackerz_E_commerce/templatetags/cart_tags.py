from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument"""
    return float(value) * float(arg)

@register.filter
def subtotal(price, quantity):
    """Returns the subtotal for an item"""
    return price * quantity 