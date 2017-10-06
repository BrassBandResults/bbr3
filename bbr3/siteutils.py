# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from html.entities import name2codepoint
import http.client
import re
import unicodedata
from django.conf import settings


def slugify(s, entities=True, decimal=True, hexadecimal=True, instance=None, slug_field='slug', filter_dict=None):
    s = smart_unicode(s)

    #character entity reference
    if entities:
        s = re.sub('&(%s);' % '|'.join(name2codepoint), lambda m: unichr(name2codepoint[m.group(1)]), s)

    #decimal character reference
    if decimal:
        try:
            s = re.sub('&#(\d+);', lambda m: unichr(int(m.group(1))), s)
        except:
            pass

    #hexadecimal character reference
    if hexadecimal:
        try:
            s = re.sub('&#x([\da-fA-F]+);', lambda m: unichr(int(m.group(1), 16)), s)
        except:
            pass

    #translate
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')

    #replace unwanted characters
    s = re.sub(r'[^-a-z0-9]+', '-', s.lower())

    #remove redundant -
    s = re.sub('-{2,}', '-', s).strip('-')

    slug = s
    if instance:
        def get_query():
            query = instance.__class__.objects.filter(**{slug_field: slug})
            if filter_dict:
                query = query.filter(**filter_dict)
            if instance.pk:
                query = query.exclude(pk=instance.pk)
            return query
        counter = 1
        while get_query():
            slug = "%s-%s" % (s, counter)
            counter += 1
    if len(slug) > 50:
        slug = slug[:50]
    return slug
    

def add_space_after_dot(pName):
    """
    If there is a full stop not followed by a space, add one in
    """
    lReturn = ""
    lFoundDot = False
    for char in pName:
        if lFoundDot and char != ' ':
            lReturn += " "
            lFoundDot = False
        if char == '.':
            lFoundDot = True
        lReturn += char
    return lReturn


def add_dot_after_initial(pName):
    """
    If there is an initial, but no dot, add the dot
    """
    lReturn = pName
    lPosition = 0
    if pName.strip().find(' ') == 1:
        lReturn = ''
        for char in pName:
            if char == ' ' and lPosition < 7 :
                lReturn += '. '
            else:
                lReturn += char
            lPosition += 1 
            
    return lReturn


def browser_details(request):
    """
    Find ip and browser string from request
    """
    try:
        lIpAddress = request.META['HTTP_X_REAL_IP']
        lUserAgent = request.META['HTTP_USER_AGENT']
    except KeyError:
        lIpAddress = ''
        lUserAgent = ''
    return (lIpAddress, lUserAgent)


def shorten_url(pUrl):
    """
    Shorten url using bit.ly api
    """
    lRequest = "/v3/shorten?format=txt&longUrl="
    lRequest += pUrl
    lRequest += "&login=" + settings.BIT_LY_LOGIN + "&apiKey=" + settings.BIT_LY_API_KEY
    lConnection = http.client.HTTPConnection("api.bit.ly")
    lConnection.request("GET", lRequest)
    lResponseObject = lConnection.getresponse()
    lStatusCode = lResponseObject.status
    lShortUrl = lResponseObject.read()
        
    if lStatusCode == 200:
        return lShortUrl
    else:
        return pUrl