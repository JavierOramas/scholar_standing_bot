#! /root/anaconda3/bin/python
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import Client, filters
from read_config import read_config
import json
import requests
import schedule
import time

def get_value_usd(sum):
    price = requests.get('https://api.coingecko.com/api/v3/simple/token_price/ethereum?contract_addresses=0xcc8fa225d80b9c7d42f96e9570156c65d6caaa25&vs_currencies=usd').json()['0xcc8fa225d80b9c7d42f96e9570156c65d6caaa25']['usd']
    return price*sum

def read_data(id):
    id = str(id)

    try:
        with open('./db/'+id+'.json', 'r') as f:
            return json.loads(f.readline())
    except:
        return {}
    
def write_data(id,db):
    id = str(id)
    with open('./db/'+id+'.json', 'w') as f:
        f.write(json.dumps(db))

config_data = read_config('./config/config_bot.json')
app = Client(config_data['bot_user_name'], config_data['api_id'], config_data['api_hash'])

@app.on_message(filters.command('add'))
def add_scholar(client, message):
    users = message.text.split()
    if len(users) != 3:
         message.reply_text("formato incorrecto, debe ser de la forma: \n /add pedro 0x000000000")
    name = str(users[-2])
    wallet = str(users[-1])
    
    os.makedirs("./db", exist_ok=True)
    db = read_data(message.chat.id)
    # db = read_data('1')
 
    if not name in db:
        db[name] = {
                    "wallet": wallet,
                    "slp": "[0]"
                    }
        write_data(message.chat.id,db)
        message.reply_text("Añadido con éxito")
    else:
        message.reply_text("Ya tienes un scholar con ese nombre")
    pass

@app.on_message(filters.command('del'))
def del_scholar(client, message):
    users = message.text.split()
    name = str(users[-2])
    # wallet = str(users[-1])
    
    os.makedirs("./db", exist_ok=True)
    db = read_data(message.chat.id)
    # db = read_data('1')
 
    if name in db:
        db.pop(name)
        write_data(message.chat.id,db)
    else:
        message.reply_text("no tienes un scholar con ese nombre")
    pass

@app.on_message(filters.command('standing'))
def see_fee(client, message):
    # owner_id = app.get_users(message.chat.id)
    
    os.makedirs("./db", exist_ok=True)
    db = read_data(message.chat.id)
    list = []
    
    if len(db.keys()) > 0:
        for i in db.keys():
            wallet = db[i]['wallet']
            slp = requests.get(f'https://game-api.skymavis.com/game-api/clients/{wallet}/items/1').json()['total']
            list.append((i,slp))
            
        list.sort(key=lambda x:x[1], reverse=True)
        stand = ''
        for i in list:
            stand += f'{i[0]} : {i[1]} - ${get_value_usd(i[1])}\n'
        message.reply_text(stand)
    else:
        message.reply_text('no tienes scholars :(')
    pass

@app.on_message(filters.command('week'))
def see_fee(client, message):
    # owner_id = app.get_users(message.chat.id)
    
    os.makedirs("./db", exist_ok=True)
    db = read_data(message.chat.id)
    list = []
    
    if len(db.keys()) > 0:
        for i in db.keys():
            slp = sum(db[i]['slp'])
            list.append((i,slp))
            
        list.sort(key=lambda x:x[1], reverse=True)
        stand = ''
        for i in list:
            stand += f'{i[0]} : {i[1]} - ${get_value_usd(i[1])}\n'
        message.reply_text(stand)
    else:
        message.reply_text('no tienes scholars :(')
    pass

# @app.on_message(filters.command('help'))


@app.on_message(filters.command('help'))
@app.on_message(filters.command('start'))
def help(client, message):
    
    message.reply_text("""
    /add nombre wallet - añade el usuario a tu lista de scholars, recuerda sustituir ronin: por 0x\n
    /del nombre - elimina el usuario de tu lista\n
    /standing - muestra todos los scholars ordenados\n
    Puedes contribuir con el desarrollo aqui: https://github.com/JavierOramas/scholar_standing_bot\no puedes donar para contribuir al desarrollo: 0x64eF391bb5Feae6023440AD12a9870062dd2B342
    """)
    pass

app.run()