from django.conf import settings
from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler
from telegram.error import Unauthorized
from .models import Subscription
import logging
from telegram_bot.data_util import *

def get_subscription(chat_id):
    try:
        return Subscription.objects.get(chat_id=chat_id)
    except Subscription.DoesNotExist:
        sub = Subscription(chat_id=chat_id)
        sub.save()
        return sub

def get_bot():
    return Bot(token=settings.TELEGRAMBOT_TOKEN)

def send_to_sub(sub, msg, bot=None, parsemode=None):
    if bot is None:
        bot = get_bot()

    try:
        bot.send_message(chat_id=sub.chat_id, text=msg, parse_mode=parsemode)
    except Unauthorized as e:
        # if the user has blocked the bot, throw away the subscription
        if str(e) == 'Forbidden: bot was blocked by the user':
            sub.delete()


def get_bot_dispatcher():
    bot = get_bot()
    dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

    def start(update, context):
        sub = get_subscription(update.message.chat_id)
        context.bot.send_message(chat_id=update.message.chat_id, text="Welkom bij Covid19 NL nieuws bot! "
                                                                      "Gebruik /help voor informatie voor gebruik")

    def caps(update, context):
        text_caps = ' '.join(context.args).upper()
        context.bot.send_message(chat_id=update.message.chat_id, text=text_caps)

    def tuewarning(update, context):
        sub = get_subscription(update.message.chat_id)
        if len(context.args) < 1:
            context.bot.send_message(chat_id=update.message.chat_id, text="vereist argument, zie /help")
            return
        try:
            arg = bool(int(context.args[0]))
        except:
            context.bot.send_message(chat_id=update.message.chat_id, text="verkeerd argument, zie /help")
            return
        sub.tuewarning = arg
        sub.save()
        context.bot.send_message(chat_id=update.message.chat_id, text="TU/e push bericht ge{}activeerd".format("de" if not arg else ""))

    def subtocity(update, context):
        sub = get_subscription(update.message.chat_id)
        if len(context.args) < 1:
            context.bot.send_message(chat_id=update.message.chat_id, text="Vereist argument, zie /help")
            return

        if context.args[0] not in validcities():
            context.bot.send_message(chat_id=update.message.chat_id, text="Ongeldige gemeente, zie /gemeenten voor een lijst van opties")
            return

        existing = set(sub.citieswarning.split(';'))
        existing.add(context.args[0])
        sub.citieswarning = ";".join(existing)
        sub.save()

        context.bot.send_message(chat_id=update.message.chat_id, text= "Subscription geupdate")

    def unsubtocity(update, context):
        sub = get_subscription(update.message.chat_id)
        if len(context.args) < 1:
            context.bot.send_message(chat_id=update.message.chat_id, text="Vereist argument, zie /help")
            return

        existing = set(sub.citieswarning.split(';'))
        try:
            existing.remove(context.args[0])
        except KeyError:
            context.bot.send_message(chat_id=update.message.chat_id, text="Deze stad stond niet in subscriptions")
            return

        sub.citieswarning = ";".join(existing)
        sub.save()
        context.bot.send_message(chat_id=update.message.chat_id, text="Subscription geupdate")

    def cities(update, context):
        sub = get_subscription(update.message.chat_id)
        context.bot.send_message(chat_id=update.message.chat_id, text=str(validcities()))

    def status(update, context):
        sub = get_subscription(update.message.chat_id)
        cities = sub.citieswarning.split(';')
        msg = "Laatste RIVM data:\n ``` " + get_latest_rivm_datatable(cities) + " ``` "

        context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode='MarkdownV2')

    def top20(update, context):
        msg = "top 20 gemeenten:\n ``` " + get_top20_datatable() + " ``` "

        context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode='MarkdownV2')

    def help(update, context):
        helpmessage = """/help dit bericht
/tuewarning <0/1> - krijg bericht als TU/e nieuwe update pushed
/subscribestad stad - krijg een update van stand van corona gevallen zodra het RIVM dat pushed
/unsubscribestad stad - zet stad update uit
/status - krijg een een stand van zaken van je geselecteerde steden volgens laatste data van RIVM
/gemeenten - lijst van alle ondersteunde gemeenten
/top20 - de top 20 van nederlandse gemeente met actieve corona gevallen 
        """

        context.bot.send_message(chat_id=update.message.chat_id, text=helpmessage)

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('caps', caps))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('tuewarning', tuewarning))
    dispatcher.add_handler(CommandHandler('subscribestad', subtocity))
    dispatcher.add_handler(CommandHandler('unsubscribestad', unsubtocity))
    dispatcher.add_handler(CommandHandler('gemeenten', cities))
    dispatcher.add_handler(CommandHandler('status', status))
    dispatcher.add_handler(CommandHandler('top20', top20))

    fh = logging.FileHandler('telegram.log')
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    for name in [name for name in logging.root.manager.loggerDict if 'telegram' in name]:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.addHandler(fh)

    return dispatcher
