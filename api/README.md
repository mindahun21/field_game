# API Documentation

This directory contains the FastAPI application that serves as the backend for the Field Game. It provides several endpoints for managing game data and interacting with the Telegram bot.

## Core Functionalities

The API is responsible for the following:

*   **Telegram Webhook:** It exposes a `/telegram-webhook` endpoint to receive updates from the Telegram bot. This is the primary way the bot communicates with the backend.
*   **Point Management:** It provides endpoints to update and set points for game participants.
*   **Group Management:** It includes functionality to transfer group ownership and search for groups.

## File Breakdown

*   `main.py`: This is the entry point of the FastAPI application. It initializes the app, sets up CORS middleware, and includes the API router. It also handles the application startup and shutdown events, which are used to set and delete the Telegram bot webhook.
*   `endpoints.py`: This file defines all the API endpoints. It contains the logic for handling requests to update points, transfer group ownership, and search for groups.
*   `models.py`: This file contains the Pydantic models used for request and response validation. These models ensure that the data received by the API is in the correct format.
*   `dependencies.py`: This file defines the dependencies used by the API, such as the database session. It provides a `get_db` function that creates a new database session for each request and closes it when the request is finished.
*   `request.http`: This file contains sample HTTP requests that can be used to test the API endpoints.

## How to Run

To run the API, you can use `uvicorn`:

```bash
uvicorn api.main:app --reload
```
