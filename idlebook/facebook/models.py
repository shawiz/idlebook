from django.db import models
from django.contrib.auth.models import User

class FacebookUser(models.Model):
	user            = models.ForeignKey(User, unique=True)
	facebook_id     = models.CharField(max_length=150, unique=True)
	access_token    = models.CharField(max_length=150, blank=True, null=True)
	inviter_id      = models.CharField(max_length=150, blank=True, null=True)
	inviter_name    = models.CharField(max_length=40, blank=True, null=True)
	
	def __unicode__(self):
	    return self.user.email