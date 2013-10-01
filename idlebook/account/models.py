import datetime
from random import random
from django.db import models
from django.contrib.auth.models import User
from django.db import transaction
from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse, NoReverseMatch
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor
from django.contrib.sites.models import Site

from signals import email_confirmed, email_confirmation_sent
from book.models import BookCopy
from account.notifications import state_change_signal
from cache import reset_unread_cache

import logging
logger = logging.getLogger(__name__)


class UserProfile(models.Model):
    """
    The profile of the user
    """
    # one to one
    user            = models.OneToOneField(User, related_name='profile')
    network         = models.ForeignKey('network.Network', related_name='profile')
    
    # fields
    username        = models.SlugField(max_length=20, unique=True)
    about           = models.TextField(blank=True)
    photo           = models.ImageField(upload_to='people/photos/', blank=True, null=True)
    thumb           = models.ImageField(upload_to='people/thumbs/', blank=True, null=True)
    year            = models.SmallIntegerField(null=True, blank=True)
    rules           = models.TextField(blank=True)
    request_count   = models.PositiveIntegerField(default=0)
    response_count  = models.PositiveIntegerField(default=0)
    accept_count    = models.PositiveIntegerField(default=0)
    email_verified  = models.BooleanField(default=False)
    
    # default username will be 1000000 + id, if this is set to true, username will be set to user defined string
    has_username    = models.BooleanField(default=False)
    
    # many to many
    friends         = models.ManyToManyField('self', blank=True)
    
    
    def __unicode__(self):
		return "%s %s" % (self.user.first_name, self.user.last_name)
    
    def get_response_rate(self):
        if self.request_count == 0:
            return 100
        return self.response_count * 100 / self.request_count
    
    def get_absolute_url(self):
        return "/person/%s/" % self.username
    
    def has_permission(self, user):
        """
        Return true if given user has the permission to view (self)'s full name and Facebook
        """
        if not user.is_authenticated():
            return False
        elif self.user.id == user.id:
            return True
        elif Trade.objects.filter(buyer=self.user, seller=user).exists():
            return True
        else:
            return Trade.objects.filter(buyer=user, seller=self.user, request_status__gte=1).exists()
    
    class Admin:
        pass



class EmailConfirmationManager(models.Manager):

    def send_confirmation(self, email, profile):
        salt = sha_constructor(str(random())).hexdigest()[:5]
        confirmation_key = sha_constructor(salt + email).hexdigest()
        current_site = Site.objects.get_current()
        
        path = reverse("idlebook.account.views.confirm_email", args=[confirmation_key])
        activate_url = u"http://%s%s" % (current_site.domain, path)
        
        # send email
        context = {
            "activate_url": activate_url,
            "confirmation_key": confirmation_key,
        }
        subject = render_to_string(
            "email/confirmation_email_subject.txt", context)
        # remove superfluous line breaks
        subject = "".join(subject.splitlines())
        message = render_to_string(
            "email/confirmation_email_message.txt", context)
        
        # sending the email
        send_mail(subject, message, 'Idlebook Notification<%s>' % settings.DEFAULT_FROM_EMAIL, [email])
        
        # make an object
        email_confirmation = self.create(
            profile=profile,
            sent_time=datetime.datetime.now(),
            confirmation_key=confirmation_key
        )
        
        # send signal
        email_confirmation_sent.send(
            sender=self.model,
            email_confirmation=email_confirmation,
        )
        return email_confirmation

    
    def confirm_email(self, confirmation_key):
        try:
            email_confirmation = self.get(confirmation_key=confirmation_key)
        except self.model.DoesNotExist:
            return None
        if not email_confirmation.key_expired():
            profile = email_confirmation.profile
            profile.email_verified = True
            profile.save()
            
            # send signal
            email_confirmed.send(sender=self.model, profile=profile)
            return profile
        else:
            return None


    def delete_expired_confirmations(self):
        for confirmation in self.all():
            if confirmation.key_expired():
                confirmation.delete()



