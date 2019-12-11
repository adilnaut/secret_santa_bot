from flask import Flask
from flask import render_template, request
import logging
import telegram
import os
import requests
import json
import random

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

        if 'new_chat_participant' in ans['message']:
            part = ans['message']['new_chat_participant']
            if part['is_bot'] == True and part['username'] == "easy_santa_astana_bot":
                # bot added to the group
                chat_id = str(ans['message']['chat']['id'])
                r_json = bot_request("getChatAdministrators?chat_id="+chat_id)
                users = r_json['result']
                model_users = {}

                arr = []
                for user in users:
                    model_user = {}
                    model_user["name"] = user['user']['first_name']
                    model_user["id"] = user['user']['id']
                    model_user["username"] = user['user']['username']
                    arr.append(model_user)
                model_users[chat_id] = {}
                model_users[chat_id]["user_data"] = arr
                bot_send_message(chat_id, "This is the secret santa bot! \n You can play Secret Santa now with /play command or set restriction with /pair @username1 @username2. \n Everyone should have admin right to be recognized by the bot")
                with open('data.txt', 'w') as outfile:
                    json.dump(model_users, outfile)
                return "ok"
            else:
                return "ok"
        else:
            if "chat" in ans['message']:
                is_bot = ans['message']['from']['is_bot']
                if is_bot == False:
                    chat_id = str(ans['message']['chat']['id'])
                    text = ans['message']['text']
                    if "/start" in text:
                        is_private = ans['message']['chat']['type'] == 'private'
                        if is_private:
                            with open('data.txt') as json_file:
                                data = json.load(json_file)
                                if chat_id in data and "santa_of" in data[chat_id]:
                                    for santa_of in data[chat_id]["santa_of"]:
                                        bot_send_message(chat_id, "You are the secret santa of {} ({}) in the group {}! Keep it secret!".format(santa_of["santa_of_name"], santa_of["santa_of_username"], santa_of["chat_title"]))
                                    return "ok"
                                return "ok"
                        return "ok"
                    if "/play" in text:
                        with open('data.txt') as json_file:
                            data = json.load(json_file)
                            if chat_id not in data:
                                return "ok"
                            players = []
                            temp_data = {}
                            i = 0
                            for user in data[chat_id]["user_data"]:
                                name = user["name"]
                                user_id = user["id"]
                                username = user["username"]
                                temp_data[username] = {}
                                temp_data[username]["name"] = name
                                temp_data[username]["user_id"] = user_id
                                temp_data[username]["index"] = i
                                players.append(username)
                                i += 1
                            again = True
                            players_copy = list(players)
                            while again:
                                print('again')
                                random.shuffle(players)
                                # break;
                                x = 0
                                for j in range(len(players)):
                                    if players[j] == players_copy[j]:
                                        x += 1

                                if x > 0:
                                    continue
                                else:
                                    if "pair" in data[chat_id]:
                                        again = False
                                        for pair in data[chat_id]["pair"]:
                                            i_user1  = temp_data[pair["user1"]]["index"]
                                            i_user2  = temp_data[pair["user2"]]["index"]
                                            if players[i_user2] == pair["user2"]:
                                                again = True
                                                break;
                                        continue
                                    else:
                                        break;
                            for i in range(len(players)):
                                usr_id = str(temp_data[players_copy[i]]["user_id"])
                                bot_send_message(usr_id, "You are secret santa of {} ({})! Keep it secret!".format(temp_data[players[i]]["name"] , players[i]))
                                data[usr_id] = {}
                                if "santa_of" not in data[usr_id]:
                                    data[usr_id]["santa_of"] = []
                                temp_dict = {}
                                temp_dict["username"] = players_copy[i]
                                temp_dict["santa_of_name"] =  temp_data[players[i]]["name"]
                                temp_dict["santa_of_username"] = players[i]
                                temp_dict["chat_title"] = ans['message']['chat']['title']
                                data[usr_id]["santa_of"].append(temp_dict)
                                with open('data.txt', 'w') as outfile:
                                    json.dump(data, outfile)
                                if players_copy[i] == "malika_nu":
                                    bot_send_message(str(temp_data[players_copy[i]]["user_id"]), "Meow meow meow")
                            bot_send_message(chat_id, "Everybody in this group now have a Secret Santa!")
                            return "ok"
                        return "ok"
                    if "/pair" in text:
                        with open('data.txt') as json_file:
                            data = json.load(json_file)
                            if chat_id in data:
                                if "pair" not in data[chat_id]:
                                    data[chat_id]["pair"] = []
                                tokens = text.split(" ")
                                print(tokens)
                                if len(tokens) != 3:
                                    bot_send_message(chat_id, "Incorrect format, try again ! \n You can play Secret Santa now with /play command or set restriction with /pair @username1 @username2.")
                                    return "ok"
                                user1  = tokens[1].replace("@", "")
                                user2 = tokens[2].replace("@", "")
                                data[chat_id]["pair"].append({"user1":user1, "user2":user2})
                                bot_send_message(chat_id, "Pair of {} and {} is recorded!".format(user1, user2))
                                with open('data.txt', 'w') as outfile:
                                    json.dump(data, outfile)
                        return "ok boomer"
                    if len(text) > 0:
                        is_private = ans['message']['chat']['type'] == 'private'
                        if is_private:
                            with open('data.txt') as json_file:
                                data = json.load(json_file)
                                if chat_id in data and "santa_of" in data[chat_id]:
                                    for santa_of in data[chat_id]["santa_of"]:
                                        bot_send_message(chat_id, "You are the secret santa of {} ({}) in the group {}! Keep it secret!".format(santa_of["santa_of_name"], santa_of["santa_of_username"], santa_of["chat_title"]))
                                    return "ok"
                                return "ok"
                        return "ok"
            return "ok"
        sender_id = str(ans['message']['from']['id'])
        sender_name = str(ans['message']['from']['first_name'])
        bot_send_message(sender_id, sender_name)
        # print("sendMessage?chat_id="+str(ans['message']['from']['id'])+",text="+str(ans['message']['from']['first_name']))
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
def bot_send_message(sender_id, text):
    bot_request("sendMessage?chat_id="+sender_id+"&text="+text)

def bot_request(req):
    r = requests.get("https://api.telegram.org/bot919844054:AAFYfWSrbUgFgKs1gZMCyHKJWDyOJjYDu7I/"+req,  headers={'Content-Type':'application/json'})
    print(r.json())
    return r.json()
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
