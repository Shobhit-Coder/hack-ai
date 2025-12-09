# Interview AI - Backend Service

This is the backend service for the **Interview AI** platform, a sophisticated, AI-powered system designed to automate and enhance the initial candidate screening process. Built with Django and Django REST Framework, it provides a robust, scalable, and secure foundation for managing jobs, candidates, and automated SMS-based interviews.

**Live API Endpoint**: `https://my-django-backend.azurewebsites.net/`

---

## Table of Contents

- [Architectural Overview](#architectural-overview)
- [Core Features](#core-features)
- [Why This Architecture?](#why-this-architecture)
  - [The Power of Django](#the-power-of-django)
  - [Scalability and Concurrency](#scalability-and-concurrency)
  - [Modular and Reusable Design](#modular-and-reusable-design)
- [Technology Stack](#technology-stack)
- [Deployment & CI/CD](#deployment--cicd)
- [API Structure](#api-structure)
- [Getting Started](#getting-started)

---

## Architectural Overview

The backend is designed as a modular, service-oriented monolith using the Django framework. This architecture provides a perfect balance of rapid development, maintainability, and scalability.

- **Modular Design**: The application is broken down into logical Django "apps":
  - `jobs`: Manages job postings.
  - `candidates`: Manages candidate profiles and resumes.
  - `interviews`: Orchestrates the entire automated SMS interview flow.
  - `dashboard`: Provides aggregated analytics for system monitoring.
- **Database**: Utilizes PostgreSQL, a powerful and reliable relational database, suitable for handling complex relationships between jobs, candidates, and interviews.
- **External Services Integration**:
  - **Twilio**: For handling all SMS communications, including a webhook for real-time, two-way messaging.
  - **Azure Blob Storage**: For secure and scalable storage of candidate resumes.
  - **Google Gemini AI**: For advanced, real-time analysis of interview responses and post-interview scoring.
- **Containerization**: The entire application is containerized using Docker, ensuring consistent development, testing, and production environments.

## Core Features

- **Automated SMS Interviews**: Conducts preliminary interviews via SMS, asking a series of predefined questions and capturing candidate responses.
- **AI-Powered Scoring**: Automatically triggers a background task upon interview completion to score the candidate's performance using Google's Gemini model, providing a "Job Fit Score".
- **Real-time Interview Monitoring**: Intelligently detects if a candidate is struggling (e.g., answering "I don't know") and can be configured to reschedule the interview to ensure a fair evaluation.
- **Centralized Dashboard**: An API endpoint that delivers key metrics like interview completion rates, average scores, and active sessions, enabling a high-level overview of the platform's activity.
- **Robust Data Management**: Full CRUD capabilities for jobs, candidates, and their associated data.
- **Built-in Admin Panel**: A comprehensive, secure, and highly configurable admin interface, provided out-of-the-box by Django, for easy data management and system oversight.

## Why This Architecture?

This backend is not just a collection of endpoints; it's a well-architected system designed for efficiency, scalability, and security.

### The Power of Django

Django is the ideal framework for this project for several reasons:

- **"Batteries-Included"**: Django provides built-in features for authentication, an admin panel, an ORM (Object-Relational Mapper), and security protections (CSRF, XSS), drastically reducing development time.
- **Scalability**: Used by giants like Instagram and Spotify, Django is proven to handle high traffic and large data volumes.
- **Security**: Django has built-in protections against common web vulnerabilities, making the application secure by default. The admin panel is a testament to this, providing granular access control.
- **ORM**: Django's ORM abstracts away direct SQL, preventing SQL injection and making database interactions Pythonic and straightforward.

### Scalability and Concurrency

The system is designed to handle numerous concurrent operations gracefully:

- **Multiple Interviews**: Each interview runs as an independent process, identified by the candidate's phone number. The webhook architecture is stateless and can process thousands of incoming messages simultaneously.
- **Multiple Resumes**: Resume uploads are offloaded to Azure Blob Storage, a highly scalable cloud storage solution. This keeps the application server light and responsive.
- **Asynchronous Processing**: Computationally expensive tasks, like AI-based interview scoring, are run in background threads. This ensures the main application remains responsive and can immediately process the next request without waiting for the AI model to finish.

### Modular and Reusable Design

The use of Django Apps (`jobs`, `candidates`, etc.) makes the codebase exceptionally clean and reusable. Each app is a self-contained unit of functionality. This means:

- **Easy Maintenance**: Finding and fixing bugs is straightforward.
- **Reusability**: The `jobs` or `candidates` app could be lifted and reused in another HR-related project with minimal modification.
- **Parallel Development**: Different teams could work on different apps simultaneously without conflict.

## Technology Stack

- **Framework**: Django, Django REST Framework
- **Database**: PostgreSQL
- **Web Server**: Gunicorn
- **SMS**: Twilio
- **AI/ML**: Google Gemini
- **File Storage**: Azure Blob Storage
- **Containerization**: Docker

## Deployment & CI/CD

The backend is deployed as a containerized application on **Azure App Service**, providing a scalable and managed hosting environment.

A CI/CD pipeline (e.g., using GitHub Actions or Azure DevOps) is configured to automate the deployment process:

1.  **Push to `main`**: A developer pushes new code to the `main` branch.
2.  **Build**: The pipeline automatically builds a new Docker image.
3.  **Test**: Automated tests are run against the new build.
4.  **Deploy**: If tests pass, the new image is pushed to a container registry and deployed to the Azure App Service, ensuring zero-downtime updates.

This setup guarantees that the live service at `https://my-django-backend.azurewebsites.net/` is always running the latest, most stable version of the code.

## API Structure

The API is versioned and organized by resource:

- `/api/jobs/`: Manage job postings.
- `/api/candidates/`: Manage candidates and resumes.
- `/api/interviews/`: Manage and track interviews.
- `/api/dashboard/`: Access analytical data.

## Getting Started

To run the project locally, ensure you have Docker and Docker Compose installed.

1.  **Clone the repository.**
2.  **Create a `.env` file** in the `backend` directory with the necessary environment variables (see `.env.example`).
3.  **Run the application:**
    ```bash
    docker-compose up --build
    ```
4.  The API will be available at `http://localhost:8000`.