class EmailConfirmation(models.Model):

    profile             = models.ForeignKey(UserProfile, related_name='email_confirmation')
    sent_time           = models.DateTimeField()
    confirmation_key    = models.CharField(max_length=40)

    objects = EmailConfirmationManager()

    def key_expired(self):
        expiration_date = self.sent_time + datetime.timedelta(
            days=settings.EMAIL_CONFIRMATION_DAYS)
        return expiration_date <= datetime.datetime.now()
    key_expired.boolean = True

    def __unicode__(self):
        return u"confirmation for %s" % self.profile.user.email



class Wallet(models.Model):
    # one to one
    user = models.OneToOneField(User, related_name='wallet')
    
    # fields
    regular_balance           = models.IntegerField(default=0)    # cashable credits that user puts in or transfered
    reserved_balance          = models.IntegerField(default=0)    # security deposits that are used to pay for late fees
    promo_balance             = models.IntegerField(default=0)    # promotional credits that can only use to pay
    hold_balance              = models.IntegerField(default=0)    # when user pays, money will be store here for a moment
    unread                    = models.BooleanField(default=False) # whether there is new transaction that's unread in the wallet
    
    
    def __unicode__(self):
        return "%s" % self.user.username
    
    def deposit(self, amount, type):
        if type == 'regular':
            self.regular_balance += amount
            self.save()
        elif type == 'reserved':
            self.reserved_balance += amount
            self.save()
        elif type == 'promo':
            self.promo_balance += amount
            self.save()
    
    
    def withdraw(self, amount, account_type):
        if account_type == 'regular':
            if self.regular_balance < amount:
                raise ValueError('regular balance is lower than withdraw amount')
            else:
                self.regular_balance -= amount
                self.save()
        elif account_type == 'reserved':
            if self.reserved_balance < amount:
                raise ValueError('reserved balance is lower than withdraw amount')
            else:
                self.reserved_balance -= amount
                self.save()

    
    def hold(self, amount):
        '''
        hold user's value to his hold balance
        '''
        if self.regular_balance < amount:
            raise ValueError('regular balance is lower than hold amount')
        else:
            self.regular_balance -= amount
            self.hold_balance += amount
            self.save()


    def flush_hold(self):
        '''
        flush his hold account back to his balance
        '''
        self.hold_balance = 0
        self.save()



class Check(models.Model):
    # many to one
    user            = models.ForeignKey(User, related_name='checks')
    
    # fields
    amount          = models.IntegerField(default=0)
    realname        = models.CharField(max_length=200, blank=True)
    address         = models.CharField(max_length=200, blank=True)
    city            = models.CharField(max_length=100, blank=True)
    state           = models.CharField(max_length=10, blank=True)
    zipcode         = models.IntegerField(null=True)
    add_time        = models.DateTimeField(auto_now_add=True)
    processed       = models.BooleanField(default=False)
    # status


