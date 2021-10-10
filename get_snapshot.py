import os
import requests
import json
from bs4 import BeautifulSoup

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
import requests


def get_snapshot():
    for cp,dir,files in os.walk('./db/'):
        for file in files:
            if file.endswith('.json'):
                user = file[:-len('.json')]
                db = read_data(user)
                list = []
                print(db)
                if len(db.keys()) > 0:
                    for i in db.keys():
                        wallet = db[i]['wallet']
                        yesterday = db[i]['yesterday']
                        slp = requests.get(f'https://game-api.skymavis.com/game-api/clients/{wallet}/items/1').json()['total']


                        if slp >= yesterday:
                            slp_new = slp-yesterday
                        else:
                            slp_new = slp

                        db[i]['slp'].append(slp_new)
                        db[i]['yesterday'] = slp
                        if len(db[i]['slp']) > 14:
                            db[i]['slp'] = db[i]['slp'][-14:]
                        list.append((i,slp_new))
                    write_data(user,db)

    pass

get_snapshot()