# Curate: AI-Powered Dining Concierge

Curate is a full-stack dining assistant utilizing vector embeddings for personalized menu recommendations. It solves the "choice paralysis" problem in dining by filtering for strict dietary constraints (allergies/restrictions) via structured SQL queries, while simultaneously optimizing for taste preferences using semantic vector search.

The system is built with a **Flutter** mobile application and a **FastAPI** backend, leveraging **PostgreSQL** with the `pgvector` extension for efficient similarity search.

## System Architecture

The application follows a client-server architecture:

1.  **Mobile Client (Flutter):** Handles user interaction, onboarding flow (dietary profile creation), and presenting menu recommendations.
2.  **API Layer (FastAPI):** Exposes RESTful endpoints for user management and menu retrieval. Orchestrates the hybrid search logic.
3.  **Data Layer (PostgreSQL + pgvector):**
    *   **Relational Data:** Stores restaurants, menu items, and structured ingredient tags for hard filtering (e.g., "contains peanuts").
    *   **Vector Embeddings:** Stores high-dimensional embeddings of menu item descriptions (generated via `sentence-transformers`) to enable semantic "vibe" matching.

## Technology Stack

*   **Frontend:** Flutter (Dart) - targeting iOS & Android.
    *   Key packages: `http`, `provider` (state management).
*   **Backend:** Python 3.10+ with FastAPI.
    *   **ORM:** SQLAlchemy (Async).
    *   **ML/AI:** `sentence-transformers` (all-MiniLM-L6-v2) for generating local embeddings.
    *   **Serialization:** Pydantic models.
*   **Database:** PostgreSQL 15+.
    *   Extension: `pgvector` for vector similarity search (IVFFlat indexing capabilities).
*   **Infrastructure:** Docker & Docker Compose for containerized development and deployment.
    *   Containers: `backend` (API), `db` (Postgres).

## Key Features

*   **Hybrid Filtering Engine:**
    *   *Stage 1 (Hard Filter):* SQL `WHERE` clauses eliminate unsafe items based on user allergy profile.
    *   *Stage 2 (Soft Rank):* Cosine similarity search against user preference text vectors ranks the remaining safe items.
*   **Dynamic Onboarding:** Assessment used to build a comprehensive user profile storing specific allergens (Peanuts, Dairy, Gluten, etc.) and dietary choice (Vegan, Vegetarian).
*   **Production-Ready API:** Fully typed Async endpoints with automatic Swagger/OpenAPI documentation (`/docs`).

## Deployment & Setup

### Prerequisites
*   Docker & Docker Compose
*   Flutter SDK (3.x+)

### 1. Database & Backend Initialization
The backend services are containerized. Use Docker Compose to spin up the Postgres instance (with vector support) and the FastAPI service.

```bash
# Start services in detached mode
docker-compose up -d --build

# Verify containers are running
docker ps
```

*The API will be available at `http://localhost:8000`.*
*Swagger UI: `http://localhost:8000/docs`*

### 2. Frontend Application
Run the Flutter mobile application. Ensure you have an emulator running or a physical device connected.

```bash
cd mobile_app
flutter pub get
flutter run
```

*Note: The app is configured to connect to `localhost` for iOS simulators and `10.0.2.2` for Android emulators automatically.*

## License

[MIT](LICENSE)