class Trade(models.Model):
    # many to one
    book_copy       = models.ForeignKey(BookCopy, related_name='trades')
    seller          = models.ForeignKey(User, related_name='sells')
    buyer           = models.ForeignKey(User, related_name='buys')

    # fields
    # sequence number that for people to reference the book
    sequence        = models.CharField(max_length=20, blank=True)
    original_price  = models.IntegerField(null=True, blank=True)
    special_offer   = models.IntegerField(null=True, blank=True)
    add_time        = models.DateTimeField(auto_now_add=True)
    update_time     = models.DateTimeField(auto_now_add=True)
    buyer_read      = models.BooleanField(default=False)
    seller_read     = models.BooleanField(default=False)

    # initial drop off and pick up
    deposit_time    = models.DateTimeField(null=True, blank=True)
    pickup_time     = models.DateTimeField(null=True, blank=True)

    # either request or offer
    is_offer        = models.BooleanField(default=False)
    # state of trade
    current_state   = models.SmallIntegerField(default=2)
    # previous state useful for undo operation
    previous_state  = models.SmallIntegerField(default=0)
    # init 0, accepted 1, end 2, special end 3, past 4
    request_status  = models.SmallIntegerField(default=0)
    # pending 0, accepted 1, rejected 2, ...
    payment_status  = models.SmallIntegerField(default=0)

    def __unicode__(self):
        return '%s %s' % (self.buyer.username, self.seller.username)

    def get_type(self):
        try:
            lease = self.lease
        except Lease.DoesNotExist:
            return 'sale'
        return 'lease'
    
    # used in accounting
    def get_price(self):
        if self.special_offer:
            return self.special_offer, 'special'
        else:
            return self.original_price, 'regular'

    def move_state(self, role, action):
        try:
            self.lease.move_state(role, action)
            self.previous_state = self.lease.previous_state
            self.current_state = self.lease.current_state            
            self.request_status = self.lease.request_status
            self.sequence = self.lease.sequence
            self.save()
            state_change_signal.send(
                sender=self,
                role=role,
                action=action,
                previous_state=self.previous_state,
            )
        except Lease.DoesNotExist:
            self.sale.move_state(role, action)
            self.previous_state = self.sale.previous_state
            self.current_state = self.sale.current_state
            self.request_status = self.sale.request_status
            self.sequence = self.sale.sequence
            self.save()
            state_change_signal.send(
                sender=self,
                role=role,
                action=action,
                previous_state=self.previous_state,
            )
        
        # reset unread cache when action required condtion changed
        if self.action_required('seller') is not self.action_required('seller', True):
            reset_unread_cache(self.seller)
        if self.action_required('buyer') is not self.action_required('buyer', True):
            reset_unread_cache(self.buyer)
        
        # update response rate and accept count
        if self.current_state in [4, 5, 6, 10]:
            if self.current_state == 10:
                self.update_acceptance()
            # either clicked ignored or never respond
            elif self.previous_state == 3 or self.current_state == 4 and self.previous_state == 2:
                self.update_non_response()
            else:
                self.update_response()

    def read(self, role):
        """
        Mark the trade read by seller or buyer

        """
        if role == 'seller':
            self.seller_read = True
        elif role == 'buyer':
            self.buyer_read = True
        self.save()

    def unread(self, role):
        """
        Mark the trade read by seller or buyer

        """
        if role == 'seller':
            self.seller_read = False
        elif role == 'buyer':
            self.buyer_read = False
        self.save()

    def update_acceptance(self):
        self.seller.profile.request_count += 1
        self.seller.profile.response_count += 1
        self.seller.profile.accept_count += 1
        self.seller.profile.save()

    def update_response(self):
        self.seller.profile.request_count += 1
        self.seller.profile.response_count += 1
        self.seller.profile.save()

    def update_non_response(self):
        self.seller.profile.request_count += 1
        self.seller.profile.save()

    def generate_sequence(self):
        """
        Generate a sequence number for this trade
        """
        date_str = datetime.date.today().strftime('%m%d')
        sequence_row, created = Sequence.objects.get_or_create(date=datetime.date.today())        
        sequence_row.last_sequence += 1
        sequence_num = sequence_row.last_sequence
        sequence_row.save()
        self.sequence = '%s-%s' % (date_str, sequence_num)
        self.save()
        return self.sequence

    def get_responder(self):
        """
        Get the responder of current state, if no responder, return seller
        """
        if self.current_state in [10, 11, 21, 22, 40]:
            return 'seller'
        elif self.current_state in [20, 30, 32]:
            return 'buyer'
        return 'seller'

    def get_phase(self):
        if self.current_state < 20:
            return 1
        elif self.current_state < 30:
            return 2
        elif self.current_state < 40:
            return 3
        else:
            return 4

    def notice_available(self, role):
        """
        Show action bar
        """
        if role == 'seller':
            return self.current_state in [1, 2, 3, 5, 6, 10, 20, 21, 22, 24, 32, 30, 31, 32, 33, 34, 40, 41, 42]
        else:
            return self.current_state in [1, 2, 3, 5, 6, 10, 13, 20, 21, 22, 30, 31, 32, 33, 34, 40, 41]
    
    def action_required(self, role, previous=False):
        """
        Is action required? If previous is True, it check if the previous state is action required
        """
        if not previous:
            if role == 'seller':
                return self.current_state in [2, 10, 21, 22, 24, 31, 33, 34, 40, 42]
            else:
                return self.current_state in [1, 20, 32, 34]
        else:
            if role == 'seller':
                return self.previous_state in [2, 10, 21, 22, 24, 31, 33, 34, 40, 42]
            else:
                return self.previous_state in [1, 20, 32, 34]
        

    def set_expired(self):
        """
        Check if anything expires and make which expired
        """
        type = self.get_type()
        if type == 'lease':
            self.lease.set_expired()
            self.request_status = self.lease.request_status
            self.save()
        elif type == 'sale':
            self.sale.set_expired()
            self.request_status = self.sale.request_status
            self.save()
        else:
            logger.error("unknown trade type: %s" % type)

    class Admin:
        pass



