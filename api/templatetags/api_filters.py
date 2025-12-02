# api/templatetags/api_filters.py
from django import template

register = template.Library()

@register.filter
def add_class(field, css_class):
    """
    Add a CSS class to a form field
    """
    return field.as_widget(attrs={"class": css_class})

@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary by key
    """
    return dictionary.get(key)

@register.filter
def multiply(value, arg):
    """
    Multiply value by argument
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ""

# Agrega más filtros según necesites
@register.filter
def format_date(value, format_string="%d/%m/%Y"):
    """
    Format a date
    """
    if value:
        return value.strftime(format_string)
    return ""

@register.filter
def join_list(value, separator=", "):
    """
    Join a list with a separator
    """
    if isinstance(value, list):
        return separator.join(str(item) for item in value)
    return value