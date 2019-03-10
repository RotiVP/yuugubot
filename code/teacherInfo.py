import ybclip
import ybcache

def teacherInfo(user_cache, rawvres, raweres, user_req):
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

    info = teacher_cache['info']

    personal_room = info['room']
    personal_campus = info['campus']
    
    email = info['email']
    phone = info['phone']

    text = f'{info["name"]}.\nДолжность: {info["post"]}, {info["unit"]}.\n'

    if personal_room is None or personal_campus is None:
        text += 'К сожалению, у меня нет данных о его личном кабинете.\n'
    else:
        text += f'Личный кабинет: {personal_room}, в корпусе {personal_campus}.\n'

    if phone is not None:
        text += f'Телефон: {info["phone"]}.\n'
    if email is not None:
        text += f'Адрес электронной почты: {info["email"]}.'

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
            'data': 'Шицелов',
        }
    }

    rawvres = {'response': {'text': 'Извините, я вас не понимаю...'}}
    raweres = {'error': ''}
    user_req = {'content': 'foo bar'}

    teacherInfo(user_cache, rawvres, raweres, user_req)
    print(rawvres)
    print(raweres)
    print(user_cache)