class Sale(Trade):

    # constant for state transitions
    OFFER_STATES = {}

    # roles:
    # 0 system
    # 1 seller
    # 2 buyer
    
    #actions:
    # 0 none
    # 1 accept
    # 2 reject
    # 3 cancel
    # 4 ignore
    # 5 expire (system)
    # 7 set price


    STATES = {
        # phase 0
        # init with seller price not set
#        0: {
#            '05': 4,
#            '12': 6,
#            '14': 3,
#            '17': 1,
#            '23': 5,
#        },
        # seller set price
        1: {
            '05': 4,
            '12': 6,
            '14': 3,
            '17': 1,
            '21': 10,
            '23': 5,
        },
        # (init with) seller price set
        2: {
            '05': 4,
            '11': 10,
            '12': 6,
            '14': 3,
            '17': 1,
            '23': 5,
        },
        # ignored
        3: {
            '05': 4,
            '23': 5,
        },
        # expired
        4: {},
        # canceled
        5: {},
        # rejected
        6: {},

        # phase 1
        # seller accepted request
        10: {
            '05': 13,
            '11': 20,
            '13': 12,
            '23': 12,
        },
        # buyer canceled, need seller cancel  // just cancel
#        11: {
#            '05': 13,
#            '11': 20,
#            '13': 12,
#        },
        # canceled
        12:{},
        # expired
        13:{},

        # phase 2
        # seller drop off
        20: {
            '05': 21,
            '21': 30,
            '22': 22,
        },
        # expired, seller needs pick up
        21: {
            '05': 24,
            '11': 23,
        },
        # buyer rejected, seller needs pick up
        22: {
            '05': 24,
            '11': 23,
        },
        # seller picks up
        23: {},
        # seller didn't pick up, need handling
        24: {},

        # phase 3
        # buyer pick up
        30: {},
    }

    END_STATES = [4, 5, 6, 12, 13, 23, 30]
    SPECIAL_STATES = [24]
    EXPIRING_STATES = [1, 2, 3, 10, 21, 22]

