import functools
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler


def callback_handler(handler):
    @functools.wraps(handler)
    async def delete_callback_msg(update:Update, context:ContextTypes,*args,**kwargs):
        error=None
        res=None
        try:
            res=await handler(update,context,*args,**kwargs)
        except Exception as e:
            error=e
        
        await context.bot.delete_message(
            update.effective_chat.id,update.callback_query.message.id
        )

        if error:
            raise error
        
        return res
    
    return delete_callback_msg

async def invalid_message(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "please send appropriate response, if you want to return to normal bot operations, please use /cancel command."
    )


async def cancel_conversation(update:Update, context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "now you are returned to the normal bot operations!"
    )
    return ConversationHandler.END