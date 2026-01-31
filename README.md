# Curate

## The Problem
"Menu Anxiety" is real. Deciding what to eat is already hard, but for people with dietary restrictions or allergies, it can be stressful and dangerous. Existing apps dump raw menus on you, forcing you to play "detective" with ingredients lists.

## The Solution
Curate is an AI concierge that flips the script. It filters menus for safety first (allergens/restrictions) and then uses vector embeddings to find the "vibe" match (taste). It's not just a filter; it's a personalized recommendation engine.

## Tech Stack
*   **Frontend:** Flutter (Mobile & Web)
*   **Backend:** Python (FastAPI)
*   **Database:** PostgreSQL with `pgvector` (Vector Search)
*   **AI:** `sentence-transformers` (Local Embeddings) + OpenRouter (Explanations - Planned)
*   **DevOps:** Docker & Docker Compose

## Current Progress
*   ✅ Backend API with CORS enabled.
*   ✅ PostgreSQL database running in Docker with `vector` extension.
*   ✅ "Safety First" SQL filtering (Verified with Peanut Allergy test).
*   ✅ Flutter Web UI running with dark mode and card layout.
*   🚧 Adaptive Onboarding flow (Work in Progress).

## Quick Start
1.  **Start the Backend & DB:**
    ```bash
    docker-compose up -d
    ```

2.  **Run the App:**
    ```bash
    cd mobile_app
    flutter run
    ```
