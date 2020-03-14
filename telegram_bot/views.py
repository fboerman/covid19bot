from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from telegram import Update
from .util import get_bot_dispatcher
from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
import json

@csrf_exempt
def callback(request, bottoken):
    if bottoken != settings.TELEGRAMBOT_TOKEN:
        return HttpResponseForbidden()

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest()

    dispatcher = get_bot_dispatcher()

    update = Update.de_json(data, dispatcher.bot)
    dispatcher.process_update(update)

    return JsonResponse({})