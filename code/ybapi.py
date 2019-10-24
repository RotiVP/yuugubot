import json
import re

import ybbrain
import yscache 
from pairPlace import pairPlace
from pairInfo import pairInfo
from teacherPlace import teacherPlace
from teacherInfo import teacherInfo


# body must be a json string
# must return a string response
def handleReqbody(body):

    #raw error response
    raweres = {
        'error': 'Unknown error'
    }

    # the input encoding should be UTF
    try:
        req = json.loads(body)
    except json.JSONDecodeError:
        raweres['error'] = 'Invalid json body of request'
        return json.dumps(raweres, indent=2)

    if req['version'] != '1.0':
        raweres['error'] = 'Only the first version of the protocol is supported now'
        return json.dumps(raweres, indent=2)

    #raw valid response
    rawvres = {
        'version': '1.0',
        'response': {
            'end_session': False,
        },
        'session': {
            'session_id': req['session']['session_id'],
            'message_id': req['session']['message_id'],
            'user_id': req['session']['user_id']
        }
    }
    

    if req['request']['original_utterance'] == 'ping':
        rawvres['response']['text'] = 'pong'
        rawvres['response']['end_session'] = True
        return json.dumps(rawvres, ensure_ascii=False, indent=None)

    if req['request']['original_utterance'] == 'test':
        rawvres['response']['text'] = 'hello'
        rawvres['response']['end_session'] = True
        return json.dumps(rawvres, ensure_ascii=False, indent=None)


    user_id = req['session']['user_id']
    user_cache = yscache.get_cache(user_id)
    # если кэш отчистился, а сессия у пользователя продолжается или пользователь новый
    if user_cache is None:
        user_cache = {
            'is_group': True,
            'clarification': None, #group or full name if teacher
            'last_context': '',
            'context_data': {} #data+is_group, отчищать при переключении контекста
        }

    if req['session']['new']:
        #сессия новая - контекст обязательно должен сброситься

        #request for user
        if 'bot_req' in user_cache: del user_cache['bot_req']
        reset_context(user_cache)

        # приветствие
        if not req['request']['original_utterance']:
            #text = 'Привет! {} Чем могу помочь?'
            text = 'Привет! {} Попробуйте узнать о занятии или преподавателе. Если у вас не получается, то спросите, что я умею.'
            if user_cache['clarification']:
                clar = user_cache['clarification']
                if user_cache['is_group']:
                    rawvres['response']['text'] = text.format(f'Ваша группа {clar}.')
                else:
                    rawvres['response']['text'] = text.format(f'Вас зовут {clar}.')
            else:
                rawvres['response']['text'] = text.format('')
            return json.dumps(rawvres, ensure_ascii=False, indent=None)
    else:
        # может переназначиться в будущем. Сделано так на случай ошибок
        rawvres['response']['text'] = 'Извините, я вас не понимаю...' 


    if 'bot_req' in user_cache:
        #user response
        status = handleResponse(user_cache, req['request'], rawvres, raweres)
    else:
        status = handleRequest(user_cache, req['request'], rawvres, raweres)

    #save user cache
    yscache.set_cache(user_id, user_cache)

    return json.dumps(
            rawvres if status else raweres,
            ensure_ascii=False,
            indent=None)


group_re = r'(?P<group>[А-яA-z0-9- ]+|)'
# регулярное выражение для ФИО слишком сложное (юзай именованные сущности яндекса)
name_re = r'(?P<name>.+)'

# здесь либо group, либо name, остальное None
# префикc У ГРУППЫ очень важен: указывает, что запрос в контексте группы, а не учителя (в случае ИИ тоже)
pair_cdata_re = f'(\\sу\\s((группы\\s*{group_re})|{name_re}))'

time_re = r'(?P<time>сегодн[А-я]|завтр[А-я])'
time_reobj = re.compile(time_re)

pairInfo_reobj = re.compile(f'^(а\\s*)?какие\\s*пары(\\s*{time_re})?{pair_cdata_re}?$')
pairInfo_rel_reobj = re.compile(f'^(а\\s*)?какие\\s*{time_re}{pair_cdata_re}?$')
pairPlace_reobj = re.compile(f'^(а\\s*)?(когда|где)\\s*(пара|занятие){pair_cdata_re}?$')

teacherPlace_reobj = re.compile(r'^(а\s*)?где\s*находится\s*')
teacherPlace_rel_reobj = [
        re.compile(r'^(а\s*)?где\s*(он|она)$'),
        re.compile(r'^(а\s*)?как\*мне\s*(его|ее)\s*найти$')]
teacherInfo_reobj = re.compile(r'^(а\s*)?кто\s*такой\s*')
teacherInfo_rel_reobj = re.compile(r'^(а\s*)?кто\s*это$')

