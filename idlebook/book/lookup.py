import re
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.utils import simplejson as json
from django.utils.encoding import smart_unicode
from django.db.models import Q

from models import Book
from idlebook.network.models import Department
import depts

class LookupBase(object):

    def get_query(self, request, term):
        return []

    def get_item_label(self, item):
        return smart_unicode(item)

    def get_item_data(self, item):
        return {
            'id': item.id
        }

    def get_item(self, value):
        return value

    def format_item(self, item):
        return {
            'value': self.get_item_label(item),
            'data': self.get_item_data(item)
        }

    def results(self, request):
        query = request.GET.get('q', '')
        raw_data = self.get_query(request, query)
        data = []
        for item in raw_data:
            data.append(self.format_item(item))
        content = json.dumps(data, cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(content, content_type='application/json')



class BookLookup(LookupBase):
    
    def get_query(self, request, term):
#     the backend way of search just filter course name. still not order by, though.
#        find = re.match(r'^[a-zA-Z&]{2,6}', term)
#        if find:
#            code = find.string.upper()
#            if code in depts.get_code_list():
#                return Book.objects.filter(courses__name__icontains=code).distinct()
        return Book.objects.filter(Q(title__icontains=term) | Q(courses__keywords__icontains=term)).order_by('title').distinct()

    def get_item_label(self, book):
        courses = ['<span class="x-8q %s">%s</span>' % (course.keywords, course.name) for course in book.courses.all()]
        course_names = ' '.join(courses)
        # truncate text
#        title = smart_truncate(book.title, 120)
        title = book.title
        if courses:
            return '%s %s' % (title, course_names)
        return '%s' % (title)
    
    def get_item_data(self, book):
        return {
            'id': book.id,
            'price': book.list_price,
        #    'owned': book.owned,
        #    'wished': book.wished,
        }


class DepartmentLookup(LookupBase):

    def get_query(self, request, term):
        return Department.objects.filter(Q(name__icontains=term) | Q(code__icontains=term)).distinct()

    def get_item_label(self, department):
        return '%s <span class="x-8q">%s</span>' % (department.name, department.code)

