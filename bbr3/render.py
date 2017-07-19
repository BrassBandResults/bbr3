from django.shortcuts import render_to_response
from django.template import RequestContext

def render_auth(request, pTemplate, pParams=None):
    return render_to_response(pTemplate, 
                              pParams)