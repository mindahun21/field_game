from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .endpoints import router
import logging
from main import application
from telegram import Update
# Removed: from dotenv import dotenv_values
from app.config import config # NEW: Import config from app.config

app = FastAPI()

logger = logging.getLogger(__name__)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    """
    Handles FastAPI application startup events.
    Sets the Telegram bot webhook and initializes the application.
    """
    logger.info("FastAPI app starting up. Setting webhook for Telegram bot.")
    
    await application.initialize()

    # Removed: config = dotenv_values(".env")
    WEBHOOK_URL = config["WEBHOOK_URL"]
    WEBHOOK_SECRET = config["WEBHOOK_SECRET"]
    
    await application.bot.set_webhook(url=WEBHOOK_URL, secret_token=WEBHOOK_SECRET)
    logger.info(f"Webhook set to: {WEBHOOK_URL}")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Handles FastAPI application shutdown events.
    Deletes the Telegram bot webhook.
    """
    logger.info("FastAPI app shutting down. Deleting webhook for Telegram bot.")
    await application.bot.delete_webhook()
    logger.info("Webhook deleted.")

@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    """
    Receives and processes incoming Telegram updates via webhook.

    Args:
        request: The incoming FastAPI Request object.

    Returns:
        A dictionary with a "message": "ok" to acknowledge receipt of the update.
    """
    raw_body = await request.json()
    update = Update.de_json(raw_body, application.bot)
    await application.process_update(update)
    return {"message": "ok"}