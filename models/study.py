"""
OmniSuite Domain Model Facade: Study & Academics
Encapsulates Academic Course, Task, and Schedule models.
"""
from models.course import Course
from models.task import Task
from models.schedule import Schedule
from models.study_tip import StudyTip, UserTipInteraction

__all__ = ['Course', 'Task', 'Schedule', 'StudyTip', 'UserTipInteraction']
