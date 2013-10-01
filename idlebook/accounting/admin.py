from django.contrib import admin
from django.db import models

from models import *

admin.site.register(Transaction)
admin.site.register(IdlebookAccount)