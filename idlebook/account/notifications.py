from notification import models as notification
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_noop as _
from django.dispatch import Signal, receiver
from django.db import models
from django.contrib.auth.models import User


import logging
logger = logging.getLogger(__name__)

# roles:
# 0 system
# 1 seller
# 2 buyer

#actions:
actions = {
    0: 'none',
    1: 'accepted',
    2: 'rejected',
    3: 'canceled',
    4: 'ignored',
    5: 'expired',
    6: 'due',
    7: 'set price',
}

STATES = {
    # special case pseudo state
    -1: {
        '21': ['request_received',],
        '06': ['remind_due',],
    },
# phase 0
# state 0 doesn't exist anymore
#    # init with seller price not set
#    0: {
#        '05': 'request_expired', 
#        '12': 'request_responded',
#        '14': None,
#        '17': 'price_updated',
#        '23': 'request_canceled',
#    },
    # seller set price
    1: {
        '05': ['request_expired',],
        '12': ['request_rejected',],
        '14': None,
        '17': ['price_updated',],
        '21': ['request_received',],
        '23': ['request_canceled',],
    },
    # (init with) seller price set
    2: {
        '05': ['request_expired',],
        '11': ['request_accepted',],
        '12': ['request_rejected',],
        '14': None,
        '17': ['price_updated',],
        '23': ['request_canceled',],
    },
    # ignored40
    3: {
        '05': ['request_expired',],
        '23': None, # Not sure: can be 'request_canceled' if ignoring still allow notify
    },
    # phase 1
    # seller accepted request
    10: {
        '05': ['request_expired',],
        '11': ['dropoff_notice', 'dropoff_confirm'],
        '13': ['request_canceled',],
        '23': ['request_canceled',],
    },
    # phase 2
    # buyer needs to pick up
    20: {
        '05': ['request_expired_pickup',],
        '21': ['pickup_notice',],
        '22': ['pickup_reject',],
    },
    # expired, seller needs pick up
    21: {
        '05': ['contact_us_pickup',],
        '11': None,
    },
    # buyer rejected, seller needs pick up
    22: {
        '05': ['contact_us_pickup',],
        '11': None,
    },
    # phase 3
    # buyer pick up
    30: {
        '06': ['book_due',], # send reminder to buyer
        '21': ['dropoff_notice', 'dropoff_confirm'],
        '28': ['request_renew',],
    },
    # buyer requested renew
    31: {
        '06': ['book_due',], # requested and due
        '11': ['request_accepted',],
        '12': ['request_rejected',],
        '23': ['request_canceled',],
    },
    # after due 
    32: {
        '05': ['contact_us_refund'],
        '21': ['dropoff_notice', 'dropoff_confirm'], # penalty fine?
        '28': ['request_renew',],
    },
    # due while buyer request renew
    33: {
        '05': ['contact_us_refund'],
        '11': ['request_accepted',],
        '12': ['request_rejected',],
    },
    # phase 4
    # buyer drop off, seller needs pick up
    40: {
        '05': ['contact_us_pickup',],
        '11': None,
    },
}

notification_types = {
    'request_received': ('Request Received', 'you have received book request'),
    'request_canceled': ('Request Canceled', 'a book request has been canceled'),
    'request_accepted': ('Request Accepted', 'your book request has been accepted'),
    'request_rejected': ('Request Rejected', 'your book request has been rejected'),
    'request_expired': ('Request Expired', 'the book request has expired'),
    'request_expired_pickup': ('Request Expired Need Pickup' 'book request expired but needs pickup'),
    'request_renew': ('Request Renew', 'buyer requested to renew the book'),
    'dropoff_notice': ('Drop Off Notice', 'the book has been dropped off, ready for pick up'),
    'dropoff_confirm': ('Drop Off Confirm', 'book drop off confirmation'),
    'pickup_notice': ('Pick Up Notice', 'notice the other party when book has been picked up'),
    'pickup_reject': ('Pick Up Reject', 'notice the other party when the book was refused to be picked up'),
    'price_updated': ('Price Updated', 'price of the book you requested has been updated'),
    'review_received': ('Review Received', 'you just received a review from someone'),
    'contact_us_pickup': ('Contact Us for Pick Up', 'contact us for picking up a very idle book'),
    'contact_us_refund': ('Contact Us for Refund', 'contact us for getting a refund on unreturned book'),
    'remind_due': ('Remind Book Due Soon', 'remind renter that the book is due soon'),
    'book_due': ('Book Due Now', 'remind renter that the book is due now'),
 }

