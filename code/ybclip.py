from datetime import timedelta, time, datetime

import yscache


pair_duration = timedelta(minutes=95)

group_tt_button = {
    'title': 'Расписание для группы',
    #'payload': {},
    'url': 'http://timetable.ugrasu.ru/index.php/list_of/inst/42',
    #'hide': True
}
teacher_tt_button = {
    'title': 'Расписание для преподавателя',
    'url': 'http://timetable.ugrasu.ru/index.php/list_of/prepods',
}
catalog_button = {
    'title': 'Справочник',
    'url': 'http://timetable.ugrasu.ru/index.php/search/get_info?s_info=',
}

def smart_ending(number, forms, base = ''):
    rest = number % 10
    number = int(str(number)[-2:])
    if rest == 1 and number != 11:
        return base + forms[0]
    elif rest in [2, 3, 4] and number not in [12, 13, 14]:
        return base + forms[1];
    else:
        return base + forms[2];

def pair_time(string):
    return time(int(string[:2]), int(string[-2:]))

def current_pair(timetable):
    day = datetime.now(yscache.zoneinfo)

    npair_item = None
    lpair_item = None
    lgap = None #left gap
    rgap = None #right gap
    for item in timetable:
        gap = datetime.combine(day.date(), pair_time(item['start']), day.tzinfo) - day 
        if gap.days >= 0 and (rgap is None or gap < rgap):
            rgap = gap 
            npair_item = item
        elif gap.days < 0 and (lgap is None or gap > lgap):
            lgap = gap 
            lpair_item = item

    is_pair_cont = (
            lpair_item is not None and
            datetime.combine(day.date(), pair_time(lpair_item['start']), day.tzinfo) + pair_duration > day)
    
    return npair_item, lpair_item, lgap, rgap, is_pair_cont

#process data preprocess
def cd_preprocess(context_data, key, rawvres, raweres):
    # если не было контекстных данных (и пользователь не представился)
    if key not in context_data or context_data[key] is None:
        return True

    return None

def group_preprocess(user_cache, rawvres, raweres, user_req):
    # сказал про группу, но не указал ее
    cdata = user_cache['context_data']['data']
    if not cdata:
        bot_req = { 
            'object': 'group',
            'start_point': user_req}
        user_cache['bot_req'] = bot_req
        # в обработчике запроса нужно выдавать непонимание на снова пустую группу
        rawvres['response']['text'] = 'Уточните группу, пожалуйста.'
        return True

    return None

def name_preprocess(user_cache, rawvres, raweres, user_req):
    # сказал не полное имя. Предлагаем варианты к фамилии
    cdata = user_cache['context_data']['data']
    name_parts = len(cdata.split())

    if name_parts == 1: 
        options = yscache.get_cache(key=cdata, complete=False)
        buttons = []
        for option in options:
            button = {
                #отправится в качестве реплики, если не указан url
                'title': ' '.join(option['info']['name'].split()[1:]),
                'hide': True
            }
            buttons.append(button)

        if len(buttons) > 1:
            bot_req = { 
                'object': 'full_name',
                'start_point': user_req}
            user_cache['bot_req'] = bot_req
            rawvres['response']['text'] = 'Уточните имя, пожалуйста.'
            rawvres['response']['buttons'] = buttons
            return True
        elif len(buttons) == 1:
            user_cache['context_data']['data'] = option['info']['name']
        else:
            rawvres['response']['text'] = 'Извините, мне не знакома эта фамилия...'
            rawvres['response']['buttons'] = [teacher_tt_button, catalog_button]
            return True

    elif name_parts != 3:
        rawvres['response']['text'] = 'Извините, я не смогла разобрать имя...'
        rawvres['response']['buttons'] = [teacher_tt_button, catalog_button]
        return True

    return None
