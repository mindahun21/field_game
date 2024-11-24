from .data import *
from telegram import InputMediaPhoto



async def send_photo(context,user_id,rank) -> None:
    photo_path = f'anime/anime{rank}.avif'  
    with open(photo_path, 'rb') as photo:
        await context.bot.send_photo(chat_id=user_id, photo=photo, caption="Here's your photo from my PC!")


async def send_game3(context,user_id):
    media = []
    for i in range(1,9):
        with open(f"anime/photo_{i}_2024-10-21_09-54-40.jpg", 'rb') as photo:
            media.append(InputMediaPhoto(photo))
    
    await context.bot.send_media_group(chat_id=user_id,media=media)