import urllib.request
import json
import time
import requests

prometheus_url = 'http://10.100.2.11:9090'
bot_token = ""
bot_chatID = ""


def tg_bot(bot_message):
    send_text = "https://api.telegram.org/bot" + bot_token + "/sendMessage?chat_id=" + bot_chatID + "&parse_mode=HTML&text=" + bot_message
    response = requests.get(send_text)
    return response.json()


def get_data(api):
    with urllib.request.urlopen(prometheus_url + '/api/v1/' + api) as url:
        data = json.load(url)
    return data


def get_alert_status():
    data = get_data('rules')
    alert_state = 0
    for item in data['data']['groups']:
        for state in item['rules']:
            if state['state'] == 'firing':
                alert_state += 1
    return alert_state


def get_alerts_message():
    data = get_data('alerts')
    msg = ''
    if data['data']['alerts']:
        for items in data['data']['alerts']:
            msg += '\nMessage: ' + items['labels']['alertname'] + '\n\n<i>' + \
                'Host: ' + items['labels']['instance'] + '\n' + \
                'Job: ' + items['labels']['job'] + '\n' + \
                'Status: ' + items['labels']['severity'] + '\n</i>'
    return msg


switch_state = None

while True:
    try:
        if get_alert_status() >= 1 and switch_state != 1:
            tg_bot('<b>Alerts!</b>\n' + get_alerts_message())
            switch_state = 1
        if get_alert_status() == 0 and switch_state != 0:
            tg_bot('<b>No alerts now!</b>')
            switch_state = 0
        time.sleep(5)

    except:
        print('Can`t connect to prometheus... Next try attempt for 30s')
        time.sleep(30)