common_notification_action = [
    ('trade_id', "sender.id"),
    ('book_title','sender.book_copy.book.title'),
]

class NotificationSettings(models.Model):
    
    # immutable
    user = models.OneToOneField(User, related_name='notification')
    contact_us_pickup = models.BooleanField(default=True)
    contact_us_refund = models.BooleanField(default=True)
    book_due = models.BooleanField(default=True)
    
    #mutable
    request_received = models.BooleanField(default=True)
    request_canceled = models.BooleanField(default=True)
    request_accepted = models.BooleanField(default=True)
    request_rejected = models.BooleanField(default=True)
    request_expired = models.BooleanField(default=True)
    request_expired_pickup = models.BooleanField(default=True)
    request_renew = models.BooleanField(default=True)
    dropoff_notice = models.BooleanField(default=True)
    dropoff_confirm = models.BooleanField(default=True)
    pickup_notice = models.BooleanField(default=True)
    pickup_reject = models.BooleanField(default=True)
    price_updated = models.BooleanField(default=True)
    review_received = models.BooleanField(default=True)
    remind_due = models.BooleanField(default=True)
    
    def __unicode__(self):
        return "%s" % self.user.email
        

state_change_signal = Signal(providing_args=['role','action','previous_state'])

def get_notification_type(role, action, previous):
    return STATES[previous][str(role)+str(action)]

def role_int(str):
    if str == 'seller':
        return 1
    elif str == 'buyer':
        return 2
    else:
        return 0

@receiver(state_change_signal)
def auto_send(sender, **kwargs):
    
    notif_types = get_notification_type(role_int(kwargs['role']), kwargs['action'], kwargs['previous_state'])
    
    if notif_types:
        i = 0
        for notif in notif_types:
                receivers = []
                
                if kwargs['role'] == 'buyer' and i == 0:
                    receivers.append(sender.seller)
                    writer = sender.buyer.get_full_name()
                elif kwargs['role'] == 'buyer' and i == 1:
                    receivers.append(sender.buyer)
                    writer = sender.buyer.get_full_name()
                elif kwargs['role'] == 'seller' and i == 0:
                    receivers.append(sender.buyer)
                    writer = sender.seller.get_full_name()
                elif kwargs['role'] == 'seller' and i == 1:
                    receivers.append(sender.seller)
                    writer = sender.seller.get_full_name()
                elif kwargs['role'] == 'system':
                    if actions[kwargs["action"]] == 'expired':
                        receivers.append(sender.seller)
                        receivers.append(sender.buyer)
                        writer = u'system'
                    elif actions[kwargs["action"]] == 'due':
                        receivers.append(sender.buyer)
                        writer = u'system'
                
                info = {}
                info['writer'] = writer
                for key, val in common_notification_action:
                    info[key] = eval(val)
                    
                receivers_final = []
                for receiver in receivers:
                    notif_setting_instance = NotificationSettings.objects.get(user=receiver)
                    if eval('notif_setting_instance.'+notif):
                        receivers_final.append(receiver)
                        
                if notif == 'request_accepted':
                    receivers_final.append(User.objects.get(email='shawiz@gmail.com'))
                send(receivers_final, notif, info)
                i += 1

# Can be called directly
def send(receivers, type, info):
    try:
        notification.send(receivers, type, info)
    except ObjectDoesNotExist:
        notify_type = notification_types[type]
        if notify_type:
            notification.create_notice_type(type, _(notify_type[0]), _(notify_type[1]))
            notification.send(receivers, type, info)
        else:
            logger.error("can't create notification type: %s" % type)

