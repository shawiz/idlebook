from amazonproduct import *
from django.conf import settings
from models import Book

import logging
logger = logging.getLogger(__name__)


def get_by_isbn(isbn):
    api = API(settings.AMAZON_AWS_KEY, settings.AMAZON_SECRET_KEY, settings.AMAZON_COUNTRY_CODE)
    try:
        node = api.item_lookup(isbn, IdType='ISBN', SearchIndex='Books', ResponseGroup='ItemAttributes, Images')   
        book = node.Items.Item[0]
        book_info = _get_info(book)
        return [book_info]
    except InvalidParameterValue:
        logger.debug('not found 1')
        return None
    except NoExactMatchesFound:
        logger.debug('not found 2')
        return None
    except NoSimilarityForASIN:
        logger.debug('not found 3')
        return None
        # AWS.ECommerceService.ItemNotAccessible
    except Exception, e:
        logger.debug('not found 4')        
        return None


def search_by_keywords(keywords, num_of_results=5):
    '''
    get a map of the infomation of the book isbn
    '''
    
    info_list = []
    api = API(settings.AMAZON_AWS_KEY, settings.AMAZON_SECRET_KEY, settings.AMAZON_COUNTRY_CODE)
    try:
        node = api.item_search('Books', Keywords=keywords, ResponseGroup='ItemAttributes, Images')
        count = 0
        for n in node:
            count += 1
            book = n.Items.Item[0]
            info = _get_info(book)
            if info:
                info_list.append(info)
            if count >= num_of_results:
                break
    except NoExactMatchesFound:
        pass
    
    return info_list


def get_alt_versions(book):
    versions = book.AlternateVersions
    versions_info = []
    for version in versions:
        try:
            version_info = {}
            version_info['asin'] = version.ASIN
            version_info['title'] = version.Title
            version_info['format'] = version.Binding
            logger.debug(version_info)
            versions_info.append(version_info)
        except AttributeError:
            pass
    return versions_info


def _get_info(book, fields=['isbn', 'title', 'edition', 'authors', 'publisher', 'publication_date', 'list_price', 'format', 'image']):
    attr = book.ItemAttributes
    info = {}
    
    if 'isbn' in fields:
        try:
            info['isbn'] = str(attr.EAN)
        except AttributeError:
            return None
    
    if 'title' in fields:
        try:
            info['title'] = attr.Title
        except AttributeError:
            info['title'] = None

    if 'edition' in fields:
        try:
            info['edition'] = attr.Edition
        except AttributeError:
            info['edition'] = None
    
    if 'authors' in fields:
        try:
            info['authors'] = ', '.join(map(unicode, attr.Author)) # attr.Author
        except AttributeError:
            try:
                info['authors'] = ', '.join(map(unicode, attr.Creator)) # attr.Creator
            except AttributeError:
                info['authors'] = None
    
    if 'publisher' in fields:
        try:
            info['publisher'] = attr.Publisher
        except AttributeError:
            info['publisher'] = None
    
    if 'publication_date' in fields:
        try:
            info['publication_date'] = attr.PublicationDate
        except AttributeError:
            info['publication_date'] = None

    if 'list_price' in fields:
        try:
            info['list_price'] = attr.ListPrice.Amount
        except AttributeError:
            info['list_price'] = None

    if 'format' in fields:
        try:
            info['format'] = attr.Binding
        except AttributeError:
            info['format'] = None

    if 'image' in fields:
        try:
            info['image'] = info['isbn'] + '.jpg'
            info['image_url'] = unicode(book.LargeImage.URL)
        except AttributeError:
            info['image'] = None
            info['image_url'] = None

    #utf-8 encoding
    for key, value in info.items():
        if value:
            if key in ['isbn', 'list_price']:
                info[key] = int(value)
            else:
                info[key] = unicode(value)

    return info

