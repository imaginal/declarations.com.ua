import json
from random import choice
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from spotter.utils import reverse_qs
from chatbot.utils import ukr_plural, chat_response, simple_search


COMMON_ANSWERS = {
    'дякую': ['Будь ласка.', 'Нема за що!', 'Користуйтесь на здоров\'я', 'Дякую, що користуєтесь.'],
    'спасибо': ['Пожалуйста', 'Не за что', 'Чому не державною?'],
}


def send_greetings(data):
    for member in data['membersAdded']:
        if 'Bot' in member['name']:
            continue
        data['from'] = {'id': data['conversation']['id']}
        message = 'Вітаю, {}!\n\n'.format(member['name'])
        message += 'Яку декларацію ти шукаєш сьогодні?'
        chat_response(data, message)


def show_details(data):
    decl_id = data['text'][6:]
    chat_response(data, decl_id)


def join_res(d, keys, sep=' '):
    return sep.join([str(d[k]) for k in keys if k in d and d[k]])


def search_reply(data):
    if 'text' not in data or len(data['text']) < 4:
        chat_response(data, 'Не зрозумів, уточніть запит.')
        return

    text = data['text'].strip().lower()

    if text in COMMON_ANSWERS:
        message = COMMON_ANSWERS[text]
        if isinstance(message, list) or isinstance(message, tuple):
            message = choice(message)
        chat_response(data, message)
        return

    search = simple_search(data['text'])
    plural = ukr_plural(search.found_total, 'декларація', 'декларації', 'декларацій')
    message = 'Знайдено {} {}'.format(search.found_total, plural)
    if search.found_total > 10:
        message += '\n\nПоказані перші 10'
    attachments = None

    if search.found_total:
        attachments = []
        for found in search:
            if 'date' in found.intro:
                found.intro.date = 'подана ' + str(found.intro.date)[:10]
            if 'corrected' in found.intro:
                if found.intro.corrected:
                    found.intro.corrected = 'Уточнена'
            url = settings.EMAIL_SITE_URL + reverse('details', args=[found.meta.id])
            att = {
                "contentType": "application/vnd.microsoft.card.hero",
                "content": {
                    "title": join_res(found.general, ('last_name', 'name', 'patronymic'), ' '),
                    "subtitle": join_res(found.intro, ('declaration_year', 'doc_type', 'corrected', 'date'), ', '),
                    "text": join_res(found.general.post, ('region', 'office', 'post'), ', '),
                    "buttons": [
                        {
                            "type": "openUrl",
                            "title": "Відкрити",
                            "value": url
                        }
                    ]
                }
            }
            if 'url' in found.declaration:
                button = {
                    "type": "openUrl",
                    "title": "Показати оригінал",
                    "value": found.declaration.url
                }
                att['content']['buttons'].append(button)

            attachments.append(att)

            if len(attachments) >= 10:
                url = settings.EMAIL_SITE_URL + reverse_qs('search', qs={'q': data['text']})
                att = {
                    "contentType": "application/vnd.microsoft.card.hero",
                    "content": {
                        "title": "Більше декларацій",
                        "subtitle": "Щоб побачити більше перейдіть на сайт",
                        "buttons": [
                            {
                                "type": "openUrl",
                                "title": "Продовжити пошук на сайті",
                                "value": url
                            }
                        ]
                    }
                }
                attachments.append(att)
                break

    chat_response(data, message, attachments=attachments)


@csrf_exempt
def messages(request):
    if request.method != 'POST':
        return HttpResponse('Method Not Allowed', status_code=405)

    data = json.loads(request.body.decode('utf-8'))

    if data['type'] == 'conversationUpdate':
        send_greetings(data)

    elif data['type'] == 'message':
        search_reply(data)

    return HttpResponse('OK')
