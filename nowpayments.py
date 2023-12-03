import requests
import json

from setup import nowpayments_api_key, WEBHOOK_TOKEN


# ======================================================================================================================


api_key = nowpayments_api_key


# Payment Class ========================================================================================================


class CryptoPayment:
    def __init__(self, payment: dict):
        self.payment_id = payment.get('id') or payment.get('payment_id')
        self.payment_amount = float(payment.get('price_amount', 0))
        self.payment_url = payment.get('invoice_url') or f"https://nowpayments.io/payment/?iid={self.payment_id}"
        self.created_at = payment.get('created_at')
        self.payment_status = payment.get('payment_status', 'waiting')


# ======================================================================================================================


def get_api_status():
    url = f"https://api.nowpayments.io/v1/status"

    payload = {}
    headers = {}

    response = requests.get(url=url, headers=headers, data=payload)

    print(response.text)


def create_invoice(amount: float):
    url = "https://api.nowpayments.io/v1/invoice"

    payload = json.dumps({
        "price_amount": amount,
        "price_currency": "usd",
        "order_description": "IT services",
        "ipn_callback_url": f"https://telegram-webhook-bot-1bc4a41520b0.herokuapp.com"
                            f"/{WEBHOOK_TOKEN}/crypto_payment",
        "is_fixed_rate": True,
        "is_fee_paid_by_user": True
    })
    headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    data = response.json()
    print(data)

    if response.status_code == 200:
        return data
    else:
        print("Request failed with status code:", response.status_code)
        return None


# ======================================================================================================================


if __name__ == "__main__":
    # create_invoice()
    # {"id":"4564587856","token_id":"5739032767","order_id":null,"order_description":"Pay for services",
    # "price_amount":"5","price_currency":"USD","pay_currency":null,
    # "ipn_callback_url":"https://telegram-webhook-bot-1bc4a41520b0.herokuapp.com
    # /7353C5F783F56B01FEF3E6BB8217A6775B8A471E28D9108/crypto_payment",
    # "invoice_url":"https://nowpayments.io/payment/?iid=4564587856","success_url":null,"cancel_url":null,
    # "partially_paid_url":null,"payout_currency":null,"created_at":"2023-10-30T20:37:48.105Z",
    # "updated_at":"2023-10-30T20:37:48.105Z","is_fixed_rate":true,"is_fee_paid_by_user":true}
    #
    # 2023-10-30T20:28:36.132545+00:00 app[web.1]: Request: <Request
    # 'https://telegram-webhook-bot-1bc4a41520b0.herokuapp.com/7353C5F783F56B01FEF3E6BB8217A6775B8A471E28D9108
    # /crypto_payment' [POST]> 2023-10-30T20:28:36.132646+00:00 app[web.1]: Request data: b'{"payment_id":5261148849,
    # "parent_payment_id":null,"invoice_id":6417549628,"payment_status":"waiting",
    # "pay_address":"TDbqd96NNmXmNQCCbdohbvDnDZHcZy1GGJ","payin_extra_id":null,"price_amount":5,"price_currency":"usd",
    # "pay_amount":69.242455,"actually_paid":0,"actually_paid_at_fiat":0,"pay_currency":"trx","order_id":"1",
    # "order_description":"Pay for services","purchase_id":"5931000544","updated_at":1698697714802,
    # "outcome_amount":4.958355,"outcome_currency":"usdttrc20","payment_extra_ids":null}'

    # Request data: b'{"payment_id":5261148849,"parent_payment_id":null,"invoice_id":6417549628,
    # "payment_status":"finished","pay_address":"TDbqd96NNmXmNQCCbdohbvDnDZHcZy1GGJ","payin_extra_id":null,
    # "price_amount":5,"price_currency":"usd","pay_amount":69.242455,"actually_paid":69.25,"actually_paid_at_fiat":0,
    # "pay_currency":"trx","order_id":"1","order_description":"Pay for services","purchase_id":"5931000544",
    # "updated_at":1698697946468,"outcome_amount":4.959058,"outcome_currency":"usdttrc20","payment_extra_ids":null}'
    ...
