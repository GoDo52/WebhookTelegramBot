import os

from setup import bot, logger
from webhook import app

from database import User, init_db

from botlogic import *


# --------------- bot -------------------


@bot.message_handler(commands=['help', 'start'])
def start_menu(message):
    logger.info(f'</code>@{message.from_user.username}<code> ({message.chat.id}) used /start or /help')
    start_menu_logic(message=message)


@bot.callback_query_handler(func=lambda call: True)
def callback_logic(call):
    user = User(user_id=call.message.chat.id)
    if call.data == "VoIP":
        voip_menu_logic(message=call.message)
    elif call.data == "VoIP_order":
        voip_order_logic(message=call.message)
    elif call.data == "VoIP_active":
        active_numbers_logic(message=call.message)
    elif call.data == "VoIP_history":
        voip_history_logic(message=call.message)
    elif call.data == "Profile":
        profile_menu_logic(message=call.message)
    elif call.data == "support":
        support_menu_logic(message=call.message)
    elif call.data == "Start_menu":
        start_menu_logic_back(message=call.message)
    elif call.data == "Balance_menu":
        balance_menu_logic(message=call.message)
    elif call.data == "crypto_payment":
        crypto_payment(message=call.message)
    elif call.data == "crypto_payment_history":
        payment_history_logic(message=call.message)
    elif call.data == "ADD_BALANCE":
        user.update_balance(amount=10)
    elif call.data == "sent_database":
        with open('DataBase.db', 'rb') as file:
            bot.send_document(chat_id=user.user_id, document=file)
    elif call.data == "init_db":
        init_db()


# --------------- main name -------------------


if __name__ == '__main__':
    if os.environ.get("IS_PRODUCTION", "False") == "True":
        app.run()
    else:
        bot.infinity_polling()
