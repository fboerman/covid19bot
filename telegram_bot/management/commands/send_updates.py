from django.core.management.base import BaseCommand
from telegram_bot.models import Subscription
from django.conf import settings
from telegram_bot.util import send_to_sub, get_bot

class Command(BaseCommand):
    help = 'Send updates to subscribers'

    def handle(self, *args, **options):
        self.stdout.write('Sending updates to subscribers')
        self.update(**options)

    def add_arguments(self, parser):
        parser.add_argument('--tueupdate', action='store_true', help='send broadcast for TU/e')
        parser.add_argument('--rivmupdate', action='store_true', help='send number updates for cities')

    def update(self, **options):
        bot = get_bot()

        if not options['tueupdate'] and not options['rivmupdate']:
            self.stdout.write('nothing to do')
            return

        num_tueupdate = 0
        num_citiesupdate = 0

        db = settings.DASHBOARD_DATA_ENGINE
        for sub in Subscription.objects.all():
            if sub.tuewarning and options['tueupdate']:
                send_to_sub(sub, "TU/e heeft een nieuwe update gepushed, mirror is te zien op: https://mirrors.boerman.dev/tuecorona.png", bot)
                num_tueupdate += 1
            if options['rivmupdate']:
                cities = str(sub.citieswarning).split(';')
                cities.remove('')
                if len(cities) > 0:
                    sql = "select \"" + '","'.join(cities) +  "\" from netherlands_cities ORDER BY time DESC LIMIT 1"
                    with db.connect() as con:
                        try:
                            row = con.execute(sql)
                        except:
                            self.stdout.write("error in query: {} for cities: {} for chat id: {}".format(sql, cities, sub.chat_id))
                        data = list(list(row)[0])
                    msg = "RIVM update: \n"
                    
                    for d in zip(cities, data):
                        msg += "{}\t{}\n".format(d[0], d[1])
                    send_to_sub(sub, msg, bot)

                    num_citiesupdate += 1

        self.stdout.write("send {} tue updates and {} cities updates".format(num_tueupdate, num_citiesupdate))
            

