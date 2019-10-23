from datetime import datetime

import yscache
import ybclip


def pairPlace(user_cache, rawvres, raweres, user_req): 
    s = ybclip.cd_preprocess(user_cache['context_data'], 'data', rawvres, raweres)
    if s is not None: return s

    cdata = user_cache['context_data']['data']

    is_group = user_cache['context_data']['is_group'] 
    if is_group:
        s = ybclip.group_preprocess(user_cache, rawvres, raweres, user_req)
        if s is not None: return s
    else:
        #может дополнить фамилию, если один вариант
        s = ybclip.name_preprocess(user_cache, rawvres, raweres, user_req) 
        if s is not None: return s
        cdata = user_cache['context_data']['data']

    if is_group:
        timetable = yscache.get_cache(cdata)
        if timetable is None:
            rawvres['response']['text'] = 'Извините, мне не знакома эта группа...'
            rawvres['response']['buttons'] = [ybclip.group_tt_button]
            return True
    else:
        teacher_cache = yscache.get_cache(yscache.short_name(cdata))
        if teacher_cache is None:
            rawvres['response']['text'] = 'Извините, мне не знакомо это имя...'
            rawvres['response']['buttons'] = [ybclip.teacher_tt_button]
            return True
        timetable = teacher_cache['timetable']
    #print(timetable)
    timetable = timetable[0]

    (npair_item,
    lpair_item,
    lgap,
    rgap,
    is_pair_cont) = ybclip.current_pair(timetable)

    text = '{} в кабинете {}, в корпусе {}, '
    if is_pair_cont:
        text = text.format(lpair_item['discipline'], lpair_item['room'], lpair_item['campus']) + 'уже идет!'
    elif rgap is not None:
        room = npair_item['room']
        campus = npair_item['campus']
        minutes = rgap.seconds//60
        hours = minutes//60
        if hours > 0:
            postfix = str(hours) + ' ' + ybclip.smart_ending(hours, ['час', 'часа', 'часов'])
        else:
            postfix = str(minutes) + ' ' + ybclip.smart_ending(minutes, ['минуту', 'минуты', 'минут'])
        text = text.format(npair_item['discipline'], room, campus) + 'начало через ' + postfix + '!'
    else:
        text = 'Сегодня занятий не будет!'

    rawvres['response']['text'] = text
    if is_group:
        rawvres['response']['buttons'] = [ybclip.group_tt_button]
    else:
        rawvres['response']['buttons'] = [ybclip.teacher_tt_button]
    return True



if __name__ == '__main__':
    user_cache = {
        'is_group': True,
        'clarification': '1162б',
        'last_context': '',
        'context_data': {
            # имена в нижнем регистре сюда не попадут, см yfio2string
            'data': 'Шицелов',
            'is_group': False
        }
    }

    rawvres = {'response': {'text': 'Извините, я вас не понимаю...'}}
    raweres = {'error': ''}
    user_req = {'content': 'foo bar'}

    pairPlace(user_cache, rawvres, raweres, user_req)
    print(rawvres)
    print(raweres)
    print(user_cache)
