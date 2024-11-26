from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """Split a string into a list on the given separator"""
    return value.split(arg)

@register.filter
def trim(value):
    """Remove leading and trailing whitespace"""
    return value.strip() if value else value
