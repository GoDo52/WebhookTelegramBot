from setup import bot, logger

import telebot.types

from database import User, get_user_id_for_sms, get_user_id_for_crypto

from nowpayments import CryptoPayment, create_invoice

from smsapi import *


# Menus ================================================================================================================


def start_menu_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("Virtual Phone Numbers 📞", callback_data='VoIP'))
    markup.add(telebot.types.InlineKeyboardButton("Profile 👤", callback_data='Profile'),
               telebot.types.InlineKeyboardButton("Balance Top Up💰", callback_data='Balance_menu'))
    markup.add(telebot.types.InlineKeyboardButton("Support 🆘", callback_data='support'))
    # Administrative...
    # markup.add(telebot.types.InlineKeyboardButton("DB", callback_data='sent_database'))
    # markup.add(telebot.types.InlineKeyboardButton("init_db", callback_data='init_db'))

    return markup


def voip_menu_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("Order Virtual Number 📞", callback_data='VoIP_order'))
    markup.add(telebot.types.InlineKeyboardButton("View active numbers ⌛️", callback_data='VoIP_active'))
    markup.add(telebot.types.InlineKeyboardButton("History of orders 📒", callback_data='VoIP_history'))
    markup.add(telebot.types.InlineKeyboardButton("Back ⬅️", callback_data='Start_menu'))

    return markup


def profile_menu_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("Back ⬅️", callback_data='Start_menu'))

    return markup


def balance_menu_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("Crypto Top Up 💰", callback_data='crypto_payment'))
    markup.add(telebot.types.InlineKeyboardButton("Support Top Up 💰", callback_data='support'))
    markup.add(telebot.types.InlineKeyboardButton("Payments history 📒", callback_data='crypto_payment_history'))
    markup.add(telebot.types.InlineKeyboardButton("ADD_BALANCE", callback_data='ADD_BALANCE'))
    markup.add(telebot.types.InlineKeyboardButton("Back ⬅️", callback_data='Start_menu'))

    return markup


def back_to_start_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("Back ⬅️", callback_data='Start_menu'))

    return markup


def back_to_voip_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("Back ⬅️", callback_data='VoIP'))

    return markup


def back_to_balance_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("Back ⬅️", callback_data='Balance_menu'))

    return markup


# Logic ================================================================================================================


def start_menu_logic(message):
    logger.info(f'</code>@{message.from_user.username}<code> ({message.chat.id}) used echo:\n\n%s', message.text)

    user = User(user_id=message.chat.id, username=message.from_user.username)
    user.add_to_database()

    markup = start_menu_markup()

    bot.send_message(
        chat_id=message.chat.id,
        text="<b>In this bot you can rent virtual one-time use numbers!</b>",
        reply_markup=markup,
        parse_mode='html'
    )


def start_menu_logic_back(message, send: bool = False):
    logger.info(f'</code>@{message.from_user.username}<code> ({message.chat.id}) used echo:\n\n%s', message.text)

    markup = start_menu_markup()

    if send:
        bot.send_message(
            chat_id=message.chat.id,
            text="<b>In this bot you can rent virtual one-time use numbers!</b>",
            reply_markup=markup,
            parse_mode='html'
        )
        return

    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text="<b>In this bot you can rent virtual one-time use numbers!</b>",
        reply_markup=markup,
        parse_mode='html'
    )


def support_menu_logic(message, send: bool = False):
    logger.info(f'</code>@{message.from_user.username}<code> ({message.chat.id}) used echo:\n\n%s', message.text)

    markup = back_to_start_markup()

    if send:
        bot.send_message(
            chat_id=message.chat.id,
            text="Contact our support here: <b>@US_RENT_SHOP_SUPPORT</b>\nYou can also use our support for balance "
                 "top up",
            reply_markup=markup,
            parse_mode='html'
        )
        return

    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text="Contact our support here: <b>@US_RENT_SHOP_SUPPORT</b>\nYou can also use our support for balance "
             "top up",
        reply_markup=markup,
        parse_mode='html'
    )


