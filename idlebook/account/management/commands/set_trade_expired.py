from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from idlebook.account.models import Trade
from time import localtime, strftime

import logging
logger = logging.getLogger("django")


class Command(BaseCommand):
    args = '<None>'
    help = 'Make all the expired (in days) trades expired (in database)'

    def handle(self, *args, **options):
        trades = Trade.objects.filter(request_status__lt=3)
        for trade in trades:
            trade.set_expired()
        logger.info('[%s] all set expired' % strftime("%a, %d %b %Y %H:%M:%S", localtime()))