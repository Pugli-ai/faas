from django import template
import json

# Register the template library
register = template.Library()

@register.filter(name='get_json_field')
def get_json_field(json_string, field_path):
    """
    Gets a field from a JSON string using dot notation
    Example: {{ idea.description|get_json_field:"analysis.refined_idea.enhanced_description" }}
    """
    try:
        if isinstance(json_string, str):
            data = json.loads(json_string)
        else:
            data = json_string
        keys = field_path.split('.')
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key, '')
            else:
                return ''
        return data if data is not None else ''
    except:
        return ''

@register.filter(name='format_list')
def format_list(value):
    """
    Formats a list as a bullet-point string
    """
    if isinstance(value, list):
        return "\n".join([f"• {item}" for item in value])
    return value or ''

@register.filter(name='format_dict')
def format_dict(value):
    """
    Formats a dictionary as a readable string
    """
    if isinstance(value, dict):
        return "\n".join([f"{k}: {v}" for k, v in value.items()])
    return value or ''
