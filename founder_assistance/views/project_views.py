from .project_base_views import (
    project_list,
    project_detail,
    project_edit
)

from .project_team_views import (
    add_team_member,
    remove_team_member
)

from .project_ai_views import (
    project_content_generator,
    project_market_analysis,
    project_competitor_analysis
)

# Re-export all views
__all__ = [
    'project_list',
    'project_detail',
    'project_edit',
    'add_team_member',
    'remove_team_member',
    'project_content_generator',
    'project_market_analysis',
    'project_competitor_analysis'
]
