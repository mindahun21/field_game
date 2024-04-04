from typing import List

from telegram.ext import BaseHandler, ConversationHandler, CommandHandler

handlers:List[BaseHandler] =[]

def register_handler(handler:BaseHandler):
    if not isinstance(handler,BaseHandler):
        raise ValueError("handler must be type of BaseHandler")
    
    handlers.append(handler)

def get_handlers() -> List[BaseHandler]:

    return sorted(
        handlers,
        key=lambda handler: 1 if isinstance(handler,ConversationHandler) else 2 if isinstance(handler,CommandHandler) else 3,
    )

