from django import template

register = template.Library()


@register.filter
def in_category(value, category_list):
    """
    Checks if the value is in the category list
    """
    return value in category_list.split(',')