setClar_reobj = re.compile(f'меня\\sзовут\\s{name_re}|моя\\sгруппа\\s{group_re}')


def insert_group(string, group):
    if string.find('у группы') >= 0:
        # когда там у группы пара (не путать с когда у меня пара)
        return string.replace('у группы', f'у группы {group}')
    else:
        # моя группа
        string += f' {group}'
        return string

# insert name continuation
def insert_name_cont(string, name_cont, pos):
    return string[:pos] + f' {name_cont}' + string[pos:]

def handleResponse(user_cache, req, rawvres, raweres):
    bot_req = user_cache.pop('bot_req')

    if bot_req['object'] == 'group':
        group = req['command']
        reres = re.match(f'^{group_re}$', group)
        if reres is None or not group:
            #не понимает
            return True

        substitution = bot_req['start_point'] #запрос пользователя, который породил уточняющий запрос бота

        #на группу именованные сущности не распространяются

        substitution['original_utterance'] = insert_group(substitution['original_utterance'], group)
        substitution['command'] = insert_group(substitution['command'], group)
        req = substitution
        #print(req)
        return handleRequest(user_cache, req, rawvres, raweres)

    elif bot_req['object'] == 'full_name':
        name_cont = req['command']
        parts = name_cont.split()
        if len(parts) != 2:
            return True

        s = bot_req['start_point']
        for entity in s['nlu']['entities']:
            if entity['type'] == 'YANDEX.FIO':
                entity['value']['first_name'] = parts[0]
                entity['value']['patronymic_name'] = parts[1]
                break

        # по хорошему нужно менять токены делать вставку, но это не обязательно в данной реализации

        req = s
        return handleRequest(user_cache, req, rawvres, raweres)
    else:
        raweres['error'] = 'Unknown the response object'
        return False


# предобработка и вызов функции/действия
#req['request']
def handleRequest(user_cache, req, rawvres, raweres):
    last_context = user_cache['last_context']
    entities = req['nlu']['entities']
    phrase = re.sub(
            r',|:|\.|\?|;|!|"|Спроси у|Скажи|Югорск.+ мудрец.+',
            '',
            req['original_utterance'].lower().strip())

    #обязательства перед яндексом
    if phrase in ['помощь', 'что ты умеешь']:
        rawvres['response']['text'] = (
        'Я могу подсказать вам: где и когда занятие, какие занятия сегодня или завтра, '
        'как найти преподавателя. Кстати, я знаю всех преподавателей в университете. Ну, '
        'или почти всех. Просто спросите меня! Вы можете сообщить мне свою группу или имя, '
        'если вы преподаватель, тогда я буду понимать, когда вы спрашиваете у себе. '
        'Произнести имя группы - непростая задача. Вместо этого я могу предложить вам '
        'ввести его. Попробуйте: "Когда пара у группы?"')
        return True


    # обработчика называть одноименно контексту и намерению

    # проверка относительных запросов (звучат только в рамках контекста)
    # проверка правильных запросов (также МОГУТ установить контекст)

    # pairInfo
    if last_context == 'pair':
        reres = re.match(pairInfo_rel_reobj, phrase)
        if reres is not None:
            fetch_pair_cd(user_cache, reres, entities)
            return pairInfo(
                    user_cache,
                    rawvres,
                    raweres,
                    req,
                    reres.group('time'))

    reres = re.match(pairInfo_reobj, phrase)
    if reres is not None:
        if last_context != 'pair':
            set_pair_context(user_cache, reres, entities)
        else:
            fetch_pair_cd(user_cache, reres, entities)
        return pairInfo(
                user_cache,
                rawvres,
                raweres,
                req,
                reres.group('time'))

    # pairPlace
    reres = re.match(pairPlace_reobj, phrase)
    if reres is not None:
        if last_context != 'pair':
            set_pair_context(user_cache, reres, entities)
        else:
            fetch_pair_cd(user_cache, reres, entities)
        return pairPlace(
                user_cache,
                rawvres,
                raweres,
                req)

    # teacherInfo
    if last_context == 'teacher':
        reres = re.match(teacherInfo_rel_reobj, phrase)
        if reres is not None:
            return teacherInfo(user_cache, rawvres, raweres, req)

    reres = re.match(teacherInfo_reobj, phrase)
    if reres is not None:
        if last_context != 'teacher':
            set_teacher_context(user_cache, entities)
        else:
            fetch_teacher_cd(user_cache, entities)
        return teacherInfo(user_cache, rawvres, raweres, req)

    # teacherPlace
    if last_context == 'teacher':
        reres = [re.match(obj, phrase) for obj in teacherPlace_rel_reobj]
        if any([res is not None for res in reres]):
            return teacherPlace(user_cache, rawvres, raweres, req)

    reres = re.match(teacherPlace_reobj, phrase)
    if reres is not None:
        if last_context != 'teacher':
            set_teacher_context(user_cache, entities)
        else:
            fetch_teacher_cd(user_cache, entities)
        return teacherPlace(user_cache, rawvres, raweres, req)

    # setClar
    reres = re.match(setClar_reobj, phrase)
    if reres is not None:
        reset_context(user_cache)
        if reres.group('group') is not None:
            #тут можно уточнение, если пустая, а можно и нет
            group = reres.group('group')
            if not group:
                return True
            if yscache.get_cache(group) is None:
                rawvres['response']['text'] = 'Извините, я не знаю такую группу...'
                return True
            user_cache['clarification'] = group
            user_cache['is_group'] = True
            rawvres['response']['text'] = 'Запомнила!'
            return True
        else:
            for item in entities:
                if item['type'] == 'YANDEX.FIO':
                    name = yfio2string(item['value'])

                    if len(name.split()) != 3:
                        rawvres['response']['text'] = 'Попробуйте снова с полным именем.'
                        return True

                    if yscache.get_cache(yscache.short_name(name)) is None:
                        rawvres['response']['text'] = 'Извините, мне это имя не знакомо...'
                        return True

                    user_cache['clarification'] = name
                    user_cache['is_group'] = False
                    rawvres['response']['text'] = 'Запомнила!'
                    return True


    # если алгоритм не помог, то попытка понять запрос

    # intent, context
    test = ybbrain.suppose(phrase, last_context)

    if test[1] == 'pair':
        #когда пара у моей группы, че когда там пара У ГРУППЫ
        reres = re.search(f'(\\sу\\sгруппы\\s*{group_re})', phrase)

        if last_context != test[1]:
            set_pair_context(user_cache, reres, entities)
        else: 
            fetch_pair_cd(user_cache, reres, entities)

        if test[0] == 'info':
            reres = re.search(time_reobj, phrase)
            return pairInfo(
                    user_cache,
                    rawvres,
                    raweres,
                    req,
                    reres.group(0) if reres is not None else reres)
        if test[0] == 'place':
            return pairPlace(
                    user_cache,
                    rawvres,
                    raweres,
                    req)

    if test[1] == 'teacher':
        if last_context != test[1]:
            set_teacher_context(user_cache, entities)
        else:
            fetch_teacher_cd(user_cache, entities)

        if test[0] == 'info':
            return teacherInfo(user_cache, rawvres, raweres, req)
        if test[0] == 'place':
            return teacherPlace(user_cache, rawvres, raweres, req)

    raweres['error'] = 'Can not to handle the request'
    return False

