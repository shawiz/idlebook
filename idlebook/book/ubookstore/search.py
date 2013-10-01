import browser
import re

'''
Created on Aug 6, 2011

@author: youngkent

=========README========
Usage: fetchBooks(*)

        parameters: quarter  (required: Spring, Summer, Autumn or Winter);
                    course; sln; author; title; isbn  (All optional)
                    max_course (Optional. Default is 3. Set for searching with course, author or title)
        return: list of dictionary of books with keys:
                department, courseNumber, section, isbn, title, newPrice, usedPrice
        
Note:   * search priority is isbn, sln, course, title, author
        * make sure quarter is set to one of the four values
'''

IMG_FOLDER = '/home/hajime/workspace/idlebook/idlebook/book/ubookstore/images/'
TMP_FOLDER = 'tmp/'

IMG = 'http://www7.bookstore.washington.edu/images/isbnimage/ummum9mro/subseta/'    #+'ahfriasdf.gif'
FIND = 'http://www.bookstore.washington.edu/student_faculty/student_faculty.taf?page=uwseattle'
DISPLAY = 'http://www3.bookstore.washington.edu'

R_NOMATCH = r'There were no matching results'
R_SLN = r'<td>.*?(\d{5}).*?(\d+)/ +(\d+).*?</td>'                       #require re.S
R_ITEM = r'(Course #:.*?Notes:)'                                        #require re.S
R_COURSE = r'colspan="2">\s+(.*?)\s+&nbsp;'                             #require re.S
R_SECTION = r'Sections:</b>&nbsp;&nbsp;&nbsp;&nbsp;(.*?)\s*<'           #require re.S
R_BOOK = r'Title.*?colspan="2">(.*?)</td>'                              #require re.S
R_NEW = r'New Price:.*?\$\s([0-9.]+).*Used Price:'                      #require re.S
R_USED = r'Used Price:.*?\$\s([0-9.]+).*Notes'                          #require re.S
R_IMG = r'http:.*?/([^/]*?)\.gif'

R_SPAN = r'<span class="orangesmallbodytext">&#42;Digital Format</span>:  '
R_NOTEXT = r'\n.*?Required'
R_LINK = r'(/_text/TextDisplay.*?)"'

bs = browser.Browser()
numTable = None


def tellNum(imgPath):
    '''num recognition'''
    global numTable
    if not numTable:
        numTable = []
        for i in range(10):
            img = open(IMG_FOLDER+str(i)+'.gif').read()
            numTable.append(img)
    img = bs.open(imgPath)
    open(TMP_FOLDER+'temp.gif', 'w').write(img) #important step
    img = open(TMP_FOLDER+'temp.gif', 'r').read()
    if img in numTable:
        return numTable.index(img)
    else:
        return '?'
    

def parsePage(html):
    '''retrieve info from info page'''
    #resolve infomation
    books = []
    imgDict = {}
    items = re.findall(R_ITEM, html, re.S)
    if len(items) == 0:
        raise Exception('Internal Error: Cannot detect courses')
    for item in items:
        course = re.findall(R_COURSE, item, re.S)[0]
        dep = course[:-3]
        num = course[-3:]
        section = re.findall(R_SECTION, item,re.S)[0]
        book = re.findall(R_BOOK, item, re.S)[0]
        new = re.findall(R_NEW, item, re.S)
        used = re.findall(R_USED, item, re.S)
        if len(new) > 0:
            new = new[0]
        else:
            new = None
        if len(used) > 0:
            used = used[0]
        else:
            used = None
        
        #resolve isbn
        imgs = re.findall(R_IMG, item)
        isbn = ''
        for img in imgs:
            if imgDict.has_key(img):
         #   if img in imgDict.keys():
                isbn += imgDict[img]
            else:
                n = tellNum(IMG+img+'.gif')
                isbn += str(n)
                imgDict[img] = str(n)
        
        #push result
        bookInfo = {
            'department': dep,
            'course_number': num,
            'section': section,
            'isbn': isbn,
            'title': book,
            'new_price': new,
            'used_price': used
        }        
        books.append(bookInfo)
    return books


def search(quarter='', course='', sln='', author='', title='', isbn=''):
    '''set form before submitted to uw book store'''
    html = bs.open(FIND)
    form = bs.getForm(html)
    if quarter == '':
        raise Exception('Error: quarter is not set')

    form['txtQuarter'] = [quarter]
    form['DEPTCOURSE'] = course
    form['multisln'] = sln
    form['author'] = author
    form['title'] = title
    form['isbn'] = isbn

    req = form.click(type='submit')
    return bs.open(req)


def fetchBooks(quarter='', course='', sln='', author='', title='', isbn='', max_course=3):
    #set up
    books = []

    #open page
    html = search(quarter, course, sln, author, title, isbn)

    #check availability
    if re.search(R_NOMATCH, html):
        return books
    
    if sln == '' and isbn == '':
        #resolve links
        links = re.findall(R_LINK, html, re.S)[:max_course]
        for link in links:
            html = bs.open(DISPLAY+link)
            books += parsePage(html)
    else:
        books = parsePage(html)

    return books

def removeBookDuplicates(list):
    i = 0
    return_list = []
    for x in list:
        delete = False
        for y in list[i+1:]:
            if x['isbn']==y['isbn']:
                delete = True
                break
        if not delete:
            return_list.append(x)
        i += 1
            
    return return_list

if __name__ == '__main__':
    #example
    print fetchBooks(quarter='Autumn', sln='10123')
    print fetchBooks(quarter='Autumn', course='cse4', max_course=10)
