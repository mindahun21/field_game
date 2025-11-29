"""
This module provides utility functions specific to the Field Game,
such as sending game-related media and photos to users.
"""

from .data import *
from telegram import InputMediaPhoto
import os # Import os for path checking
import logging # Import logging
logger = logging.getLogger(__name__) # Get logger instance


# async def send_photo(context, user_id, rank) -> None:
#     """
#     Sends a specific photo based on rank to a user.

#     Args:
#         context: The ContextTypes.DEFAULT_TYPE object for bot interactions.
#         user_id: The Telegram user ID to send the photo to.
#         rank: The rank used to determine the photo.
#     """
#     # NOTE: Hardcoded path. Consider moving base path to configuration (.env).
#     photo_path = f'anime/anime{rank}.avif'  
#     if os.path.exists(photo_path):
#         with open(photo_path, 'rb') as photo:
#             await context.bot.send_photo(chat_id=user_id, photo=photo, caption="Here's your photo from my PC!")
#     else:
#         # Log an error if photo not found
#         logger.error(f"Photo not found at {photo_path} for user {user_id}")

async def send_photo(context, user_id, path) -> None:
    """
    Sends a specific photo based on rank to a user.

    Args:
        context: The ContextTypes.DEFAULT_TYPE object for bot interactions.
        user_id: The Telegram user ID to send the photo to.
        rank: The rank used to determine the photo.
    """
   
    if os.path.exists(path):
        with open(path, 'rb') as photo:
            await context.bot.send_photo(chat_id=user_id, photo=photo, caption="")
    else:
        # Log an error if photo not found
        logger.error(f"Photo not found at {path} for user {user_id}")


async def send_game5(context, user_id):
    """
    Sends a group of photos for 'Game 5' to a user.

    Args:
        context: The ContextTypes.DEFAULT_TYPE object for bot interactions.
        user_id: The Telegram user ID to send the media group to.
    """
    media = []
    # NOTE: Hardcoded path. Consider moving base path to configuration (.env).
    for i in range(1,8):
        photo_path = f"images/photo_{i}.jpg"
        if os.path.exists(photo_path):
            with open(photo_path, 'rb') as photo:
                media.append(InputMediaPhoto(photo))
        else:
            logger.warning(f"Game 5 photo not found at {photo_path} for user {user_id}")
            
    if media: # Only send if there are photos to send
        await context.bot.send_media_group(chat_id=user_id, media=media)
