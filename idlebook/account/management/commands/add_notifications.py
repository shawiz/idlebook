"""
DEPRECATED!!!! see idlebook.account.notifications 
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils.translation import ugettext_noop as _
from django.db.models import signals

class Command(BaseCommand):
    args = '<None>'
    help = 'Add desired notifications'

    def handle(self, *args, **options):        
        from notification import models as notification
        notification.create_notice_type("request_received", _("Request Received"), _("you have received book request"))
        notification.create_notice_type("request_cancelled", _("Request Cancelled"), _("a book request has been cancelled"))
        notification.create_notice_type("request_responded", _("Request Responded"), _("your book request has been responded"))
        notification.create_notice_type("request_updated", _("Request Updated"), _("a book request has been updated"))
        notification.create_notice_type("price_updated", _("Price Updated"), _("price of the book you requested has been updated"))
        notification.create_notice_type("special_offer", _("Special Offer"), _("you received a speical offer for the book you requested"))
        notification.create_notice_type("review_received", _("Review Received"), _("you just received a review from someone"))
        
        if "notification" in settings.INSTALLED_APPS:
#            from notification import models as notification

            def create_notice_types(app, created_models, verbosity, **kwargs):
                notification.create_notice_type("request_received", _("Request Received"), _("you have received book request"))

            signals.post_syncdb.connect(create_notice_types, sender=notification)
        else:
            print "Skipping creation of NoticeTypes as notification app not found"
