from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from idlebook.account.models import Lease
from time import localtime, strftime

import logging
logger = logging.getLogger("django")


class Command(BaseCommand):
    args = '<None>'
    help = 'Set due states and send due reminders to renters'

    def handle(self, *args, **options):
        leases = Lease.objects.filter(request_status=1)
        for lease in leases:
            lease.set_due()
            lease.check_due_reminder()
        logger.info('[%s] all set due or sent reminder' % strftime("%a, %d %b %Y %H:%M:%S", localtime()))
