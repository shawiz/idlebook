import re
import depts 
from models import Book, BookPrices
from django.conf import settings


def _is_isbn(isbn):
    isbn = isbn.strip()
    return re.match(r'^(978|979)?-?[0-9xX]{10}$', isbn) is not None

def _is_course_name(term):
    term = term.strip().lower()
    for i in depts.get_code_list():
        if term.startswith(i.lower()):
            rest = term[len(i):len(term)].strip()
            if len(rest) == 0 or rest[0].isdigit():
                return True
            else:
                return False
    return False

def _to_int(decimal):
    """
    convert a decimal string to int
    """
    # prevent people from doing evil things with '-'
    while decimal.startswith('-'):
        decimal = decimal[1:]
    return int(float(decimal) * 100)


def duration(start_date, end_date):
    """
    utility function. roughly compute a duration in terms of months and days

    """
    days = (end_date - start_date).days + 1
    months = days / 30
    remainder = max(days%30-(months+1)/2, 0)    # a rough calculation of days
    month_str = "month" if months == 1 else "months"
    day_str = "day" if remainder == 1 else "days"    

    if months == 0:
        return "%s %s" % (days, day_str)  
    elif remainder == 0:
        return "%s %s" % (months, month_str)
    else:
        return "%s %s and %s %s" % (months, month_str, remainder, day_str)


def get_buyer_price(seller_price, type):
    """
    compute the price for the buyer
    """
    return seller_price + get_commission(seller_price, type)


def get_price_range(list_price, type):
    """
    find a suggested price range for user
    """
    if type == 'sale':
        return list_price * 0.6, list_price * 0.7
    else:
        return list_price * 0.2, list_price * 0.3


def get_commission(seller_price, type):
    """
    mystery function
    """
    commission = seller_price*.1
    if type == 'sale' and commission > 500:
        return 500
    else:
        return commission


def smart_truncate(content, length=100, suffix='...'):
    if len(content) <= length:
        return content
    else:
        return content[:length].rsplit(' ', 1)[0] + suffix
        

def smart_truncate_lists(content, length=100, suffix=''):
    if len(content) <= length:
        return content
    else:
        return content[:length].rsplit(', ', 1)[0] + suffix
