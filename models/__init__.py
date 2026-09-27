from extensions import db
from models.user import User
from models.course import Course
from models.task import Task
from models.schedule import Schedule
from models.document import Document
from models.user_ai_config import UserAIConfig

__all__ = ['db', 'User', 'Course', 'Task', 'Schedule', 'Document', 'UserAIConfig']