def profile_menu_logic(message):
    logger.info(f'</code>@{message.from_user.username}<code> ({message.chat.id}) used echo:\n\n%s', message.text)

    user = User(user_id=message.chat.id)

    markup = profile_menu_markup()

    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=f"👤 Your profile information:\nAccount ID: {user.user_id}\nBalance: {user.balance}\n💲Date of "
             f"registration: {user.date_of_registration}",
        reply_markup=markup,
        parse_mode='html'
    )


def balance_menu_logic(message, send: bool = False):
    logger.info(f'</code>@{message.from_user.username}<code> ({message.chat.id}) used echo:\n\n%s', message.text)

    user = User(user_id=message.chat.id)

    markup = balance_menu_markup()

    if send:
        bot.send_message(
            chat_id=message.chat.id,
            text=f"Your balance: {user.balance}💲\nTotal deposit: {user.deposit}💲",
            reply_markup=markup,
            parse_mode='html'
        )
        return

    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=f"Your balance: {user.balance}💲\nTotal deposit: {user.deposit}💲",
        reply_markup=markup,
        parse_mode='html'
    )


def voip_menu_logic(message, send: bool = False):
    logger.info(f'</code>@{message.from_user.username}<code> ({message.chat.id}) used echo:\n\n%s', message.text)

    markup = voip_menu_markup()

    if send:
        bot.send_message(
            chat_id=message.chat.id,
            text=f"Here you can order numbers or see history of successfully used numbers",
            reply_markup=markup,
            parse_mode='html'
        )
        return

    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=f"Here you can order numbers or see history of successfully used numbers",
        reply_markup=markup,
        parse_mode='html'
    )


def voip_order_logic(message):
    logger.info(f'</code>@{message.from_user.username}<code> ({message.chat.id}) used echo:\n\n%s', message.text)

    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text="Write a Service name you would like to order number on\n"
             "Or <i>cancel</i> if you want to get back",
        parse_mode='html'
    )

    bot.register_next_step_handler(message, give_number_logic)


def give_number_logic(message):
    logger.info(f'</code>@{message.from_user.username}<code> ({message.chat.id}) used echo:\n\n%s', message.text)
    user = User(user_id=message.chat.id)
    service_name = message.text.lower()

    if service_name == 'cancel':
        voip_menu_logic(message=message, send=True)
        return None

    service = check_service(service=service_name)
    if not service:
        bot.send_message(
            chat_id=message.chat.id,
            text=f"No service found for {service_name}, check the name entered and try again!",
            parse_mode='html'
        )
        voip_menu_logic(message=message, send=True)
        return None

    if user.balance >= service[1]:
        if service[2] < 1:
            bot.send_message(
                chat_id=message.chat.id,
                text=f"There is no available numbers for {service[0]} right now, try again later!",
                parse_mode='html'
            )
            return None

        mdn_request = rent_mdn(service=service_name)
        if mdn_request is not None:
            number = VirtualNumber(mdn=mdn_request)

            user.insert_voip_number(number=number)

            bot.send_message(
                chat_id=message.chat.id,
                text=f"Your number is: `{number.mdn_number_text()}`, price is: {number.price}\n"
                     f"You have {number.mdn_time_till_expiration} minutes left for this mdn!\n"
                     f"Bot will send you a message when the sms arrives, be patient :)",
                parse_mode='Markdown'
            )
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text=f"No service found for {service_name}, check the name entered and try again!",
                parse_mode='html'
            )
            voip_menu_logic(message=message, send=True)
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text=f"Your balance is not sufficient! Top up your account before ordering.",
            parse_mode='html'
        )
        balance_menu_logic(message=message, send=True)


def voip_history_logic(message):
    logger.info(f'</code>@{message.from_user.username}<code> ({message.chat.id}) used echo:\n\n%s', message.text)

    user = User(user_id=message.chat.id)
    history = user.get_used_numbers_history()
    markup = back_to_voip_markup()

    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=f"Your history for the last 20 successfully used numbers:\n{history}",
        reply_markup=markup,
        parse_mode='html'
    )


def active_numbers_logic(message):
    logger.info(f'</code>@{message.from_user.username}<code> ({message.chat.id}) used echo:\n\n%s', message.text)

    user = User(user_id=message.chat.id)
    history = user.get_active_numbers()
    markup = back_to_voip_markup()

    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=f"Your active numbers:\n{history}",
        reply_markup=markup,
        parse_mode='html'
    )


