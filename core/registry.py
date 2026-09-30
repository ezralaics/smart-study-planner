"""Pluggable Domain Module Registry for Life Planner OS (OmniLife).
Enables seamless domain extension (e.g. Health, Travel, Fitness) without modifying core infrastructure.
"""
from typing import Dict, List, Optional

class LifePlannerModule:
    """Represents a pluggable domain module in Life Planner OS."""
    def __init__(
        self,
        key: str,
        name: str,
        short_name: str,
        icon: str,
        color: str,
        url: str,
        badge: str,
        description: str = "",
        prefix: str = ""
    ):
        self.key = key
        self.name = name
        self.short_name = short_name
        self.icon = icon
        self.color = color
        self.url = url
        self.badge = badge
        self.description = description
        self.prefix = prefix or f"/{key}"

    def to_dict(self) -> dict:
        return {
            'key': self.key,
            'name': self.name,
            'short_name': self.short_name,
            'icon': self.icon,
            'color': self.color,
            'url': self.url,
            'badge': self.badge,
            'description': self.description,
            'prefix': self.prefix
        }


class LifePlannerRegistry:
    """Central registry tracking all active domains in the Life Planner OS Modular Monolith."""
    def __init__(self):
        self._modules: Dict[str, LifePlannerModule] = {}

    def register(self, module: LifePlannerModule) -> None:
        self._modules[module.key] = module

    def get(self, key: str) -> Optional[LifePlannerModule]:
        return self._modules.get(key)

    def list_all(self) -> List[LifePlannerModule]:
        return list(self._modules.values())

    def to_workspaces_list(self) -> List[dict]:
        return [m.to_dict() for m in self._modules.values()]


# Singleton Global Registry
registry = LifePlannerRegistry()

# -------------------------------------------------------------
# Register the 6 Foundational Life Planner OS Domain Modules:
# -------------------------------------------------------------

registry.register(LifePlannerModule(
    key='academics',
    name='Study Planner',
    short_name='Academics',
    icon='bi-mortarboard-fill',
    color='#0d6efd',
    url='/student/dashboard',
    badge='Courses & Timetable',
    description='Courses, Deadlines, Timetable, AI Tutor & GPA Simulator',
    prefix='/student'
))

registry.register(LifePlannerModule(
    key='finance',
    name='Financial Planner',
    short_name='Finances',
    icon='bi-wallet2',
    color='#0dcaf0',
    url='/finance',
    badge='Wealth & E-Wallets',
    description='E-Wallets, Bank Accounts, Net Worth & AI Statement Ingestion',
    prefix='/finance'
))

registry.register(LifePlannerModule(
    key='life',
    name='Habits & Routines',
    short_name='Habits',
    icon='bi-flower1',
    color='#198754',
    url='/life',
    badge='Habits & Wellness',
    description='Daily routines, habit streaks, wellness checks & streak protection',
    prefix='/life'
))

registry.register(LifePlannerModule(
    key='reports',
    name='Intelligence Reports',
    short_name='Reports',
    icon='bi-newspaper',
    color='#6366f1',
    url='/reports',
    badge='Executive AI Digest',
    description='Morning AI news briefing, weekly macro trends & RSS feeds',
    prefix='/reports'
))

registry.register(LifePlannerModule(
    key='journal',
    name='Journal & Reflection',
    short_name='Journal',
    icon='bi-journal-richtext',
    color='#6f42c1',
    url='/journal',
    badge='Diary & Moods',
    description='Daily reflections, mood tracker, gratitude logs & retrospectives',
    prefix='/journal'
))

registry.register(LifePlannerModule(
    key='career',
    name='Career & Job Tracker',
    short_name='Career',
    icon='bi-briefcase-fill',
    color='#fd7e14',
    url='/career',
    badge='Kanban & Milestones',
    description='Job application Kanban board, resume milestones & interview prep',
    prefix='/career'
))

def get_registered_modules() -> List[LifePlannerModule]:
    return registry.list_all()

def get_workspaces_list() -> List[dict]:
    return registry.to_workspaces_list()

def get_module(key: str) -> Optional[LifePlannerModule]:
    return registry.get(key)