def reset_context(user_cache):
    user_cache['context_data'].clear()
    user_cache['last_context'] = ''

def yfio2string(fio_dict):
    #алмазов олег викторович
    fio_arr = []
    if 'last_name' not in fio_dict:
        return ''
    fio_arr.append(fio_dict['last_name'])

    if 'first_name' in fio_dict and 'patronymic_name' in fio_dict:
        fio_arr.append(fio_dict['first_name'])
        fio_arr.append(fio_dict['patronymic_name'])

    # + привести в порядок регистр
    return yscache.fix_name(' '.join(fio_arr))

def fetch_pair_cd(user_cache, reres, entities):
    if reres is not None:
        if reres.group('group') is not None:
            #может быть пустой, уточнение сгенерируется в обработчике 
            user_cache['context_data']['data'] = reres.group('group').replace(" ", "")
            user_cache['context_data']['is_group'] = True
            return

    if entities is not None:
        for item in entities:
            if item['type'] == 'YANDEX.FIO':
                #фамиля или полное имя, в первом случае уточнение сгенерируется (в обработчике)
                #может быть пустым. Тогда не поняла
                user_cache['context_data']['data'] = yfio2string(item['value'])
                user_cache['context_data']['is_group'] = False
                break

def set_pair_context(user_cache, reres, entities):
    reset_context(user_cache)
    
    user_cache['context_data']['data'] = user_cache['clarification']
    user_cache['context_data']['is_group'] = user_cache['is_group']
    fetch_pair_cd(user_cache, reres, entities)

    user_cache['last_context'] = 'pair'

def fetch_teacher_cd(user_cache, entities):
    for item in entities:
        if item['type'] == 'YANDEX.FIO':
            user_cache['context_data']['data'] = yfio2string(item['value'])
            break

def set_teacher_context(user_cache, entities):
    reset_context(user_cache)

    fetch_teacher_cd(user_cache, entities)

    user_cache['last_context'] = 'teacher'
