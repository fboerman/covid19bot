from django.conf import settings
from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler
from telegram.error import Unauthorized
from .models import Subscription
import logging
from sqlalchemy import inspect
from sqlalchemy.sql.sqltypes import BIGINT

def get_subscription(chat_id):
    try:
        return Subscription.objects.get(chat_id=chat_id)
    except Subscription.DoesNotExist:
        sub = Subscription(chat_id=chat_id)
        sub.save()
        return sub

def get_bot():
    return Bot(token=settings.TELEGRAMBOT_TOKEN)

def send_to_sub(sub, msg, bot=None):
    if bot is None:
        bot = get_bot()

    try:
        bot.send_message(chat_id=sub.chat_id, text=msg)
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

    def citieswarning(update,context):
        sub = get_subscription(update.message.chat_id)
        if len(context.args) < 1:
            context.bot.send_message(chat_id=update.message.chat_id, text="vereist argument, zie /help")
            return

        args = context.args[0].split(';')
        db = settings.DASHBOARD_DATA_ENGINE
        inspector = inspect(db)
        columns = inspector.get_columns('netherlands_cities')
        cities = [c['name'] for c in columns if type(c['type']) == BIGINT]
        cities.remove('index')

        illigal = set(args) - set(cities)
        if len(illigal) != 0:
            context.bot.send_message(chat_id=update.message.chat_id, text="Ongeldige steden: {}, moet een keuze zijn uit: {}".format(illigal, cities))
            return

        sub.citieswarning = str(context.args[0])
        sub.save()
        context.bot.send_message(chat_id=update.message.chat_id, text="Steden geupdate")  

    def help(update, context):
        helpmessage = """/help dit bericht\n
/tuewarning <0/1> - krijg bericht als tue nieuwe update pushed
/stadupdate <stad1;stad2> - krijg een update van nieuwe gevallen zodra RIVM dat pushed 
        """

        context.bot.send_message(chat_id=update.message.chat_id, text=helpmessage)

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('caps', caps))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('tuewarning', tuewarning))
    dispatcher.add_handler(CommandHandler('stadupdate', citieswarning))

    fh = logging.FileHandler('telegram.log')
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    for name in [name for name in logging.root.manager.loggerDict if 'telegram' in name]:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.addHandler(fh)

    return dispatcher
