import yscache
import ybclip


def pairInfo(user_cache, rawvres, raweres, user_req, time):
    s = ybclip.cd_preprocess(user_cache['context_data'], 'data', rawvres, raweres)
    if s is not None: return s

    cdata = user_cache['context_data']['data']

    is_group = user_cache['context_data']['is_group'] 
    if is_group:
        s = ybclip.group_preprocess(user_cache, rawvres, raweres, user_req)
        if s is not None: return s
    else:
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

    day = 0 
    if time is not None and 'завтр' in time:
        day = 1 
    timetable = timetable[day]

    if is_group:
        pairs = {}
        for item in timetable:
            #в одно время могут начинаться дисциплины по выбору (сразу вся группа дисциплин)
            #либо занятия у подгрупп (не обязательно)
            pairs[item['start']] = item['discipline']
        pairs = pairs.values()
    else:
        pairs = {}
        for item in timetable:
            #может быть одна пара у нескольких групп
            pairs[item['start']] = item['discipline']
        pairs = pairs.values()

    if len(pairs) > 6:
        text = 'К сожалению, не получилось узнать, посмотрите на сайте.'
    elif len(pairs) > 0:
        text = '\n'.join(pairs)
    else:
        text = 'Занятий нет!'

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
            'data': '1162б',
            'is_group': True
        }
    }

    rawvres = {'response': {'text': 'Извините, я вас не понимаю...'}}
    raweres = {'error': ''}
    user_req = {'content': 'foo bar'}

    pairInfo(user_cache, rawvres, raweres, user_req, 'завтра')
    print(rawvres)
    print(raweres)
    print(user_cache)
