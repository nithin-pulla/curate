# Curate

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flutter](https://img.shields.io/badge/Flutter-3.13+-02569B?style=for-the-badge&logo=flutter&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-24.0+-2496ED?style=for-the-badge&logo=docker&logoColor=white)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

## Abstract

**Curate** is an intelligent dining concierge designed to mitigate decision fatigue ("menu anxiety") through a hybrid filtering engine. Unlike traditional discovery platforms that rely solely on collaborative filtering or keyword matching, Curate implements a two-stage recommendation architecture. It prioritizes dietary safety via strict boolean filtering and optimizes for user preference using semantic vector search. By mapping menu item descriptions into high-dimensional space, the system identifies culinary options that validly match a user's "vibe" and taste profile, moving beyond simple tag-based retrieval.

## System Architecture

The solution uses a decoupled client-server architecture designed for scalability and separation of concerns.

### 1. Mobile Client (Presentation Layer)
Built with **Flutter**, the mobile client provides an adaptive UI that services both iOS and Android platforms from a single codebase. It manages local state for the user's dietary profile and interacts with the backend via a RESTful interface.
*   **Key Responsibilities:** User Onboarding, Preference Collection, Result Visualization.

### 2. API Gateway (Application Layer)
The backend is powered by **FastAPI**, chosen for its high-performance asynchronous capabilities and automatic OpenAPI generation. It acts as the orchestration layer, handling authentication, request validation, and the execution of the search algorithms.
*   **Key Features:** Async processing, Pydantic data validation, Dependency Injection.

### 3. Intelligence Engine (Inference Layer)
We utilize `sentence-transformers` (specifically `all-MiniLM-L6-v2`) to generate dense vector embeddings for menu items. This allows the system to understand that a user asking for "spicy comfort food" might enjoy a "Sichuan Beef Noodle Soup" even if the exact keywords don't overlap.

### 4. Data Persistence Strategy
*   **PostgreSQL 15:** Primary relational store for structural data (restaurants, menus, ingredients).
*   **pgvector:** Extension enabled to support vector similarity search directly within the database. This eliminates the need for a separate vector database (like Pinecone or Milvus) for this scale, simplifying infrastructure complexity.

## Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | [![Flutter](https://img.shields.io/badge/Flutter-02569B?style=flat-square&logo=flutter&logoColor=white)](https://flutter.dev) | Cross-platform UI toolkit for high-fidelity rendering. |
| **Backend** | [![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com) | High-performance Python web framework (ASGI). |
| **Database** | [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org) | Advanced ORDBMS with ACID compliance. |
| **Vector Search** | `pgvector` | Open-source vector similarity search for Postgres. |
| **AI/ML** | `sentence-transformers` | Hugging Face library for SOTA sentence embeddings. |
| **DevOps** | [![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com) | Containerization for consistent development and deployment environments. |

## Feature Set

*   **Hybrid Query Execution**:
    1.  **Safety Filter (Hard)**: Executes boolean SQL query to exclude allergens (e.g., `WHERE NOT ingredients @> '{peanuts}'`).
    2.  **Semantic Rank (Soft)**: Performs cosine similarity search on the remaining subset to rank items by taste preference.
*   **Dynamic Onboarding Profile**: Captures granular dietary constraints (Vegan, Gluten-Free, Nut Allergies) and constructs a persistent user profile.
*   **Containerized Environment**: Full `docker-compose` setup ensures the API, Database, and Vector extensions are orchestrated seamlessly.

## Getting Started

### Prerequisites
*   Docker Desktop (with Docker Compose)
*   Flutter SDK 3.10+
*   Python 3.10+ (for local scripts)

### Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/nithinpulla/curate.git
    cd curate
    ```

2.  **Initialize Backend Services**
    Launch the containerized backend and database.
    ```bash
    docker-compose up -d --build
    ```
    *The API will be available at `http://localhost:8000/docs`.*

3.  **Launch Mobile Application**
    Navigate to the mobile directory and run the application.
    ```bash
    cd mobile_app
    flutter pub get
    flutter run
    ```

## Roadmap

*   [ ] **RAG Integration**: Implement Retrieval-Augmented Generation to provide natural language explanations for *why* a dish was recommended.
*   [ ] **User Feedback Loop**: Reinforcement learning from user selection to refine embedding weights.
*   [ ] **Geospatial Indexing**: Integrate PostGIS to filter recommendations by user location.

---
*License: MIT*
