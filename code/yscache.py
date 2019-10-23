# кэшируются данные с сервера ЮГУ
# может возникнуть проблема с фамилиями с одинаковыми инициалами

import redis
import requests
import json
import datetime
import re
import pytz

rcon = redis.Redis(host='172.19.0.3', port=6379, db=0)

zoneinfo = pytz.timezone('Asia/Yekaterinburg')
ugrasu_api = 'http://api.ugrasu.ru/api.php?'

def get_cache(key, complete=True):
    if complete:
        data = rcon.get(key)
        if data is None: return None
        else: return json.loads(data)
 
    else:
        data = []
        for vkey in rcon.keys(pattern=key+' *'):
            data.append(json.loads(rcon.get(vkey)))
        return data

def set_cache(key, value):
    rcon.set(key, json.dumps(value))   

def parse_place(place):
    #СОК/БАСС
    #Ерм./ЕР10
    if place is None:
        return None, None
    place_re = r'(?P<campus>\d+|СОК)/(?P<room>\d+|БАСС)'
    reres = re.search(place_re, place)
    room = reres.group('room') if reres is not None else None
    campus = reres.group('campus') if reres is not None else None
    return campus, room

def fix_name(name):
    words = list(map(lambda word: word.capitalize(), name.split()))
    return ' '.join(words)

def short_name(name):
    #БУЛЫГИН КОНСТАНТИН СЕРГЕЕВИЧ
    #Сомикова К.C.
    name = fix_name(name)
    words = name.split(' ')
    return words[0] + f' {words[1][0]}.{words[2][0]}.'

def get_ok_json(resp, dname=None):
    if resp.status_code != requests.codes.ok:
        return None

    try:
        ok_json = resp.json()
    except ValueError:
        return None

    #if dname is not None:
    #    with open(dname+'.json', 'w') as f:
    #        json.dump(ok_json, f, indent=2, ensure_ascii=False)

    return ok_json

def update_cache():
    day = datetime.datetime.now(zoneinfo).date().strftime('%Y.%m.%d')
    next_day = (datetime.datetime.now(zoneinfo) + datetime.timedelta(days=1)).date().strftime('%Y.%m.%d') 

    #rcon.set('123450', json.dumps({'clarification': '1162б', 'is_group': True}))
    #print(json.loads(rcon.get('123450')))

    teacher_data = {}
    group_data = {}

    # timetable
    #url = ugrasu_api + urllib.parse.urlencode({'view': 'timetable'})

    resp = requests.get(ugrasu_api, params={'view': 'timetable'})
    fat_tt = get_ok_json(resp, 'timetable')
    if fat_tt is None: return

    for item in fat_tt:
        group = item['group'].strip()
        if group not in group_data:
            group_data[group] = [[], []]
        teacher = item['lecturer'].strip()
        if teacher not in teacher_data:
            teacher_data[teacher] = {'timetable': [[], []]}

        if item['date'] == day:
            day_idx = 0
        elif item['date'] == next_day:
            day_idx = 1
        else:
            continue

        timetable = {}
     
        timetable['campus'], timetable['room'] = parse_place(item['classroom'])

        timetable['start'] = item['time_start']
        timetable['end'] = item['time_end']

        long_disc = item['discipline']
        avlen = 90 #average length
        disc_words = []
        for word in long_disc.split():
            disc_words.append(word)
            avlen -= len(word)
            if (avlen <= 0): 
                disc_words.append('...')
                break
        timetable['discipline'] = ' '.join(disc_words)

        #1162б
        group_timetable = timetable.copy()
        group_timetable['subgroup'] = item['subgroup'] #может быть None (json null)
        group_data[group][day_idx].append(group_timetable)
        #Русанов М.А.
        teacher_data[teacher]['timetable'][day_idx].append(timetable)

    # teacher info
    resp = requests.get(ugrasu_api, params={'view': 'contacts'})
    fat_contacts = get_ok_json(resp, 'contacts')
    if fat_contacts is None: return

    #f = open('log.txt', 'w')
    #f.write('\n'.join(teacher_data.keys()))
    #f.write('\n')

    for contact in fat_contacts:
        #f.write('\n' + short_name(contact['FIO']))

        shname = short_name(contact['FIO'])
        if shname in teacher_data:
            info = {}
            info['name'] = fix_name(contact['FIO'])
            info['email'] = contact['EMAIL'] #может быть None
            info['phone'] = contact['PHONE']
            info['post'] = contact['DOL']
            info['unit'] = contact['PATH']
            info['campus'], info['room'] = parse_place(contact['KORP'])

            teacher_data[shname]['info'] = info

            #f.write('\n' + short_name(contact['FIO']))

    # save
    for data in [group_data, teacher_data]:
        for key, value in data.items():
            set_cache(key, value)
            

# for test only
if __name__ == '__main__':
    update_cache()

    test1 = get_cache('1162б')
    test2 = get_cache('Шицелов А.В.')
    test3 = get_cache(key='Орлов', complete=False)
    print('group')
    print(json.dumps(test1, indent=2))
    print('teacher')
    print(json.dumps(test2, indent=2))
    print('smooth teacher')
    print(json.dumps(test3, indent=2))
