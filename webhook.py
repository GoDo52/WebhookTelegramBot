import datetime
import time
import traceback
import json

import pytz
from flask import request
from werkzeug.exceptions import HTTPException

from setup import *

from botlogic import smsapi_webhook_logic, crypto_webhook_logic
from smsapi import MdnMessage
from nowpayments import CryptoPayment


# ------------- server boot time -------------


boot_time = time.time()
boot_date = datetime.datetime.now(tz=pytz.timezone("Europe/Kyiv"))


# -------------- Exception handler --------------


@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e

    logger.error(traceback.format_exc())
    return "Oops", 500


# -------------- status webpage --------------


@app.route('/')
def status():
    password = request.args.get("password")
    if password != ADMIN_PASSWORD:
        logger.info('Status page loaded without password')
        return "<h1>Access denied!<h1>", 403

    return f'<h1>This is telegram bot server, ' \
           f'<p>Server uptime: {datetime.timedelta(seconds=time.time() - boot_time)}</p>' \
           f'<p>Server last boot at {boot_date}'


# ------------- webhook ----------------


@app.route('/' + WEBHOOK_TOKEN, methods=['POST'])
def get_message():
    # temp = request.stream.read().decode("utf-8")
    temp = request.get_data().decode("utf-8")
    temp = telebot.types.Update.de_json(temp)
    logger.debug('New message received. raw: %s', temp)
    bot.process_new_updates([temp])
    return "!", 200


# UNITED_SMS_WEBHOOK
@app.route('/' + WEBHOOK_TOKEN + '/unitedsms_api', methods=['POST', 'GET'])
def unitedsms_api_handler():
    print('UNITED_SMS API DATA HAS BEEN SENT HERE')

    # Extract form data from the incoming request
    form_data = request.form
    print(form_data)

    received_phone_info = MdnMessage(form_data=form_data)
    print(received_phone_info.mdn_id)
    print(received_phone_info.mdn_number)
    print(received_phone_info.mdn_price)
    print(received_phone_info.mdn_reply)

    smsapi_webhook_logic(number=received_phone_info)

    logger.debug('New message received. raw: %s\n\n', form_data)
    return "GOT UNITEDSMS_API POST REQUEST!", 200


@app.route('/' + WEBHOOK_TOKEN + '/crypto_payment', methods=['POST', 'GET'])
def nowpayments_api_handler():
    print('NOWPAYMENTS API DATA HAS BEEN SENT HERE')

    data_bytes = request.data
    data_str = data_bytes.decode('utf-8')
    payment_dict = json.loads(data_str)

    print(payment_dict)

    if payment_dict.get('payment_status') == 'finished':
        payment = CryptoPayment(payment=payment_dict)
        crypto_webhook_logic(payment=payment)

    return "GOT NOWPAYMENTS POST REQUEST!", 200


@app.route("/set_webhook")
def webhook_on():
    password = request.args.get("password")
    if password != ADMIN_PASSWORD:
        logger.info('Set_webhook page loaded without password')
        return "<h1>Access denied!<h1>", 403

    bot.remove_webhook()
    url = 'https://' + os.environ.get('HOST') + '/' + WEBHOOK_TOKEN
    bot.set_webhook(url=url)
    logger.info(f'Webhook is ON! Url: %s', url)
    return "<h1>WebHook is ON!</h1>", 200


@app.route("/remove_webhook")
def webhook_off():
    password = request.args.get("password")
    if password != ADMIN_PASSWORD:
        logger.info('Remove_webhook page loaded without password')
        return "<h1>Access denied!<h1>", 403

    bot.remove_webhook()
    logger.info('WebHook is OFF!')
    return "<h1>WebHook is OFF!</h1>", 200
