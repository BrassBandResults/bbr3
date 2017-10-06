# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.shortcuts import render_to_response
from django.template import RequestContext

def render_auth(request, pTemplate, pParams=None):
    return render_to_response(pTemplate, 
                              pParams)