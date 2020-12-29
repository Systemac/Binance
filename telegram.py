import requests

from config.config import config


def senders(message):
    bot_token = config.get("TOK_TELEGRAM")
    bot_chatid = config.get("CHAT_ID")
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatid + '&parse_mode=Markdown&text=' + message
    response = requests.get(send_text)
    return response.json()
