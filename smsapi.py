import requests
from typing import Dict, Union
from datetime import datetime, timedelta

from setup import united_sms_password, united_sms_user


# ======================================================================================================================


password = united_sms_password
user = united_sms_user

price_markup = 1.25


# Phone Classes========================================================================================================


class VirtualNumber:
    def __init__(self, mdn: tuple):

        self.mdn_id = mdn[5]
        self.mdn_number = mdn[0]
        self.service = mdn[1]
        self.mdn_state = mdn[2] or None
        self.price = round(price_markup * float(mdn[3]), 2)
        self.mdn_time_till_expiration = mdn[4]

    def display_info(self):
        print(f"ID: {self.mdn_id}")
        print(f"MDN: {self.mdn_number}")
        print(f"Service: {self.service}")
        print(f"Price: ${self.price}")

    def mdn_number_text(self):
        country_code = self.mdn_number[0]
        area_code = self.mdn_number[1:4]
        central_office_code = self.mdn_number[4:7]
        line_number = self.mdn_number[7:]

        # Format the number
        formatted_number = f"+{country_code} ({area_code}) {central_office_code}-{line_number}"

        return formatted_number


# Phone Classes========================================================================================================


class MdnMessage:
    def __init__(self, form_data: Dict[str, Union[str, int]]):
        self.mdn_id = form_data.get('id')
        self.mdn_number = form_data.get('to')
        self.mdn_service = form_data.get('service')
        self.mdn_price = round(price_markup * float(form_data.get('price')), 2)
        self.mdn_reply = form_data.get('reply')
        self.pin = form_data.get('pin')
        self.from_number = form_data.get('from')
        self.date_time = form_data.get('date_time')

    def mdn_reply_text(self):
        formatted_text = self.mdn_reply.replace('\\n', '\n')
        return formatted_text

    def mdn_number_text(self):
        country_code = self.mdn_number[0]
        area_code = self.mdn_number[1:4]
        central_office_code = self.mdn_number[4:7]
        line_number = self.mdn_number[7:]

        # Format the number
        formatted_number = f"+{country_code} ({area_code}) {central_office_code}-{line_number}"

        return formatted_number


# SHORT TERM============================================================================================================


def check_balance():
    command = "balance"
    url = f"https://www.unitedsms.net/api_command.php?cmd={command}&user={user}&pass={password}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        if data['status'] == "ok":
            return data['message']
        else:
            return None
    else:
        print("Request failed with status code:", response.status_code)
        return None


def check_service(service: str):
    command = "list_services"
    url = f"https://www.unitedsms.net/api_command.php?cmd={command}&user={user}&pass={password}&service={service}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        if data['status'] == "ok":
            service_name = data['message'][0]['name']
            service_price = round(price_markup * float(data['message'][0]['price']), 2)
            service_available = float(data['message'][0]['available'])
            return service_name, service_price, service_available
        else:
            return None
    else:
        print("Request failed with status code:", response.status_code)
        return None


def rent_mdn(service: str, state: str = None):
    command = "request"
    url = f"https://www.unitedsms.net/api_command.php?cmd={command}&user={user}&pass={password}&service={service}"
    response = requests.get(url)
    data = response.json()
    print(data)
    if response.status_code == 200:
        if data['status'] == "ok":
            return (data['message'][0]['mdn'], data['message'][0]['service'], data['message'][0]['state'],
                    data['message'][0]['price'], data['message'][0]['till_expiration'] / 60,
                    data['message'][0]['id'])
        else:
            return None
    else:
        print("Request failed with status code:", response.status_code)
        return data['message']


def check_mdn(mdn_id: str):
    command = "request_status"
    url = f"https://www.unitedsms.net/api_command.php?cmd={command}&user={user}&pass={password}&id={mdn_id}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        if data['status'] == "ok":
            minutes = data['message']['till_expiration'] // 60
            seconds = data['message']['till_expiration'] % 60
            return (minutes, seconds)
        else:
            return None
    else:
        print("Request failed with status code:", response.status_code)
        return None


