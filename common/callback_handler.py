from telegram import Update

from telegram.ext import CallbackContext

from app.callback_resolver import resolver


async def handle_callback(update:Update,context:CallbackContext):
    query = update.callback_query
    splited_data = query.data.split(':')
    data_type = splited_data[0]

    handler = resolver(data_type)
    if not handler:
        await query.answer("Invalid action, please try again.")
        return
    
    await handler(update,context,splited_data[1: ])
    await query.answer()