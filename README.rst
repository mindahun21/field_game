.. Field Game Bot documentation master file, created by
   sphinx-quickstart on Tue Dec  2 12:45:21 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Field Game Bot's documentation!
============================================

This is the documentation for the Field Game Bot, a Telegram bot that facilitates a real-life field game. This document provides a comprehensive overview of the project, its components, and instructions for installation and usage.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Project Overview
----------------

The Field Game Bot is a Telegram-based application designed to manage a field game. It allows users to register as groups, participate in a series of challenges, and compete for points. The bot provides a set of commands for users to interact with the game, and for administrators to manage the game's progress.

Components
----------

The project is divided into several components, each with a specific responsibility:

*   **api:** A FastAPI application that provides a RESTful API for managing game data. It includes endpoints for updating points, transferring group ownership, and searching for groups.
*   **app:** This directory contains the core application logic, including database models, utility functions, and handlers for Telegram bot commands.
*   **common:** This directory contains common command handlers that are not specific to any particular game or feature, such as the `/start` and `/help` commands.
*   **field_game:** This directory contains the core game logic, including the game flow, data, and utility functions.
*   **mini_app:** A React-based mini-app that provides a user interface for administrators and game administrators to manage the game.

Functionalities
---------------

The Field Game Bot offers the following functionalities:

*   **User Registration:** Users can register for the game by providing a unique group name.
*   **Game Progression:** Users can progress through the game by entering codes that they receive after completing each challenge.
*   **Point Management:** Administrators and game administrators can update the points of each group using the mini-app.
*   **Role-Based Access Control:** The bot's commands and the mini-app's features are restricted based on the user's role (USER, GAME_ADMIN, or ADMIN).
*   **Real-time Results:** Administrators can view the real-time results of the game, including the ranking of each group.

Installation
------------

To install and run the Field Game Bot, follow these steps:

1.  **Clone the repository:**

    .. code-block:: shell

       git clone https://github.com/mindahun21/field_game.git
       cd field_game

2.  **Create and activate a virtual environment:**

    It is highly recommended to use a virtual environment to manage project dependencies.

    .. code-block:: shell

       python3 -m venv venv
       source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

3.  **Install the dependencies:**

    .. code-block:: shell

       pip install -r requirements.txt

4.  **Set up the environment variables:**

    Create a ``.env`` file in the project's root directory and add the following variables:

    .. code-block:: shell

       API_KEY='your_telegram_bot_token'
       WEBHOOK_URL='your_ngrok_webhook_url'
       WEBHOOK_SECRET='your_webhook_secret'
       MINI_APP_BASE_URL='your_mini_app_base_url'

    **Note on WEBHOOK_URL:** Telegram webhooks require an HTTPS connection. You can use tools like `ngrok` to expose your local FastAPI server (which runs on port 8000 by default) to the internet via a secure HTTPS tunnel.

    To get your `WEBHOOK_URL` and `WEBHOOK_SECRET` using `ngrok`:

    a.  Install ngrok (if you haven't already): `snap install ngrok`
    b.  Run ngrok for port 8000: `ngrok http 8000`
    c.  ngrok will provide an HTTPS URL (e.g., `https://xxxx-yyyy-zzzz.ngrok-free.app`). Use this as your `WEBHOOK_URL`.
    d.  Choose a strong, random string for `WEBHOOK_SECRET`.

5.  **Run the application:**

    First, start the FastAPI backend (which will run on port 8000):

    .. code-block:: shell

       uvicorn api.main:app --host 0.0.0.0 --port 8000

    In a separate terminal, start the Telegram bot:

    .. code-block:: shell

       python main.py

Testing
-------

To run the tests for the Field Game Bot, you can use the following command:

.. code-block:: shell

   pytest

This will discover and run all the tests in the `tests/` directory.

License
-------

This project is licensed under the MIT License. See the `LICENSE` file for more details.
