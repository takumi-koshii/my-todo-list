from sqlalchemy import Column, TIMESTAMP, Integer, String, Date
from sqlalchemy.schema import FetchedValue

from settings import Base


# モデル

# ユーザー情報
class TodoListUser(Base):
    __tablename__ = "todolistuser"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(64), nullable=False)
    password = Column(String(64), nullable=False)
    created_at = Column(TIMESTAMP, FetchedValue())
    updated_at = Column(TIMESTAMP, FetchedValue())


# Todo リストの項目
class TodoListItem(Base):
    __tablename__ = "todolistitem"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, nullable=False)
    content = Column(String(1024), nullable=True)
    deadline = Column(Date)
    created_at = Column(TIMESTAMP, FetchedValue())
    updated_at = Column(TIMESTAMP, FetchedValue())
