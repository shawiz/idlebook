from django.contrib import admin
from django.db import models

from models import *

admin.site.register(Network)
admin.site.register(Department)
admin.site.register(Course)