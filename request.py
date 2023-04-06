import requests
import json

proxy = {'https': 'socks5h://user:password@IP:1080'}

token = '8888:ABC'
chat_id = 88888

URL = 'https://api.telegram.org/bot' + token + '/sendMessage'
reply_markup ={ "keyboard": [["Yes", "No"], ["Maybe"], ["1", "2", "3"]], "resize_keyboard": True}
data = {'chat_id': chat_id, 'text': '123', 'reply_markup': json.dumps(reply_markup)}
r = requests.post(URL, data=data, proxies=proxy)

print(r.json())