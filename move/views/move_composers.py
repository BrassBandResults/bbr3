# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved



from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from bbr3.siteutils import browser_details
from bbr3.render import render_auth
from move.models import ComposerMergeRequest
from move.tasks import notification
from pieces.models import Composer, TestPiece


@login_required
def merge_request(request, pSourceComposerSlug):
    """
    Request move of all pieces from one composer to another
    """
    try:
        lSourceComposer = Composer.objects.filter(slug=pSourceComposerSlug)[0]
        lDestinationComposer = Composer.objects.filter(id=request.POST['moveToComposer'])[0]
        
        lComposerMergeRequest = ComposerMergeRequest()
        lComposerMergeRequest.source_composer = lSourceComposer
        lComposerMergeRequest.destination_composer = lDestinationComposer
        lComposerMergeRequest.lastChangedBy = request.user
        lComposerMergeRequest.owner = request.user
        lComposerMergeRequest.save()
        
        notification.delay(None, lComposerMergeRequest, 'composer_merge', 'request', request.user, browser_details(request))
    except IndexError:
        # someone already merged one or either side
        pass        
    
    return render_auth(request, 'move/merge_request_received.html')
    
    
@login_required
def list_merge_requests(request):
    """
    List all requests for composer merges
    """
    if request.user.profile.superuser == False:
        raise Http404
    
    lMergeRequests = ComposerMergeRequest.objects.filter()
    
    return render_auth(request, 'move/list_composer_merge_requests.html', {'MergeRequests' : lMergeRequests})
    
    
@login_required
@csrf_exempt
def reject_merge(request, pMergeComposerRequestSerial):
    """
    Reject a composer merge
    """
    if request.user.profile.superuser == False:
        raise Http404
    
    try:
        lComposerMergeRequest = ComposerMergeRequest.objects.filter(id=pMergeComposerRequestSerial)[0]
    except IndexError:
        raise Http404
    
    # send email back to original submitter
    lReason = request.POST['reason']
    
    if lReason:
        lSubmitterUser = lComposerMergeRequest.owner
        lDestination = lSubmitterUser.email
    else:
        lDestination = 'tsawyer@brassbandresults.co.uk'
    
    lContext = {'Reason' : lReason, }
    notification.delay(None, lComposerMergeRequest, 'composer', 'reject', request.user, browser_details(request), pDestination=lDestination, pAdditionalContext=lContext)
        
    # delete merge request
    lComposerMergeRequest.delete()
    
    return render_auth(request, 'blank.htm')


@login_required
def merge_action(request, pMergeComposerRequestSerial):
    """
    Perform a merge of composers
    """  
    if request.user.profile.superuser == False:
        raise Http404
    
    try:
        lMergeRequest = ComposerMergeRequest.objects.filter(id=pMergeComposerRequestSerial)[0]
    except IndexError:
        raise Http404
    
    lFromComposer= lMergeRequest.source_composer
    lToComposer = lMergeRequest.destination_composer
    
    lCompositionsToMove = TestPiece.objects.filter(composer=lFromComposer)
    for piece in lCompositionsToMove:
        piece.composer = lToComposer
        piece.lastChangedBy = request.user
        piece.save()
    
    lArrangementsToMove = TestPiece.objects.filter(arranger=lFromComposer)
    for piece in lArrangementsToMove:
        piece.arranger = lToComposer
        piece.lastChangedBy = request.user
        piece.save()
            
    notification.delay(None, lMergeRequest, 'composer_merge', 'done', request.user, browser_details(request))
    lSubmitterUser = lMergeRequest.owner
    notification.delay(None, lMergeRequest, 'composer', 'merge', request.user, browser_details(request), pDestination=lSubmitterUser.email)
    
    lFromComposer.delete()
    lMergeRequest.delete()
        
    return HttpResponseRedirect('/move/composers/')