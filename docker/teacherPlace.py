import ybclip
import ybcache

def teacherPlace(user_cache, rawvres, raweres, user_req):
    s = ybclip.cd_preprocess(user_cache['context_data'], 'data', rawvres, raweres)
    if s is not None: return s

    cdata = user_cache['context_data']['data']

    s = ybclip.name_preprocess(user_cache, rawvres, raweres, user_req) 
    if s is not None: return s
    cdata = user_cache['context_data']['data']

    teacher_cache = ybcache.get_cache(ybcache.short_name(cdata))
    if teacher_cache is None:
        rawvres['response']['text'] = 'Извините, мне не знакомо это имя...'
        rawvres['response']['buttons'] = [ybclip.catalog_button]
        return True

    timetable = teacher_cache['timetable'][0]
    info = teacher_cache['info']
    personal_room = info['room']
    personal_campus = info['campus']

    (npair_item,
    lpair_item,
    lgap,
    rgap,
    is_pair_cont) = ybclip.current_pair(timetable)

    text = 'У данного преподавателя {}'
    personalfail_text = ''
    if personal_room is None or personal_campus is None:
        personalfail_text = 'к сожалению, у меня нет данных о его личном кабинете.'

    if is_pair_cont:
        text = text.format(f'сейчас занятие в кабинете {lpair_item["room"]}, корпусе {lpair_item["campus"]}.')

    elif rgap is not None:
        text = text.format('сейчас перерыв, ')
        if personalfail_text:
            text += personalfail_text
        else:
            text += f'он может быть в кабинете {personal_room}, корпусе {personal_campus}.'
    else:
        text = text.format('сегодня нет занятий, ')
        if personalfail_text:
            text += personalfail_text
        else:
            text += f'но вы можете проверить кабинет {personal_room} в корпусе {personal_campus}.'

    rawvres['response']['text'] = text

    fixed_button = ybclip.catalog_button.copy()
    fixed_button['url'] += info['name'].replace(' ', '+')
    rawvres['response']['buttons'] = [fixed_button]

    return True

if __name__ == '__main__':
    user_cache = {
        'is_group': True,
        'clarification': '1162б',
        'last_context': '',
        'context_data': {
            'data': 'Годовников',
        }
    }

    rawvres = {'response': {'text': 'Извините, я вас не понимаю...'}}
    raweres = {'error': ''}
    user_req = {'content': 'foo bar'}

    teacherPlace(user_cache, rawvres, raweres, user_req)
    print(rawvres)
    print(raweres)
    print(user_cache)
