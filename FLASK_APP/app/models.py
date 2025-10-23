from .extensions import db
import datetime
from .enum_models import TransactionType, FrequencyEnum
from flask_login import UserMixin

# --------------------
# User
# --------------------
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)

    side_projects = db.relationship("SideProject", back_populates="user", cascade="all, delete-orphan")
    categories = db.relationship("Category", back_populates="user", cascade="all, delete-orphan")
    planned_transactions = db.relationship("PlannedTransaction", back_populates="user", cascade="all, delete-orphan")
    actual_transactions = db.relationship("ActualTransaction", back_populates="user", cascade="all, delete-orphan")
    user_info = db.relationship("UserInfo", back_populates="user", uselist=False, cascade="all, delete-orphan")


# --------------------
# SideProject
# --------------------
class SideProject(db.Model):
    __tablename__ = 'side_projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    target_budget = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship("User", back_populates="side_projects")
    planned_transactions = db.relationship("PlannedTransaction", back_populates="side_project", cascade="all, delete-orphan")
    actual_transactions = db.relationship("ActualTransaction", back_populates="side_project", cascade="all, delete-orphan")


# --------------------
# Category / SubCategory
# --------------------
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    created_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship("User", back_populates="categories")
    sub_categories = db.relationship("SubCategory", back_populates="category", cascade="all, delete-orphan")
    planned_transactions = db.relationship("PlannedTransaction", back_populates="category", cascade="all, delete-orphan")
    actual_transactions = db.relationship("ActualTransaction", back_populates="category", cascade="all, delete-orphan")


class SubCategory(db.Model):
    __tablename__ = 'sub_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    created_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    category = db.relationship("Category", back_populates="sub_categories")
    planned_transactions = db.relationship("PlannedTransaction", back_populates="sub_category", cascade="all, delete-orphan")
    actual_transactions = db.relationship("ActualTransaction", back_populates="sub_category", cascade="all, delete-orphan")



# --------------------
# Account
# --------------------
class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), default='Conto principale')
    currency = db.Column(db.String(10), default='EUR')

    initial_balance = db.Column(db.Float, default=0.0)
    current_balance = db.Column(db.Float, default=0.0)

    created_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship("User", backref=db.backref("accounts", cascade="all, delete-orphan"))

    # Collegamento opzionale alle transazioni
    planned_transactions = db.relationship("PlannedTransaction", back_populates="account", cascade="all, delete-orphan")
    actual_transactions = db.relationship("ActualTransaction", back_populates="account", cascade="all, delete-orphan")

# --------------------
# PlannedTransaction
# --------------------
class PlannedTransaction(db.Model):
    __tablename__ = 'planned_transactions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)

    planned_amount = db.Column(db.Integer, nullable=False)

    # Date columns: use date (not datetime); default as date.today
    planned_date_start = db.Column(db.Date, default=datetime.date.today, nullable=False)
    planned_date_end = db.Column(db.Date)

    transaction_type = db.Column(
        db.Enum(TransactionType, name="transaction_type_enum", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False
    )

    frequency = db.Column(
        db.Enum(FrequencyEnum, name="frequency_enum", values_callable=lambda obj: [e.value for e in obj])
    )

    recurring = db.Column(db.Boolean, nullable=False, default=False)
    priority_score = db.Column(db.Integer, nullable=False, default=1)

    is_completed = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # FK
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    sub_category_id = db.Column(db.Integer, db.ForeignKey('sub_categories.id'), nullable=False)
    side_project_id = db.Column(db.Integer, db.ForeignKey('side_projects.id'), nullable=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)
    
    account = db.relationship("Account", back_populates="planned_transactions")   
    user = db.relationship("User", back_populates="planned_transactions")
    category = db.relationship("Category", back_populates="planned_transactions")
    sub_category = db.relationship("SubCategory", back_populates="planned_transactions")
    side_project = db.relationship("SideProject", back_populates="planned_transactions")
    actual_transactions = db.relationship("ActualTransaction", back_populates="planned", cascade="all, delete-orphan")


# --------------------
# ActualTransaction
# --------------------
class ActualTransaction(db.Model):
    __tablename__ = 'actual_transactions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    actual_amount = db.Column(db.Integer, nullable=False)

    actual_date_start = db.Column(db.Date, default=datetime.date.today, nullable=False)
    actual_date_end = db.Column(db.Date)

    created_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Reuse same field names (no "actual_" prefix required for enums) or keep them — here keep generic names for clarity
    transaction_type = db.Column(  # this is the actual transaction type
        db.Enum(TransactionType, name="transaction_type_enum", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False
    )

    frequency = db.Column(
        db.Enum(FrequencyEnum, name="frequency_enum", values_callable=lambda obj: [e.value for e in obj])
    )

    recurring = db.Column(db.Boolean, nullable=False, default=False)
    priority_score = db.Column(db.Integer, nullable=False, default=1)

    # FK
    planned_id = db.Column(db.Integer, db.ForeignKey('planned_transactions.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    sub_category_id = db.Column(db.Integer, db.ForeignKey('sub_categories.id'), nullable=False)
    side_project_id = db.Column(db.Integer, db.ForeignKey('side_projects.id'), nullable=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)
    
    
    account = db.relationship("Account", back_populates="actual_transactions") 
    planned = db.relationship("PlannedTransaction", back_populates="actual_transactions")
    user = db.relationship("User", back_populates="actual_transactions")
    category = db.relationship("Category", back_populates="actual_transactions")
    sub_category = db.relationship("SubCategory", back_populates="actual_transactions")
    side_project = db.relationship("SideProject", back_populates="actual_transactions")


# --------------------
# UserInfo
# --------------------
class UserInfo(db.Model):
    __tablename__ = 'user_infos'
    id = db.Column(db.Integer, primary_key=True)
    salary = db.Column(db.Integer, nullable=False)
    where_live = db.Column(db.String)
    life_style = db.Column(db.String)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship("User", back_populates="user_info")