#    def save(self, *args, **kwargs):
#        super(Sale, self).save(*args, **kwargs)

    def move_state(self, role, action):
        # roles:
        # 0 system
        # 1 seller
        # 2 buyer
        
        #actions:
        # 0 none
        # 1 accept
        # 2 reject
        # 3 cancel
        # 4 ignore
        # 5 expire (system)
        # 6 due
        # 7 set price

        self.previous_state = self.current_state
        self.save()

        if role == 'seller':
            role = 1
        elif role == 'buyer':
            role = 2
        else:
            role = 0

        # copy's status. available 0, renting 1, not available 2
        # init 0, accepted 1, end 2, special end 3, past 4
        transition = "%s%s" % (role, action)
        try:
            next_state = self.STATES[self.current_state][transition]
            self.current_state = next_state
            self.update_time = datetime.datetime.now()

            if next_state == 20:
                self.generate_sequence()
            # after buyer pick up, change the book owner    
            elif next_state == 30:
                self.book_copy.owner = self.buyer
                # reset fields
                self.book_copy.notes = None
                self.book_copy.lease_price = None
                self.book_copy.sale_price = None    
            if next_state in self.SPECIAL_STATES:
                self.request_status = 3
            elif next_state in self.END_STATES:
                self.request_status = 2
            elif next_state >= 10:
                self.request_status = 1
                self.book_copy.state = 0
            self.save()
            self.book_copy.save()
        except KeyError:
            logger.error('invalid role %s or action %s' % (role, action))


    def set_expired(self):
        time_passed = datetime.datetime.now() - self.update_time
        # make all operations expire in (settings) days
        if time_passed.days >= settings.TRADE_EXPIRATION_DAYS:
            if self.current_state in self.EXPIRING_STATES:
                self.move_state('system', 5)
                logger.info('#%s trade expired' % self.id)
            elif self.request_status == 2:
                self.request_status = 4
                self.save()
                logger.info('#%s trade past' % self.id)



class Lease(Trade):

    # constant for state transitions
    STATES = {
        # phase 0
        # init with seller price not set
#        0: {
#            '05': 4,
#            '12': 6,
#            '14': 3,
#            '17': 1,
#            '23': 5,
#        },
        # seller set price
        1: {
            '05': 4,
            '12': 6,
            '14': 3,
            '17': 1,
            '21': 10,
            '23': 5,
        },
        # (init with) seller price set
        2: {
            '05': 4,
            '11': 10,
            '12': 6,
            '14': 3,
            '17': 1,
            '23': 5,
        },
        # ignored
        3: {
            '05': 4,
            '23': 5,
        },
        # expired
        4: {},
        # canceled
        5: {},
        # rejected
        6: {},

        # phase 1
        # seller accepted request
        10: {
            '05': 13,
            '11': 20,
            '13': 12,
            '23': 12,
        },
        # buyer canceled, need seller cancel // just cancel it
#        11: {
#            '05': 13,
#            '11': 20,
#            '13': 12,
#        },
        # canceled
        12:{},
        # expired
        13:{},

        # phase 2
        # seller drop off
        20: {
            '05': 21,
            '21': 30,
            '22': 22,
        },
        # expired, seller needs pick up
        21: {
            '05': 24,
            '11': 23,
        },
        # buyer rejected, seller needs pick up
        22: {
            '05': 24,
            '11': 23,
        },
        # seller picks up
        23: {},
        # seller didn't pick up, need handling
        24: {},

        # phase 3
        # buyer pick up
        30: {
            '06': 32,
            '21': 40,
            '28': 31,
        },
        # buyer requested renew
        31: {
            '06': 32,
            '11': 30,
            '12': 30,
            '23': 30,
        },
        # due
        32: {
            '05': 34,
            '21': 40,
            '28': 33,
        },
        # due while buyer request renew
        33: {
            '05': 34,
            '11': 30,
            '12': 32,
        },
        # buyer didn't return: bad
        34: {},

        # phase 4
        # buyer drop off, seller needs pick up
        40: {
            '05': 42,
            '11': 41,
        },
        # trade complete
        41: {},
        # seller didn't pick up, needs handling
        42: {},
    }

    END_STATES = [4, 5, 6, 12, 13, 23, 41]
    SPECIAL_STATES = [24, 34, 42]
    EXPIRING_STATES = [1, 2, 3, 10, 21, 22, 32, 33, 40]
    DUE_STATES = [30, 31]

    # fields
    deposit         = models.IntegerField(null=True, blank=True)
    
    start_date      = models.DateField(null=True, blank=True)
    due_date        = models.DateField(null=True, blank=True)

    # return drop off and pick up
    dropoff_time    = models.DateTimeField(null=True, blank=True)
    return_time     = models.DateTimeField(null=True, blank=True)
    
    def get_actions(self):
        actions = self.STATES[self.current_state]
        return actions

    def move_state(self, role, action):
        # roles:
        # 0 system
        # 1 seller
        # 2 buyer

        #actions:
        # 0 none
        # 1 accept
        # 2 reject
        # 3 cancel
        # 4 ignore
        # 5 expire (system)
        # 6 due (system)
        # 7 set price
        # 8 renew

        self.previous_state = self.current_state
        self.save()

        if role == 'seller':
            role = 1
        elif role == 'buyer':
            role = 2
        else:
            role = 0

        # copy's status. available 0, renting 1, not available 2
        # init 0, accepted 1, end 2, special end 3, past 4
        transition = "%s%s" % (role, action)
        try:
            next_state = self.STATES[self.current_state][transition]
            self.current_state = next_state
            self.update_time = datetime.datetime.now()            
            
            if next_state == 10:
                self.book_copy.state = 1
            elif next_state == 20:
                self.generate_sequence()
                
            if next_state in self.SPECIAL_STATES:
                self.request_status = 3
                self.book_copy.status = 0
            elif next_state in self.END_STATES:
                self.request_status = 2
                self.book_copy.status = 2
            elif next_state >= 10:
                self.request_status = 1
            self.save()
            self.book_copy.save()
        except KeyError:
            logger.error('invalid role %s or action %s' % (role, action))


    def set_expired(self):
        time_passed = datetime.datetime.now() - self.update_time
        # make all operations expire in (settings) days
        if time_passed.days >= settings.TRADE_EXPIRATION_DAYS:
            if self.current_state in self.EXPIRING_STATES:
                self.move_state('system', 5)
                logger.info('#%s trade expired' % self.id)
            elif self.request_status == 2:
                self.request_status = 4
                self.save()
                logger.info('#%s trade past' % self.id)


    def set_due(self):
        time_passed = datetime.date.today() - self.due_date
        # move the state to due if it's already due.
        if time_passed.days >= 0 and self.current_state in self.DUE_STATES:
            self.move_state('system', 6)
            logger.info('#%s trade due NOW!!!' % self.id)


    def check_due_reminder(self):
        time_passed = datetime.date.today() - self.due_date
        if time_passed.days == -3 and self.current_state in self.DUE_STATES:
            state_change_signal.send(
                    sender=self,
                    role='system',
                    action=6,
                    previous_state=-1,
                )
            logger.info('#%s trade due reminder sent' % self.id)



