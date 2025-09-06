import requests

INSTANCE_ID = "instance134909"  # Replace with your actual instance ID
TOKEN = "71gxkcbh3xhtfod6"  # Replace with your actual API token

url = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"



def notify_whatsapp(message, phone_number):
    payload = f"token={TOKEN}&to=%2B222{phone_number}&body={message}"
    payload = payload.encode('utf8').decode('iso-8859-1')
    headers = {'content-type': 'application/x-www-form-urlencoded'}

    response = requests.request("POST", url, data=payload, headers=headers)

    return response

