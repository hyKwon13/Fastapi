from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class Item_name(Base):
    __tablename__ = "items_name"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    position = Column(String, index=True)
    password = Column(String)
    is_admin = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)

class GroupedItem(Base):
    __tablename__ = "grouped_items"
    id = Column(Integer, primary_key=True, index=True)
    vendor = Column(String, index=True)
    cargo_type = Column(String, index=True)
    total_quantity = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    items = relationship("Item", back_populates="grouped_item")

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    vendor = Column(String, index=True)
    address = Column(String, index=True)
    recipient = Column(String, index=True)
    phone_number = Column(String, index=True)
    note = Column(String, index=True)
    product = Column(String, index=True)
    quantity = Column(Integer)
    cargo_type = Column(String)
    status = Column(String, default="출고대기")
    created_at = Column(DateTime, default=datetime.now)
    username = Column(String, index=True)
    position = Column(String, index=True)
    grouped_item_id = Column(Integer, ForeignKey("grouped_items.id"))
    grouped_item = relationship("GroupedItem", back_populates="items")