# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved



import re

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from bbr3.siteutils import browser_details
from bbr3.render import render_auth
from conductors.models import Conductor, ConductorAlias
from contests.models import ContestResult
from move.models import ConductorMergeRequest
from move.tasks import notification


@login_required
def merge_request(request, pSourceConductorSlug):
    """
    Request move of all results from one conductor to another
    """
    try:
        lSourceConductor = Conductor.objects.filter(slug=pSourceConductorSlug)[0]
        lDestinationConductor = Conductor.objects.filter(id=request.POST['moveToConductor'])[0]
        
        lConductorMergeRequest = ConductorMergeRequest()
        lConductorMergeRequest.source_conductor = lSourceConductor
        lConductorMergeRequest.destination_conductor = lDestinationConductor
        lConductorMergeRequest.lastChangedBy = request.user
        lConductorMergeRequest.owner = request.user
        lConductorMergeRequest.save()
        
        notification.delay(None, lConductorMergeRequest, 'conductor_merge', 'request', request.user, browser_details(request))
    except IndexError:
        # someone already merged one or either side
        pass
    
    return render_auth(request, 'move/merge_request_received.html')
    
    
@login_required
def list_merge_requests(request):
    """
    List all requests for conductor merges
    """
    if request.user.profile.superuser == False:
        raise Http404
    
    lMergeRequests = ConductorMergeRequest.objects.filter()
    
    return render_auth(request, 'move/list_conductor_merge_requests.html', {'MergeRequests' : lMergeRequests})
    
    
@login_required
@csrf_exempt
def reject_merge(request, pMergeConductorRequestSerial):
    """
    Reject a conductor merge
    """
    if request.user.profile.superuser == False:
        raise Http404
    
    try:
        lConductorMergeRequest = ConductorMergeRequest.objects.filter(id=pMergeConductorRequestSerial)[0]
    except IndexError:
        raise Http404
    
    # send email back to original submitter
    lReason = request.POST['reason']
    
    if lReason:
        lSubmitterUser = lConductorMergeRequest.owner
        lDestination = lSubmitterUser.email
    else:
        lDestination = 'tsawyer@brassbandresults.co.uk'
    
    lContext = {'Reason' : lReason, }
    notification.delay(None, lConductorMergeRequest, 'conductor', 'reject', request.user, browser_details(request), pDestination=lDestination, pAdditionalContext=lContext)
        
    # delete merge request
    lConductorMergeRequest.delete()
    
    return render_auth(request, 'blank.htm')


@login_required
def merge_action(request, pMergeConductorRequestSerial):
    """
    Perform a merge of conductors
    """    
    if request.user.profile.superuser == False:
        raise Http404
    
    try:
        lMergeRequest = ConductorMergeRequest.objects.filter(id=pMergeConductorRequestSerial)[0]
    except IndexError:
        raise Http404
    
    lFromConductor = lMergeRequest.source_conductor
    lToConductor = lMergeRequest.destination_conductor
    
    lResultsToMove = ContestResult.objects.filter(conductor=lFromConductor)
    for result in lResultsToMove:
        result.conductor = lToConductor
        if not result.conductor_name:
            result.conductor_name = lFromConductor.name
        result.lastChangedBy = request.user
        result.save()
        
    lInitialRegex = "^\w\.\s\w+$"
    if lFromConductor.name.strip() != lToConductor.name.strip():
        # if it's just initial surname, don't move
        
        lMatches = re.match(lInitialRegex, lFromConductor.name)
        if lMatches == None:
            # does it exist already on destination conductor?
            try:
                lExistingAlias = ConductorAlias.objects.filter(conductor=lToConductor, name=lFromConductor.name)[0]
            except IndexError:
                lNewPreviousName = ConductorAlias()
                lNewPreviousName.conductor = lToConductor
                lNewPreviousName.name = lFromConductor.name
                lNewPreviousName.save()
    
    for previous_name in ConductorAlias.objects.filter(conductor=lFromConductor):
        # if it's just initial surname, don't move
        lMatches = re.match(lInitialRegex, previous_name.name)
        if lMatches == None:
            # does it exist already on destination conductor?
            try:
                lExistingAlias = ConductorAlias.objects.filter(conductor=lToConductor, name=previous_name.name)[0]
            except IndexError:
                lNewPreviousName = ConductorAlias()
                lNewPreviousName.conductor = lToConductor
                lNewPreviousName.name = previous_name.name
                lNewPreviousName.save()    
                
    notification.delay(None, lMergeRequest, 'conductor_merge', 'done', request.user, browser_details(request))
    lSubmitterUser = lMergeRequest.owner
    notification.delay(None, lMergeRequest, 'conductor', 'merge', request.user, browser_details(request), pDestination=lSubmitterUser.email)
    
    lFromConductor.delete()
    lMergeRequest.delete()
        
    return HttpResponseRedirect('/move/conductors/')