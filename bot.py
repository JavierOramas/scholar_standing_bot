#! /root/anaconda3/bin/python
import os
from pyrogram import Client, filters
from read_config import read_config
import json
import requests
import schedule
import time

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
    name = str(users[-2])
    wallet = str(users[-1])
    
    os.makedirs("./db", exist_ok=True)
    db = read_data(message.chat.id)
    # db = read_data('1')
 
    if not name in db:
        db[name] = {
                    "wallet": wallet,
                    "slp": "0"
                    }
        write_data(message.chat.id,db)
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
            stand += f'{i[0]} : {i[1]}\n'
        message.reply_text(stand)
    else:
        message.reply_text('no tienes scholars :(')
    pass

# @app.on_message(filters.command('help'))
def get_snapshot():
    
    for cp,dir,files in os.walk('./db/'):
        for file in files:
            if file.endswith('.json'):
                user = file[:len('.json')]
                db = read_data(user)
        
                if len(db.keys()) > 0:
                    for i in db.keys():
                        wallet = db[i]['wallet']
                        slp = requests.get(f'https://game-api.skymavis.com/game-api/clients/{wallet}/items/1').json()['total']

                        
                        if slp > int(db[i]['slp']):
                            slp_new = slp-int(db[i]['slp'])
                        else:
                            slp_new = slp
                            
                        db[i]['slp'] = slp    
                        list.append((i,slp_new))

                    list.sort(key=lambda x:x[1], reverse=True)
                    stand = 'Weekly Snapshot:\n'
                    
                    for i in list:
                        stand += f'{i[0]} : {i[1]}\n'
                        
                    app.send_message(user,stand)
                
                    write_data(user,db)

    pass  

def scheduler_snapshot():
    from apscheduler.schedulers.background import BackgroundScheduler
    
    sched = BackgroundScheduler()
    sched.add_job(get_snapshot, 'cron', day_of_week='sun', hour=8, minute=0)
    sched.start()

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


scheduler_snapshot()
app.run()
