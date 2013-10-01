from django.core.management.base import BaseCommand, CommandError
from network.models import Course


class Command(BaseCommand):
    args = '<None>'
    help = 'Add book keywords for searching'

    def handle(self, *args, **options):
        courses = Course.objects.all()
        counter = 0
        for course in courses:
            counter += 1
            course.keywords = "%s %s %s" % (course.name, course.department.code, course.number)
            course.save()
            print "#%s %s %s" % (counter, course.id, course.keywords)