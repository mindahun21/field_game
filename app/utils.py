"""
This module provides various utility functions for common bot operations,
such as handling callbacks, responding to invalid messages, and cancelling conversations.
"""

import functools
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler


def callback_handler(handler):
    """
    Decorator for callback query handlers to automatically delete the callback message
    after processing. This prevents users from clicking old inline keyboard buttons.

    Args:
        handler: The asynchronous function that processes the callback query.

    Returns:
        The wrapped asynchronous function.
    """
    @functools.wraps(handler)
    async def delete_callback_msg(update:Update, context:ContextTypes,*args,**kwargs):
        error=None
        res=None
        try:
            res=await handler(update,context,*args,**kwargs)
        except Exception as e:
            error=e
        
        await context.bot.delete_message(
            update.effective_user.id,update.callback_query.message.id
        )

        if error:
            raise error
        
        return res
    
    return delete_callback_msg

async def invalid_message(update:Update,context:ContextTypes.DEFAULT_TYPE):
    """
    Handles invalid messages received during a conversation,
    prompting the user to send an appropriate response.
    """
    await update.message.reply_text(
        "Please send an appropriate response. If you want to stop the current operation, please use the /cancel command."
    )


async def cancel_conversation(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """
    Handles the /cancel command, ending the current conversation
    and clearing user-specific data.
    """
    await update.message.reply_text(
        "You have returned to normal bot operations!"
    )
    context.user_data.clear()
    return ConversationHandler.END
