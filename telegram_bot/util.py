from django.conf import settings
from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler
from .models import Subscription
import logging


def get_subscription(chat_id, bot):
    try:
        return Subscription.objects.get(chat_id=chat_id)
    except Subscription.DoesNotExist:
        bot.send_message(chat_id=chat_id, text="Chat is not registered")
        return None


def get_bot_dispatcher():
    bot = Bot(token=settings.TELEGRAMBOT_TOKEN)
    dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

    def start(update, context):
        context.bot.send_message(chat_id=update.message.chat_id, text="Welkom bij Covid19 NL nieuws bot! "
                                                                      "Gebruik /help voor informatie voor gebruik")

    def caps(update, context):
        text_caps = ' '.join(context.args).upper()
        context.bot.send_message(chat_id=update.message.chat_id, text=text_caps)

    def help(update, context):
        helpmessage = """/help dit bericht
        """

        context.bot.send_message(chat_id=update.message.chat_id, text=helpmessage)

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('caps', caps))
    dispatcher.add_handler(CommandHandler('help', help))

    fh = logging.FileHandler('telegram.log')
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    for name in [name for name in logging.root.manager.loggerDict if 'telegram' in name]:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.addHandler(fh)

    return dispatcher