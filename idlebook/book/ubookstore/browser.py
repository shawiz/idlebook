import urllib2, cookielib, ClientForm
import re
import time
from cStringIO import StringIO



class Browser() :
    def __init__(self):
        self.html=''
        self.silent=False
        self.view='view.html'
        #private
        self._currentUrl=''
        self._redir=r'<body onload="document\..*\.submit\(\)">'
        self._refresh=r'http-equiv="refresh"'
        self._nexturl=r'content=".*?URL=(.*?)"'
        #init
        self.newBrowser()

    def newBrowser(self):
        '''make up a browser'''
        #make the browser
        cookiejar = cookielib.CookieJar()
        cookiejar = urllib2.HTTPCookieProcessor(cookiejar)
        self.browser= urllib2.build_opener(cookiejar)
        self.browser.addheaders=[('Accept','application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5'),\
                                ('Content-Type','application/x-www-form-urlencoded'),\
                                ('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.517.44 Safari/534.7')]
                     
    def open(self,request):
        '''general page openner'''
        #open page
        resp=self.browser.open(request)
        html=resp.read()
        if re.search(self._redir,html,re.I)!=None:
            if not self.silent: print 'Redirecting...'
            form=self.getForm(html)
            fc=form.click(type='submit')
            return self.open(fc)
        elif re.search(self._refresh,html,re.I)!=None:
            if not self.silent: print 'Redirecting...'
            try:
                newurl=re.findall(self._nexturl,html,re.I)[0]
            except:
                raise Exception('redirection url not found')
            if re.search(r'http:',newurl,re.I)!=None:
                return self.open(newurl)
            else:
                newurl=re.sub(r'/[^/]*$','/'+newurl,resp.geturl())
                return self.open(newurl)
        #no redirect
        self.html,self._currentUrl=html,resp.geturl()
        return html
        
    def write(self):
        '''write view html file'''
        file=open(self.view,'w')
        file.write(self.html)    
        file.close()
    
    
    def getForm(self,html,index=0):
        '''parse the form in html. The fist form by default'''
        fp=StringIO()
        fp.write(html)
        fp.seek(0)
        form=ClientForm.ParseResponse(fp,self._currentUrl,backwards_compat=False)[index]
        return form