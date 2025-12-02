# Common Handlers

This directory contains common command handlers for the Telegram bot that are not specific to any particular game or feature.

## Core Functionalities

The handlers in this directory are responsible for the following:

*   **Handling callback queries:** The `callback_handler.py` module provides a generic handler for all callback queries from the Telegram bot. It parses the callback data and calls the appropriate handler based on the data type.
*   **Providing help:** The `help.py` module defines the `/help` command handler. This handler sends a message to the user with a list of available commands based on their role (USER, GAME_ADMIN, or ADMIN).
*   **Starting the bot:** The `start.py` module contains the `/start` command handler. This handler is responsible for registering new users in the database and sending them a welcome message.

## File Breakdown

*   `callback_handler.py`: This module contains the main callback handler for the bot. It uses a resolver to determine which handler to call for a given callback query.
*   `help.py`: This module defines the `/help` command handler, which provides users with a list of available commands.
*   `start.py`: This module defines the `/start` command handler, which is the first command that new users interact with. It is responsible for creating a new user in the database.
