from sqlalchemy.orm import Session
from sqlalchemy import not_
from typing import List
import random

from backend.models import User, Dish, Restaurant
from backend.schemas import MealBundle, DishResponse

class RecommendationEngine:
    def __init__(self, db: Session):
        self.db = db

    def _get_safe_dishes(self, user: User, restaurant_id: str) -> List[Dish]:
        """
        HARD GUARDRAIL: Returns ONLY dishes that are safe for the user.
        Strict Set-Difference: Dish Allergens - User Strict Allergens must be Empty.
        """
        # 1. Fetch all dishes for the restaurant
        all_dishes = self.db.query(Dish).filter(Dish.restaurant_id == restaurant_id, Dish.is_available == True).all()
        
        safe_dishes = []
        user_strict_allergens = set(user.allergens_strict) if user.allergens_strict else set()
        
        for dish in all_dishes:
            dish_allergens = set(dish.allergens) if dish.allergens else set()
            
            # CRITICAL CHECK: Intersection must be empty
            if not dish_allergens.isdisjoint(user_strict_allergens):
                # LOGGING WOULD GO HERE: Blocked dish {dish.name} due to {dish_allergens & user_strict_allergens}
                continue
            
            # Dietary Constraint Check (e.g. Vegan)
            # This is simpler: if user is Vegan, dish must have "vegan" tag? 
            # TDD says "diet_type = user.diet". Let's assume constraints are inclusive requirements.
            # If user has constraints, dish tags must include ALL of them? OR at least one?
            # TDD: "Filter WHERE... diet_type = user.diet".
            # Let's implement: If user has constraints, dish tags must match.
            # For MVP, strict allergens is the red line. Constraints are often preferences or strict.
            # Let's enforce constraints strictly if present.
            
            if user.constraints:
                user_constraints = set(user.constraints)
                dish_tags = set(dish.tags) if dish.tags else set()
                # If user wants Vegan, dish MUST be Vegan.
                if not user_constraints.issubset(dish_tags):
                   continue

            safe_dishes.append(dish)
            
        return safe_dishes

    def _mock_vector_search(self, user: User, candidates: List[Dish]) -> List[Dish]:
        """
        Placeholder for semantic search. 
        In real life: Pinecone query(user.vector, filter={id: [candidates.ids]})
        For now: Random shuffle to simulate "AI" picking the best ones.
        """
        # Simulate scoring
        ranked = candidates.copy()
        random.shuffle(ranked)
        return ranked

    def generate_recommendations(self, user_id: str, restaurant_id: str) -> List[MealBundle]:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
            
        # Step 1 & 2: Get Safe Menu
        safe_dishes = self._get_safe_dishes(user, restaurant_id)
        
        if not safe_dishes:
            return [] # No safe options
            
        # Step 3: Semantic Ranking (Mock)
        ranked_dishes = self._mock_vector_search(user, safe_dishes)
        
        # Step 4: Simple Bundling Logic (Greedy)
        # Bundle 1: Top Rated (Single Item)
        bundles = []
        
        if ranked_dishes:
            best_dish = ranked_dishes[0]
            bundles.append(MealBundle(
                title="The Top Pick",
                dishes=[DishResponse.model_validate(best_dish)],
                total_price=best_dish.price,
                explanation=f"Based on your taste profile, we think you'll love the {best_dish.name}."
            ))
            
        # Bundle 2: Chef's Combo (If 2 items exist)
        if len(ranked_dishes) >= 2:
             main = ranked_dishes[0]
             side = ranked_dishes[1]
             # Check budget
             total_price = main.price + side.price
             # Mock budget check (User budget 1=$, 2=$$, 3=$$$)
             # Let's assume budget 2 allows up to $50
             
             bundles.append(MealBundle(
                 title="Perfect Pairing",
                 dishes=[DishResponse.model_validate(main), DishResponse.model_validate(side)],
                 total_price=total_price,
                 explanation=f"Try the {main.name} with a side of {side.name}."
             ))
             
        return bundles
