from django.contrib import admin
from django.db import models
from notifications import NotificationSettings

from models import *

admin.site.register(UserProfile)
admin.site.register(EmailConfirmation)
admin.site.register(Wallet)
admin.site.register(Check)
admin.site.register(Trade)
admin.site.register(Sale)
admin.site.register(Lease)
admin.site.register(Sequence)
admin.site.register(Review)
admin.site.register(Mail)
admin.site.register(MailMessage)
admin.site.register(TradeMessage)
admin.site.register(NotificationSettings)