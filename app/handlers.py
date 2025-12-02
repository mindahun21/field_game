"""
This module manages the registration and retrieval of bot handlers,
ensuring they are properly organized for the Telegram `Application`.
"""

from typing import List

from telegram.ext import BaseHandler, ConversationHandler, CommandHandler

handlers:List[BaseHandler] =[]

def register_handler(handler:BaseHandler):
    """
    Registers a new handler to be included in the bot's application.

    Args:
        handler: An instance of `telegram.ext.BaseHandler` to be registered.

    Raises:
        ValueError: If the provided handler is not an instance of `BaseHandler`.
    """
    if not isinstance(handler,BaseHandler):
        raise ValueError("handler must be type of BaseHandler")
    
    handlers.append(handler)

def get_handlers() -> List[BaseHandler]:
    """
    Retrieves all registered handlers, sorted by a predefined priority
    (ConversationHandler, then CommandHandler, then others).

    Returns:
        A sorted list of `telegram.ext.BaseHandler` instances.
    """
    return sorted(
        handlers,
        key=lambda handler: 1 if isinstance(handler,ConversationHandler) else 2 if isinstance(handler,CommandHandler) else 3,
    )