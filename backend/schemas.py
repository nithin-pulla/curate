from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Any
from enum import Enum
from uuid import UUID
from datetime import datetime

# Enums for Strict Validation
class AllergenEnum(str, Enum):
    PEANUTS = "peanuts"
    SHELLFISH = "shellfish"
    DAIRY = "dairy"
    GLUTEN = "gluten"
    EGGS = "eggs"
    SOY = "soy"
    TREE_NUTS = "tree_nuts"
    FISH = "fish"
    # Add more as needed based on TDD usually, but these are updated standard attributes

class DietaryConstraintEnum(str, Enum):
    VEGAN = "vegan"
    VEGETARIAN = "vegetarian"
    GLUTEN_FREE = "gluten_free"
    HALAL = "halal"
    KOSHER = "kosher"
    KETO = "keto"
    PALEO = "paleo"

# Base Schemas
class DishBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    ingredients: Optional[List[str]] = []
    
    # Relaxing Enum for MVP AI output compatibility
    allergens: Optional[List[str]] = []
    
    tags: Optional[List[str]] = []
    calories: Optional[int] = None
    spice_level: int = Field(default=0, ge=0, le=5) # 0-5 scale
    is_available: bool = True

class DishCreate(DishBase):
    restaurant_id: str # UUID string

class DishResponse(DishBase):
    id: str
    restaurant_id: str
    
    class Config:
        from_attributes = True

class RestaurantBase(BaseModel):
    name: str
    address: Optional[str] = None

class RestaurantCreate(RestaurantBase):
    owner_id: str

class RestaurantResponse(RestaurantBase):
    id: str
    owner_id: str
    dishes: List[DishResponse] = []
    
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr
    constraints: List[DietaryConstraintEnum] = []
    allergens_strict: List[AllergenEnum] = []
    spice_tolerance: int = Field(default=0, ge=0, le=5)
    budget_setting: int = Field(default=2, ge=1, le=3)

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    # hashed_password is NOT returned

    class Config:
        from_attributes = True

class MealBundle(BaseModel):
    title: str
    dishes: List[DishResponse]
    total_price: float
    explanation: str

class RecommendationRequest(BaseModel):
    user_id: str
    restaurant_id: str
    hunger_level: Optional[str] = None
    mood: Optional[str] = None

class UserOnboardingRequest(BaseModel):
    name: str
    email: EmailStr
    preferences: str
    allergens: List[str] = []