def read_mdn(mdn_id: str):
    command = "read_sms"
    url = f"https://www.unitedsms.net/api_command.php?cmd={command}&user={user}&pass={password}&id={mdn_id}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        if data['status'] == "ok":
            return data['message'][0]['reply']
        else:
            return None
    else:
        print("Request failed with status code:", response.status_code)
        return None


# LONG TERM=============================================================================================================


def rent_long_mdn(service: str):
    command = "ltr_rent"
    url = f"https://www.unitedsms.net/api_command.php?cmd={command}&user={user}&pass={password}&service={service}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        if data['status'] == "ok":
            return (data['message']['mdn'], data['message']['service'],
                    data['message']['price'], data['message']['expires'],
                    data['message']['id'])
        else:
            return None
    else:
        print("Request failed with status code:", response.status_code)
        return None


def release_long_mdn(ltr_id: int):
    command = "ltr_release"
    url = f"https://www.unitedsms.net/api_command.php?cmd={command}&user={user}&pass={password}&id={ltr_id}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        if data['status'] == "ok":
            return True
        elif data['status'] == "error":
            return data['message']
        else:
            return None
    else:
        print("Request failed with status code:", response.status_code)
        return None


def report_long_mdn(ltr_number: int):
    command = "ltr_report"
    url = f"https://www.unitedsms.net/api_command.php?cmd={command}&user={user}&pass={password}&mdn={ltr_number}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        if data['status'] == "ok":
            return True
        elif data['status'] == "error":
            return data['message']
        else:
            return None
    else:
        print("Request failed with status code:", response.status_code)
        return None


def change_from_unknown_service_long_mdn(service: str, ltr_id: int):
    command = "ltr_switch_service"
    url = f"https://www.unitedsms.net/api_command.php?cmd={command}&user={user}&pass={password}&service={service}&id={ltr_id}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        if data['status'] == "ok":
            return True
        elif data['status'] == "error":
            return data['message']
        else:
            return None
    else:
        print("Request failed with status code:", response.status_code)
        return None


def change_auto_renew_service_long_mdn(ltr_id: int, autorenew='true'):
    command = "ltr_autorenew"
    url = f"https://www.unitedsms.net/api_command.php?cmd={command}&user={user}&pass={password}&id={ltr_id}&autorenew={autorenew}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        if data['status'] == "ok":
            return True
        elif data['status'] == "error":
            return data['message']
        else:
            return None
    else:
        print("Request failed with status code:", response.status_code)
        return None


def activate_long_mdn(ltr_number: int):
    command = "ltr_activate"
    url = f"https://www.unitedsms.net/api_command.php?cmd={command}&user={user}&pass={password}&mdn={ltr_number}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        if data['status'] == "ok":
            return True
        elif data['status'] == "error":
            return data['message']
        else:
            return None
    else:
        print("Request failed with status code:", response.status_code)
        return None


def check_online_status_long_mdn():
    pass


# ======================================================================================================================


if __name__ == "__main__":
    print(check_service(service='telegram'))
    # response = {'status': 'ok', 'message': [{'id': 14031792, 'mdn': '12029133303', 'service': 'Telegram',
    #             'status': 'Reserved', 'state': '', 'markup': 0, 'price': '0.32', 'till_expiration': 900}]}
    #
    # print(f"Your number for {service} is: {mdn}, "
    #       f"for price {price}$ is ready you have {minutes} minutes till expiration!")
    # print(rent_long_mdn(service='Telegram'))
    # print(release_long_mdn(ltr_id=109428))

    # command = "balance"
    # # url = f"https://www.unitedsms.net/api_command.php?cmd={command}&user={user}&pass={password}"
    # url = f"https://telegram-webhook-bot-1bc4a41520b0.herokuapp.com/7353C5F783F56B01FEF3E6BB8217A6775B8A471E28D9108/unitedsms_api"
    # response = requests.post(url=url, json={'apple': 'red'})
    # data = response.text
    # print(data)
    # print(rent_mdn(service='Unknown'))
    pass
