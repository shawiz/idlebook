from django.conf import settings
from django.contrib import auth
import facebook
from idlebook.account.forms import FacebookSignupForm


class DjangoFacebook(object):
    """ Simple accessor object for the Facebook user. """
    def __init__(self, user):
        self.user = user
        self.uid = user['uid']
        self.graph = facebook.GraphAPI(user['access_token'])


class FacebookDebugCookieMiddleware(object):
    """ Sets an imaginary cookie to make it easy to work from a development environment.

    This should be a raw string as is sent from a browser to the server, obtained by
    LiveHeaders, Firebug or similar. The middleware takes care of naming the cookie
    correctly. This should initialised before FacebookMiddleware.
    """
    def process_request(self, request):
        cookie_name = "fbs_" + settings.FACEBOOK_APP_ID
        request.COOKIES[cookie_name] = settings.FACEBOOK_DEBUG_COOKIE
        return None


class FacebookDebugTokenMiddleware(object):
    """ Forces a specific access token to be used.

    This should be used instead of FacebookMiddleware. Make sure you have
    FACEBOOK_DEBUG_UID and FACEBOOK_DEBUG_TOKEN set in your configuration.
    """
    def process_request(self, request):
        user = {
            'uid':settings.FACEBOOK_DEBUG_UID,
            'access_token':settings.FACEBOOK_DEBUG_TOKEN,
        }
        request.facebook = DjangoFacebook(user)
        return None


class FacebookMiddleware(object):
    """ Transparently integrate Django accounts with Facebook.

    If the user presents with a valid facebook cookie, then we want them to be
    automatically logged in as that user. We rely on the authentication backend
    to create the user if it does not exist.

    We do not want to persist the facebook login, so we avoid calling auth.login()
    with the rationale that if they log out via fb:login-button we want them to
    be logged out of Django also.

    We also want to allow people to log in with other backends, which means we
    need to be careful before replacing request.user.
    """

    def get_fb_user_cookie(self, request):
        """ Attempt to find a facebook user using a cookie. """
        fb_user = facebook.get_user_from_cookie(request.COOKIES,
            settings.FACEBOOK_APP_ID, settings.FACEBOOK_SECRET_KEY)
        if fb_user:
            fb_user['method'] = 'cookie'
        return fb_user

    def process_request(self, request):
        """ Add `facebook` into the request context and attempt to authenticate the user.

        If no user was found, request.facebook will be None. Otherwise it will contain
        a DjangoFacebook object containing:
          uid: The facebook users UID
          user: Any user information made available as part of the authentication process
          graph: A GraphAPI object connected to the current user.

        An attempt to authenticate the user is also made. The fb_uid and fb_graphtoken
        parameters are passed and are available for any AuthenticationBackends.

        The user however is not "logged in" via login() as facebook sessions are ephemeral
        and must be revalidated on every request.
        """
        fb_user = self.get_fb_user_cookie(request)
        request.facebook = DjangoFacebook(fb_user) if fb_user else None
        
        return None
