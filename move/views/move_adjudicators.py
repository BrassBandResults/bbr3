# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved



from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from adjudicators.models import Adjudicator, AdjudicatorAlias, ContestAdjudicator
from bbr3.siteutils import browser_details
from bbr3.render import render_auth
from move.models import AdjudicatorMergeRequest
from move.tasks import notification


@login_required
def merge_request(request, pSourceAdjudicatorSlug):
    """
    Request move of all contests from one adjudicator to another
    """
    try:
        lSourceAdjudicator = Adjudicator.objects.filter(slug=pSourceAdjudicatorSlug)[0]
        lDestinationAdjudicator = Adjudicator.objects.filter(id=request.POST['moveToAdjudicator'])[0]
        
        lAdjudicatorMergeRequest = AdjudicatorMergeRequest()
        lAdjudicatorMergeRequest.source_adjudicator = lSourceAdjudicator
        lAdjudicatorMergeRequest.destination_adjudicator = lDestinationAdjudicator
        lAdjudicatorMergeRequest.lastChangedBy = request.user
        lAdjudicatorMergeRequest.owner = request.user
        lAdjudicatorMergeRequest.save()
        
        notification.delay(None, lAdjudicatorMergeRequest, 'adjudicator_merge', 'request', request.user, browser_details(request))
    except IndexError:
        # someone already merged one or either side
        pass
        
    return render_auth(request, 'move/merge_request_received.html')
    
    
@login_required
def list_merge_requests(request):
    """
    List all requests for adjudicator merges
    """
    if request.user.profile.superuser == False:
        raise Http404
    
    lMergeRequests = AdjudicatorMergeRequest.objects.filter()
    
    return render_auth(request, 'move/list_adjudicator_merge_requests.html', {'MergeRequests' : lMergeRequests})
    
    
@login_required
@csrf_exempt
def reject_merge(request, pMergeAdjudicatorRequestSerial):
    """
    Reject an adjudicator merge
    """
    if request.user.profile.superuser == False:
        raise Http404
    
    try:
        lMergeRequest = AdjudicatorMergeRequest.objects.filter(id=pMergeAdjudicatorRequestSerial)[0]
    except IndexError:
        raise Http404
    
    # send email back to original submitter
    lReason = request.POST['reason']
    
    if lReason:
        lSubmitterUser = lMergeRequest.owner
        lDestination = lSubmitterUser.email
    else:
        lDestination = 'tsawyer@brassbandresults.co.uk'

    lContext = {'Reason' : lReason, }
    notification.delay(None, lMergeRequest, 'adjudicator', 'reject', request.user, browser_details(request), pDestination=lDestination, pAdditionalContext=lContext)
    
    # delete merge request
    lMergeRequest.delete()
    
    return render_auth(request, 'blank.htm')


@login_required
def merge_action(request, pMergeAdjudicatorRequestSerial):
    """
    Perform a merge of adjudicators
    """    
    if request.user.profile.superuser == False:
        raise Http404
    
    try:
        lMergeRequest = AdjudicatorMergeRequest.objects.filter(id=pMergeAdjudicatorRequestSerial)[0]
    except IndexError:
        raise Http404
    
    lFromAdjudicator = lMergeRequest.source_adjudicator
    lToAdjudicator = lMergeRequest.destination_adjudicator
    
    lContestsToMove = ContestAdjudicator.objects.filter(adjudicator=lFromAdjudicator)
    for result in lContestsToMove:
        if not result.adjudicator_name:
            result.adjudicator_name = result.adjudicator.name
        result.adjudicator = lToAdjudicator
        result.lastChangedBy = request.user
        result.save()
        
    # does it exist already on destination adjudicator?
    try:
        lExistingAlias = AdjudicatorAlias.objects.filter(adjudicator=lToAdjudicator, name=lFromAdjudicator.name)[0]
    except IndexError:
        lNewPreviousName = AdjudicatorAlias()
        lNewPreviousName.adjudicator = lToAdjudicator
        lNewPreviousName.name = lFromAdjudicator.name
        lNewPreviousName.owner = request.user
        lNewPreviousName.lastChangedBy = request.user
        lNewPreviousName.save()
    
    for previous_name in AdjudicatorAlias.objects.filter(adjudicator=lFromAdjudicator):
        # does it exist already on destination adjudicator?
        try:
            lExistingAlias = AdjudicatorAlias.objects.filter(adjudicator=lToAdjudicator, name=previous_name.name)[0]
        except IndexError:
            lNewPreviousName = AdjudicatorAlias()
            lNewPreviousName.adjudicator = lToAdjudicator
            lNewPreviousName.name = previous_name.name
            lNewPreviousName.owner = previous_name.owner
            lNewPreviousName.lastChangedBy = request.user
            lNewPreviousName.save()    
        
    notification.delay(None, lMergeRequest, 'adjudicator_merge', 'done', request.user, browser_details(request))
    lSubmitterUser = lMergeRequest.owner
    notification.delay(None, lMergeRequest, 'adjudicator', 'merge', request.user, browser_details(request), pDestination=lSubmitterUser.email)
    
    lFromAdjudicator.delete()
    lMergeRequest.delete()
        
    return HttpResponseRedirect('/move/adjudicators/')