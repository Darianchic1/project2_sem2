from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Favorite(Base):
    __tablename__ = 'favorites'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    recipe_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    image = Column(String)  
    source_url = Column(String) 

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, unique=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    is_banned = Column(Boolean, default=False)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)

class BotStats(Base):
    __tablename__ = 'bot_stats'
    
    id = Column(Integer, primary_key=True)
    total_users = Column(Integer, default=0)
    total_commands = Column(Integer, default=0)
    random_recipe_requests = Column(Integer, default=0)
    ingredient_searches = Column(Integer, default=0)
    favorites_views = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)