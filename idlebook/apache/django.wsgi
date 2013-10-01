import os
import sys

sys.path.append(os.getenv('WSGI_PATH_ADD'))
sys.path.append(os.getenv('WSGI_PATH_ADD') + 'idlebook/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'idlebook.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