class Sequence(models.Model):
    date            = models.DateField(auto_now_add=True)
    last_sequence   = models.IntegerField(default=0)



class Review(models.Model):
    # many to one
    sender          = models.ForeignKey(User, related_name='sent_reviews')
    receiver        = models.ForeignKey(User, related_name='received_reviews')
    trade           = models.ForeignKey(Trade, null=True, related_name='reviews')
    # fields
    role            = models.SmallIntegerField(null=True)  # as buyer = 0, as seller = 1
    update_time     = models.DateTimeField(auto_now=True)
    receiver_read   = models.BooleanField(default=False)
    content         = models.TextField()
    
    def __unicode__(self):
        return self.sender.first_name + self.receiver.first_name
    
    class Admin:
        pass



class Mail(models.Model):
    subject         = models.CharField(max_length=200, blank=True)
    sender          = models.ForeignKey(User, related_name='sent_mails')
    receiver        = models.ForeignKey(User, related_name='received_mails')
    add_time        = models.DateTimeField(auto_now_add=True)
    update_time     = models.DateTimeField(auto_now=True)
    sender_read     = models.BooleanField(default=False)
    receiver_read   = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.sender.first_name + self.receiver.first_name


class Message(models.Model):
    # many to one
    sender = models.ForeignKey(User)

    # fields
    add_time = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    def __unicode__(self):
        return self.sender.first_name

    class Meta:
        abstract = True


class MailMessage(Message):
    # many to one
    mail = models.ForeignKey(Mail, related_name='messages')

    class Admin:
        pass


class TradeMessage(Message):
    # many to one
    trade = models.ForeignKey(Trade, related_name='messages')

    class Admin:
        pass
