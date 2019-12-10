from flask import Flask
from flask import render_template, request
import logging
import telegram
import os
import requests

HOST = "https://secret-santa-astana.herokuapp.com/"

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

global bot
bot = telegram.Bot(token='919844054:AAFYfWSrbUgFgKs1gZMCyHKJWDyOJjYDu7I')
botName = "easy_santa_astana_bot" #Without @


@app.route("/", methods=["POST", "GET"])
def setWebhook():
    if request.method == "GET":
        logging.info("Hello, Telegram!")
        print ("Done")

        r = requests.get("https://api.telegram.org/bot919844054:AAFYfWSrbUgFgKs1gZMCyHKJWDyOJjYDu7I/setWebhook?url=https://secret-santa-astana.herokuapp.com/")

        print(r.json())# https://api.telegram.org/bot{my_bot_token}/setWebhook?url={url_to_send_updates_to}
        return "OK, Telegram Bot!"
    if request.method == "POST":
        print(request.get_json())
        ans = request.get_json()
        bot_request("sendMessage?chat_id="+str(ans['message']['from']['id'])+",text="+str(ans['message']['from']['first_name']))
        return "ok"

@app.route("/verify", methods=["POST"])
def verification():
    if request.method == "POST":
        print(request.get_json())
        # update = telegram.Update.de_json(request.get_json(force=True),bot)
        # if update is None:
        #     return "Show me your TOKEN please!"
        # logging.info("Calling {}".format(update.message))
        # handle_message(update.message)
        return "ok"

def bot_request(req):
    r = requests.get("https://api.telegram.org/bot919844054:AAFYfWSrbUgFgKs1gZMCyHKJWDyOJjYDu7I/"+req)
    print(r.json())
# def handle_message(msg):
#     text = msg.text
#     print(msg)
#     # An echo bot
#     bot.sendMessage(chat_id=msg.chat.id, text=text)


if __name__ == "__main__":
    # s = bot.setWebhook("{}/verify".format(HOST))
    # if s:
    #     logging.info("{} WebHook Setup OK!".format(botName))
    # else:
    #     logging.info("{} WebHook Setup Failed!".format(botName))
    app.run(host= "0.0.0.0", debug=True)
