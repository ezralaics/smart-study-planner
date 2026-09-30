from extensions import db
from models.user import User
from models.course import Course
from models.task import Task
from models.schedule import Schedule
from models.document import Document
from models.user_ai_config import UserAIConfig
from models.message import DirectMessage
from models.habit import Habit, HabitLog
from models.finance import BudgetGoal, Transaction, FinancialAccount, FinancialTransaction
from models.journal import JournalEntry
from models.career import JobApplication
from models.report import UserInterestSource, DigestReport

__all__ = [
    'db', 'User', 'Course', 'Task', 'Schedule', 'Document', 'UserAIConfig', 
    'DirectMessage', 'Habit', 'HabitLog', 'BudgetGoal', 'Transaction', 
    'FinancialAccount', 'FinancialTransaction',
    'JournalEntry', 'JobApplication', 'UserInterestSource', 'DigestReport'
]
