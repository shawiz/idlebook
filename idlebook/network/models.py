from django.db import models
from django.contrib.auth.models import User

class Network(models.Model):
    # fields
    name = models.CharField(max_length=100)
    email_patterns = models.CharField(max_length=100, blank=True)
    name_slug = models.SlugField(max_length=60)
    
    def __unicode__(self):
        return self.name

    class Admin:
        pass


class Department(models.Model):
    # many to one
    network = models.ForeignKey(Network, related_name='departments')
    
    # fields
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10, unique=True)
    
    # many to many
    students = models.ManyToManyField(User, blank=True, null=True, related_name='departments')
    
    def __unicode__(self):
        return self.name
    
    class Admin:
        pass


class Course(models.Model):
    # many to one
    department  = models.ForeignKey(Department, related_name='courses')
    
    # fields
    name        = models.CharField(max_length=20, unique=True) #example CSE457
    number      = models.IntegerField(max_length=10) #example 457
    keywords    = models.CharField(max_length=40) #example CSE457 CSE 457
#    section = models.CharField(max_length=5, blank=True)
#    quarter = models.CharField(max_length=20, blank=True)
#    year = models.PositiveIntegerField(null=True, blank=True)
    
    books = models.ManyToManyField('book.Book', null=True, blank=True, related_name='courses')
    
    def __unicode__(self):
        return self.name

    class Admin:
        pass