def crypto_payment(message, send: bool = False):
    logger.info(f'</code>@{message.from_user.username}<code> ({message.chat.id}) used echo:\n\n%s', message.text)

    if send:
        bot.send_message(
            chat_id=message.chat.id,
            text="Write an amount <i>USD</i> (more than <b>5</b>).\n"
                 "You will get a link to external site to finish up payment.\n"
                 "Or enter <i>cancel</i> if you want to get back",
            parse_mode='html'
        )
    else:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Write an amount <i>USD</i> (more than <b>5</b>).\n"
                 "You will get a link to external site to finish up payment.\n"
                 "Or enter <i>cancel</i> if you want to get back",
            parse_mode='html'
        )
    bot.register_next_step_handler(message, give_crypto_payment_logic)


def give_crypto_payment_logic(message):
    logger.info(f'</code>@{message.from_user.username}<code> ({message.chat.id}) used echo:\n\n%s', message.text)
    user = User(user_id=message.chat.id)
    amount = message.text.lower()

    if amount == 'cancel':
        balance_menu_logic(message=message, send=True)
        return None

    if amount.isdigit():
        amount = float(amount)
        if amount >= 5:
            created_payment = create_invoice(amount=amount)
            if not created_payment:
                bot.send_message(
                    chat_id=message.chat.id,
                    text="Error happened in the request contact support!",
                    parse_mode="html"
                )
                crypto_payment(message=message, send=True)
                return
            payment = CryptoPayment(payment=created_payment)
            user.insert_crypto_payment(payment=payment)
            bot.send_message(
                chat_id=message.chat.id,
                text=f"Invoice has been created! You can visit this link to make transaction: {payment.payment_url}\n"
                     f"Payment amount in USD is: {payment.payment_amount}$\n"
                     f"Payment was created at: {payment.created_at}\n"
                     f"Payment status: <i>{payment.payment_status}</i>\n"
                     f"<i>Bot will send you a message when funds are finished transferring!</i>",
                parse_mode="html"
            )
            start_menu_logic_back(message=message, send=True)
            return
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text="Entered amount is lower than 5 USD.",
                parse_mode="html"
            )
            crypto_payment(message=message, send=True)
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text="Please enter a valid number.",
            parse_mode="html"
        )
        crypto_payment(message=message, send=True)


def payment_history_logic(message):
    logger.info(f'</code>@{message.from_user.username}<code> ({message.chat.id}) used echo:\n\n%s', message.text)

    user = User(user_id=message.chat.id)
    history = user.get_finished_payments()
    markup = back_to_balance_markup()

    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=f"Your history of the last 20 successful top ups:\n{history}",
        reply_markup=markup,
        parse_mode='html'
    )


# Webhook ==============================================================================================================


def smsapi_webhook_logic(number: MdnMessage):
    user_id = get_user_id_for_sms(number_id=number.mdn_id, number=number.mdn_number_text())
    user = User(user_id=user_id)
    user.update_used_voip_number(number=number)
    user.update_balance(amount=-number.mdn_price)
    markup = back_to_voip_markup()
    bot.send_message(
        chat_id=user_id,
        text=f"Received message for number {number.mdn_number_text()}:\n"
             f"\"{number.mdn_reply_text()}\"\nPin from the message (click to copy): `{number.pin}`\n"
             f"Price of {number.mdn_price} was deducted from your balance",
        reply_markup=markup,
        parse_mode="Markdown"
    )


def crypto_webhook_logic(payment: CryptoPayment):
    user_id = get_user_id_for_crypto(payment_id=payment.payment_id)
    user = User(user_id=user_id)
    user.update_balance(amount=payment.payment_amount)
    user.update_crypto_payment(payment=payment)
    markup = back_to_balance_markup()
    bot.send_message(
        chat_id=user_id,
        text=f"Payment with ID {payment.payment_id} finished.\n"
             f"You balance has successfully been topped up for <b>{payment.payment_amount}$</b>",
        reply_markup=markup,
        parse_mode="html"
    )
