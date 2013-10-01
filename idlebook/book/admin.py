from django.contrib import admin
from django.db import models

from models import *

admin.site.register(Book)
admin.site.register(BookPrices)
admin.site.register(BookCopy)
admin.site.register(Wishlist)
