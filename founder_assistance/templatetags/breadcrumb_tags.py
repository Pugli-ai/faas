from django import template
from django.urls import resolve, reverse

register = template.Library()

@register.inclusion_tag('founder_assistance/includes/breadcrumbs.html', takes_context=True)
def breadcrumb_items(context):
    """Generate breadcrumb items based on the current URL path."""
    request = context['request']
    path = request.path.strip('/')
    parts = path.split('/')
    
    # Start with home
    items = [{'title': 'Home', 'url': '/'}]
    
    # Build breadcrumb items
    current_path = ''
    for i, part in enumerate(parts):
        if not part:  # Skip empty parts
            continue
            
        # Special case for project URLs
        if part == 'project' and i == 0:
            items.append({'title': 'Projects', 'url': reverse('founder_assistance:project_list')})
            continue
            
        current_path += f'/{part}'
        
        # Convert URL part to title (e.g., project-detail -> Project Detail)
        title = ' '.join(word.capitalize() for word in part.split('-'))
        
        # If this is the last item, don't make it a link
        if i == len(parts) - 1:
            items.append({'title': title, 'url': None})
        else:
            items.append({'title': title, 'url': current_path})
    
    return {'items': items}
