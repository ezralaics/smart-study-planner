"""
OmniSuite Domain Model Facade: Study & Academics
Encapsulates Academic Course, Task, and Schedule models.
"""
from models.course import Course
from models.task import Task
from models.schedule import Schedule

__all__ = ['Course', 'Task', 'Schedule']
