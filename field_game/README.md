# Field Game Logic

This directory contains the core logic for the Field Game, including the game flow, data, and utility functions.

## Core Functionalities

The code in this directory is responsible for the following:

*   **Game Flow:** The `game.py` module defines the main conversation handler for the game. It manages the user's state as they progress through the game, from registering their group to entering codes and completing challenges.
*   **Game Data:** The `data.py` module contains a `Game` class that holds all the static data for the game. This includes the game rules, the list of valid codes, the puzzles for each game, and the list of administrators.
*   **Game Utilities:** The `utils.py` module provides utility functions that are used by the game logic, such as functions for sending photos to users.

## File Breakdown

*   `game.py`: This is the heart of the game. It contains the `ConversationHandler` that manages the game's state machine. It also defines all the command handlers for the bot, including `/start`, `/reset`, `/result`, and `/update_point`.
*   `data.py`: This module centralizes all the game's data into a single `Game` class. This makes it easy to manage and modify the game's content without having to change the game logic.
*   `utils.py`: This module contains helper functions that are used by the game. For example, it has a function for sending photos to users, which is used to send the game's image-based puzzles.
