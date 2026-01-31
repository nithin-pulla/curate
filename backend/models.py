from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, Boolean, Text
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import ARRAY
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)  # UUID
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # User Profile Data
    constraints = Column(ARRAY(String), default=[])  # e.g. ["vegan", "gluten_free"]
    allergens_strict = Column(ARRAY(String), default=[])  # e.g. ["peanuts", "shellfish"]
    spice_tolerance = Column(Integer, default=0)  # 0-5
    budget_setting = Column(Integer, default=2)  # 1: Cheap, 2: Moderate, 3: Expensive
    
    # Vector Embedding for Taste
    taste_embedding = Column(Vector(1536))  # Dimensions depend on model, assuming OpenAI for now

class Restaurant(Base):
    __tablename__ = 'restaurants'
    
    id = Column(String, primary_key=True) # UUID
    name = Column(String, nullable=False)
    address = Column(String)
    owner_id = Column(String, nullable=False) # Link to auth user who owns this
    
    dishes = relationship("Dish", back_populates="restaurant")

class Dish(Base):
    __tablename__ = 'dishes'
    
    id = Column(String, primary_key=True) # UUID
    restaurant_id = Column(String, ForeignKey('restaurants.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    
    # Dietary Info
    ingredients = Column(ARRAY(String), default=[])
    allergens = Column(ARRAY(String), default=[]) # e.g. ["peanuts", "milk"]
    tags = Column(ARRAY(String), default=[]) # e.g. ["spicy", "comfort_food"]
    
    calories = Column(Integer)
    spice_level = Column(Integer) # 0-5
    is_available = Column(Boolean, default=True)
    
    # Vector Embedding for Dish
    embedding = Column(Vector(1536))
    
    restaurant = relationship("Restaurant", back_populates="dishes")
