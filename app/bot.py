import logging
import os
from datetime import datetime, timedelta
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
from utils import validate_email, codes_match, generate_code, create_access_token, send_email
from bot_messages import messages, get_email_body
from schemas import UserCreate, UserUpdate
from users import get_user_by_telegram_id, create_user
from dotenv import load_dotenv
from db import SessionLocal

import httpx

httpx_logger = logging.getLogger("httpx")
httpx_logger.disabled = True

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

token = os.getenv("BOT_TOKEN")
bot = Bot(token=token)


# States
USER_CHECK, EMAIL_VALIDATION, CODE_VERIFICATION, CODE_EXPIRED, AUTHORIZED = range(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("User %s started the bot", update.message.from_user.id)
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=(
            "Bienvenido a la comunidad de Matemáticas de la UNED."
        ))
    
    telegram_id = update.message.from_user.id
    # We check if the user is already in the db
    user = await get_user_by_telegram_id(telegram_id)
    if user is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text= (
                "Veo que todavía no has iniciado sesión. \n"

                "Para continuar, necesito tu correo electrónico de la UNED. Tiene que ser un correo terminado en '@alumno.uned.es'. \n"

                "¿Podrías introducirlo a continuación?"
            )
        )
        return EMAIL_VALIDATION
    else:
        context.user_data["access_token_active?"] = user.access_token_expires_at > datetime.now()

        if context.user_data["access_token_active?"]:
            context.user_data["authorized"] = True

            await send_authorized_message(update, context)

            return AUTHORIZED  
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, 
                    text=(

                        "Parece que tu sesión ha expirado. \n"

                        f"Recibirás en tu correo {context.user_data["email"]} un código de 6 cifras iniciar sesión de nuevo. \n"

                        "Si no lo recibes, comprueba tu bandeja de spam. \n"

                        "Por favor, introduce el código a continuación. \n"

                    ))

            generated_code = await generate_code()
            context.user_data["generated_code"] = generated_code
            user_email = context.user_data["email"]
            send_email(user_email, "Código de verificación Mates UNED", get_email_body(generated_code[0]))
            return CODE_EXPIRED

# EMAIL VALIDATION
async def get_user_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text
    logger.info("Email received: %s", email)
    if validate_email(email):
        logger.info("Email is valid")
        context.user_data["email"] = email
        await context.bot.send_message(chat_id=update.effective_chat.id, 
        text=(

        "Muchas gracias. Tu correo es válido. \n"

        "En breves momentos recibirás en tu correo un código de 6 cifras para verificar que eres estudiante. Si no lo recibes, comprueba tu bandeja de spam. \n"

        "Por favor, introduce el código a continuación. \n"

        ))

        generated_code = await generate_code()
        context.user_data["generated_code"] = generated_code
        user_email = context.user_data["email"]
        send_email(user_email, "Código de verificación Mates UNED", get_email_body(generated_code[0]))
        return CODE_VERIFICATION
    else:
        logger.info("Email is not valid")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=messages["invalid_email_message"])

# CODE VERIFICATION
async def verify_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input_code = update.message.text
    generated_code = context.user_data["generated_code"][0]
    code_expires_at = context.user_data["generated_code"][1]
    user_email = context.user_data["email"]
    if codes_match(update.message.from_user.id, generated_code, user_input_code) and datetime.now() < code_expires_at:
        access_token = create_access_token()
        new_user = UserCreate(
            email=user_email,
            telegram_id=update.message.from_user.id,
            access_token=access_token,
            access_token_expires_at=datetime.now() + timedelta(days=180)
        )
        user = await create_user(new_user)

        logger.info("New user created: %s", user)

        context.user_data["authorized"] = True

        await send_authorized_message(update, context)

        return AUTHORIZED

# CODE EXPIRED
async def reverify_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input_code = update.message.text
    generated_code = context.user_data["generated_code"][0]
    code_expires_at = context.user_data["generated_code"][1]
    if codes_match(update.message.from_user.id, generated_code, user_input_code) and datetime.now() < code_expires_at:
        new_access_token = create_access_token()
        update_user = UserUpdate(
            access_token=new_access_token,
            access_token_expires_at=datetime.now() + timedelta(days=180)
        )
        user = await update_user(update.message.from_user.id, update_user)
        
        logger.info("Access token updated for user %s", user)

        context.user_data["authorized"] = True

        await send_authorized_message(update, context)

        return AUTHORIZED

async def send_authorized_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=messages["authorized_prompt"])

# Cancel command
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Operación cancelada.")

# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Error: %s", context.error)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sucedio un error. Por favor, intenta de nuevo.")

# Authorized commands
async def primero(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data["authorized"]:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Grupos del primer curso:")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No tienes permiso para acceder a este comando.")

async def segundo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data["authorized"]:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Grupos del segundo curso:")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No tienes permiso para acceder a este comando.")

async def tercero(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data["authorized"]:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Grupos del tercer curso:")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No tienes permiso para acceder a este comando.")

async def cuarto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data["authorized"]:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Grupos del cuarto curso:")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No tienes permiso para acceder a este comando.")


def main():

    # Check if the db is ready
    if os.getenv("DB_URL") is None:
        raise Exception("DB_URL is not set")

    application = ApplicationBuilder().token(token).build()

    conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                EMAIL_VALIDATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_user_email)],
                CODE_VERIFICATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, verify_code)],
                CODE_EXPIRED: [MessageHandler(filters.TEXT & ~filters.COMMAND, reverify_code)],
                AUTHORIZED: [
                    CommandHandler('primero', primero),
                    CommandHandler('segundo', segundo),
                    CommandHandler('tercero', tercero),
                    CommandHandler('cuarto', cuarto),
                    CommandHandler('cancel', cancel),
                ],
    
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('start', start))

    # Error handler
    application.add_error_handler(error)

    application.run_polling()

if __name__ == '__main__':
    main()