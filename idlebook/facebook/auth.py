from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
import facebook
from models import *

class FacebookBackend(ModelBackend):
    """ Authenticate a facebook user. """
    def authenticate(self, fb_uid=None, fb_graphtoken=None):
        """ If we receive a facebook uid then the cookie has already been validated. """
        if fb_uid and fb_graphtoken:
            try:
                fb_user = FacebookUser.objects.get(facebook_id=fb_uid)
                user = fb_user.user
                if fb_user.access_token != fb_graphtoken:
                    fb_user.access_token = fb_graphtoken
                    fb_user.save()
                return user
            except FacebookUser.DoesNotExist:
                return None
        return None
