import requests
import os
import json
import time
from bs4 import BeautifulSoup

token = '712182367:AAH9MO0MkOO1ohikgWGIlJFTMDbO1VlSXmY'

httpsProxy = {'https' : '134.209.80.237:80'}


def sendMessage(a, text):
    URL = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={a}&text={text}'
    requests.get(URL, proxies=httpsProxy)


def addAccount(a, cmd):
    if len(cmd) != 29:
        sendMessage(a, 'Length of the command does not match a required length. Maybe you wrote wrong steamID? Try again or use /help')
        return 0

    steamid64 = cmd.split(' ')[1]

    url = f"https://steamcommunity.com/profiles/{steamid64}/inventory/"
    getRequest = requests.get(url).text
    if BeautifulSoup(getRequest, "html.parser").select("#inventory_link_730"):
        inventoryPage = BeautifulSoup(getRequest, "html.parser").select("#inventory_link_730")[0].find("span",
                                                                                              class_="games_list_tab_number")
        inventoryPageStr = str(inventoryPage)

        items_counter_str = inventoryPageStr.split('(')[1].split(')')[0]
        items_counter = int(items_counter_str)

        nick = BeautifulSoup(getRequest, "html.parser").select(".whiteLink")[0].text

        f = open(f'{a}.txt', 'a')
        f.write(f"{steamid64}|{items_counter}|{nick}|\n")
        f.close()

        sendMessage(a, 'Account added successfully.')
    else:
        nick = BeautifulSoup(getRequest, "html.parser").select(".whiteLink")[0].text

        f = open(f'{a}.txt', 'a')
        f.write(f"{steamid64}|{'0'}|{nick}|\n")
        f.close()

        sendMessage(a,                  'Account added successfully.\n'
                                        'NOTE: Seems like your account is private or has 0 CSGO items.\n'
                                        'Please make inventory public to see updates for this account in the future.\n')


def check(a):
    sendMessage(a, 'Starting a check...')

    f = open(f'{a}.txt', 'r+')

    while True:
        fileline = f.readline()
        if fileline != '':
            line = fileline.split('|')
            steamid64 = line[0]
            dbItems = int(line[1])
            nickname = line[2]

            url = f"https://steamcommunity.com/profiles/{steamid64}/inventory/"
            getRequest = requests.get(url).text
            if BeautifulSoup(getRequest, "html.parser").select("#inventory_link_730"):
                inventoryPage = BeautifulSoup(getRequest, "html.parser").select("#inventory_link_730")[0].find("span",
                                                                                                               class_="games_list_tab_number")
                inventoryPageStr = str(inventoryPage)

                items_counter_str = inventoryPageStr.split('(')[1].split(')')[0]
                items_counter = int(items_counter_str)

                sendMessage(a, f'Checking {nickname}...')

                temp = open(f'{a}_temp.txt', 'w')

                if items_counter != dbItems:
                    sendMessage(a, f'{nickname} got {items_counter - dbItems} items from the last check\n')

                    temp.write(f'{steamid64}|{items_counter}|{nickname}|\n')
                    temp.close()
                else:
                    temp.write(fileline)
                    temp.close()
                items_counter = 0
            else:
                temp = open(f'{a}_temp.txt', 'w')
                temp.write(f"{steamid64}|{'0'}|{nickname}|\n")
                temp.close()

                sendMessage(a, f"Seems like inventory of {nickname} has 0 CSGO items or is private.")
        else:
            sendMessage(a, f'Checking done successfully.')
            break

    f.close()
    os.remove(f'{a}.txt')
    os.rename(f'{a}_temp.txt', f'{a}.txt')


def getUpdates(c):
    URL = f'https://api.telegram.org/bot{token}/getUpdates?offset={c}'
    getRequest = requests.get(URL, proxies = httpsProxy).text
    dict = json.loads(getRequest)
    print(getRequest + "\n")
    if dict["result"] != []:
        #print(dict)
        text = dict["result"][0]["message"]["text"]
        sender = dict["result"][0]["message"]["from"]["id"]
        #print(sender)
        if text == '/help':
            sendMessage(sender,     'You can always see this menu using /help\n'
                                    'You can add a steam account using /addAccount [STEAMID64]\n'
                                    'You can check for changes in your inventory using /check\n' )
        elif text == '/start':
            sendMessage(sender,     'Hello!\n'
                                    'This bot will help you know if the number of Steam items in your CSGO inventory changes.\n'
                                    'To see the list of possible commands, type /help\n')
        elif text.split(" ")[0] == '/addAccount':
            addAccount(sender, text)
        elif text == '/check':
            check(sender)
        else:
            sendMessage(sender,     'Sorry, but i only understand commands listed in /help')
        return dict["result"][0]["update_id"]
    return 0


offset = 0

while True:
    b = getUpdates(offset)
    offset = b + 1
    time.sleep(0.25)