# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from bbr.siteutils import render_auth
from pieces.models import TestPiece


def testpiecexml(request):
    """
    Render a list of test piece names as xml
    """
    lTestPieces = TestPiece.objects.all()
    return render_auth(request, 'feeds/testpieces.xml', {'TestPieces' : lTestPieces })