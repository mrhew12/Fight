# Development Sprint Plan: SpriteShift AI

This document outlines a high-level, six-sprint development plan to take SpriteShift AI from concept to a functional MVP. Each sprint is assumed to be two weeks long.

---

## Sprint 1: Foundation & Core Infrastructure

**Goal:** Establish the foundational infrastructure and developer tooling. No user-facing features will be built in this sprint.

**Key Tasks:**
-   **Project Setup:** Initialize Git repository and set up branch policies.
-   **CI/CD Pipeline:** Create a basic continuous integration and deployment pipeline (e.g., using GitHub Actions) to build and test the services.
-   **Microservice Scaffolding:** Create the skeleton projects for all backend services (Orchestrator, Auth, Inference, etc.) with basic health check endpoints.
-   **Containerization:** Write initial `Dockerfile`s for each service.
-   **API Contracts:** Define the initial OpenAPI/gRPC specifications for communication between services.
-   **Infrastructure as Code:** Set up initial Terraform or Pulumi scripts for cloud resources (e.g., object storage bucket, database).

---

## Sprint 2: User Management & Basic Upload

**Goal:** Implement the core user authentication and the ability to upload an image.

**Key Tasks:**
-   **Auth Service:** Implement user registration, login, and JWT generation.
-   **Database Schema:** Finalize the initial database schema for users and projects.
-   **Orchestrator:** Create the initial endpoint to receive an upload request.
-   **File Upload Logic:** Implement the logic to securely upload a user's image to the Object Storage bucket.
-   **API Gateway:** Configure routing for the new auth and upload endpoints.

---

## Sprint 3: End-to-End Pipeline (Happy Path)

**Goal:** Achieve the first successful, end-to-end run of the AI pipeline.

**Key Tasks:**
-   **Job Queue Integration:** Integrate the Orchestrator and worker services with the job queue (e.g., RabbitMQ).
-   **Inference Service (MVP):** Implement the `rembg` and `AnimateDiff` steps. Focus on making it work for a single, well-behaved input image.
-   **Orchestrator Logic:** Implement the state machine to manage a job's lifecycle (e.g., `UPLOADED` -> `PROCESSING` -> `COMPLETED`).
-   **Media Pipeline Service (MVP):** Implement a simple pass-through for the generated animation.
-   **Result Storage:** Save the output (e.g., a GIF) back to Object Storage.

---

## Sprint 4: Asset Generation & Godot Integration

**Goal:** Produce game-engine-ready assets and prove they work in a sample project.

**Key Tasks:**
-   **Sprite Sheet Generation:** In the Media Pipeline Service, add logic to pack the generated animation frames into a single sprite sheet.
-   **Metadata Generation:** Create the JSON output file with animation names, frame timings, and hitbox data (even if hitboxes are just placeholders for now).
-   **Hitbox Generation:** Implement the algorithmic hitbox generation from Step 4 of the AI Pipeline doc.
-   **Sample Godot Project:** Create a new Godot project.
-   **Godot Integration Script:** Write a GDScript (`.gd`) file in the sample project that can read the JSON metadata and use the sprite sheet to play back the animations on a `Sprite2D` node.

---

## Sprint 5: Web Frontend & User Experience

**Goal:** Build the user interface for the platform.

**Key Tasks:**
-   **Frontend Framework Setup:** Initialize a new project using a framework like React, Vue, or Svelte.
-   **User Authentication Flow:** Build the login and registration pages.
-   **Upload Interface:** Create the UI for users to upload their character images.
-   **Project Gallery:** Develop a dashboard where users can see their past and current character generation jobs.
-   **Results Viewer:** Create a component to display the final sprite sheet and play a preview of the generated animations.
-   **Connect to Backend:** Integrate the frontend with the API Gateway to make authenticated requests.

---

## Sprint 6: Billing & Production Readiness

**Goal:** Implement monetization and prepare the platform for public launch.

**Key Tasks:**
-   **Billing Service:** Integrate with Stripe to handle monthly subscriptions.
-   **Tiered Feature Logic:** Implement the logic to enforce feature differences between Free and Pro tiers (e.g., resolution limits, watermarks).
-   **Job Prioritization:** Implement priority queues in the job system to process Pro users' jobs first.
-   **Logging & Monitoring:** Set up structured logging for all services and create a monitoring dashboard (e.g., in Grafana) to track system health and performance.
-   **Final Testing & Bug Fixes:** Conduct end-to-end testing and address any critical bugs before launch.
