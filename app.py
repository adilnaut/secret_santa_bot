from flask import Flask
from flask import render_template, request
import logging
import telegram
import os
import requests
import json
import random

HOST = "https://secret-santa-astana.herokuapp.com/"
Telegram_token = "919844054:AAFYfWSrbUgFgKs1gZMCyHKJWDyOJjYDu7I"
jsonbin = "https://jsonbin.io/5fe24d0c47ed0861b36aa379"
jsonbin_secret = "$2b$10$R248o3.U5BEnIlPpNDFs.uERh/ui3h4oD/xLYz6Cbi2DTr.RrM52y"

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# update json database
def edit_json(value):
    url = jsonbin
    headers = {'Content-Type': 'application/json', 'secret-key': jsonbin_secret,}
    data = {"data": value}

    req = requests.put(url, json=data, headers=headers)
    print(req.text)
# get latest json database state
def get_json():
    url = jsonbin
    headers = {'secret-key': jsonbin_secret, 'Content-Type': 'application/json'}

    req = requests.get(url, json={"another":"nothing"}, headers=headers)
    print(req.text)
    return json.loads(req.text)['data']
@app.route("/", methods=["POST", "GET"])
def setWebhook():
    if request.method == "GET":
        logging.info("Hello, Telegram!")
        print ("Done")

        r = requests.get("https://api.telegram.org/bot"+Telegram_token+"/setWebhook?url="+HOST)

        print(r.json())
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
                if "result" not in r_json:
                    return "ok boomer"
                users = r_json['result']
                model_users = {}

                arr = []
                # collect data of every chat participant into our database
                for user in users:
                    model_user = {}
                    model_user["name"] = user['user']['first_name']
                    model_user["id"] = user['user']['id']
                    if "username" in user['user']:
                        model_user["username"] = user['user']['username']
                    else:
                        model_user["username"] = user['user']['first_name']
                    arr.append(model_user)
                model_users[chat_id] = {}
                model_users[chat_id]["user_data"] = arr
                bot_send_message(chat_id, "This is the secret santa bot! \n You can play Secret Santa now with /play command or set restriction with /pair @username1 @username2. \n Everyone should have admin right to be recognized by the bot")
                edit_json(model_users)
                return "ok"
            else:
                return "ok"
        else:
            if "chat" in ans['message']:
                is_bot = ans['message']['from']['is_bot']
                if is_bot == False:
                    chat_id = str(ans['message']['chat']['id'])
                    if "text" not in ans['message']:
                        return "ok boomer"
                    text = ans['message']['text']
                    if "/start" in text:
                        is_private = ans['message']['chat']['type'] == 'private'
                        if is_private:
                            data = get_json()
                            if chat_id in data and "santa_of" in data[chat_id]:
                                # There could be more than one group that user is in
                                for santa_of in data[chat_id]["santa_of"]:
                                    bot_send_message(chat_id, "You are the secret santa of {} ({}) in the group {}! Keep it secret!".format(santa_of["santa_of_name"], santa_of["santa_of_username"], santa_of["chat_title"]))
                                return "ok"
                            return "ok"
                        else:
                            bot_send_message(chat_id, "Bot already started!")
                        return "ok"
                    if "/play" in text:
                        # assign secret santa to every user
                        data = get_json()
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
                        c = 0
                        while again:
                            random.shuffle(players)
                            if c > 100:
                                bot_send_message(chat_id, "Restrictions are imposible to meet, try to delete bot and invite again!")
                                break;
                            c += 1
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
                                        if players[i_user1] == pair["user2"]:
                                            again = True
                                            break;
                                        if players[i_user2] == pair["user1"]:
                                            again = True
                                            break;
                                    continue;
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
                            s = json.dumps(data)
                            edit_json(data)
                        bot_send_message(chat_id, "Everybody in this group now have a Secret Santa!")
                        return "ok"
                    if "/pair" in text:
                        with open('data.txt') as json_file:
                            data = get_json()
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
                                s = json.dumps(data)
                                edit_json(data)
                        return "ok boomer"
                    if len(text) > 0:
                        is_private = ans['message']['chat']['type'] == 'private'
                        if is_private:
                            with open('data.txt') as json_file:
                                data = get_json()
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
        return "ok"

@app.route("/verify", methods=["POST"])
def verification():
    if request.method == "POST":
        print(request.get_json())
        return "ok"
def bot_send_message(sender_id, text):
    bot_request("sendMessage?chat_id="+sender_id+"&text="+text)

def bot_request(req):
    r = requests.get("https://api.telegram.org/bot"+Telegram_token+"/"+req,  headers={'Content-Type':'application/json'})
    print(r.json())
    return r.json()



if __name__ == "__main__":

    app.run(host= "0.0.0.0", debug=True)
