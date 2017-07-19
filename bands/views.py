from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection

from bbr3.render import render_auth

from bands.models import Band

def bands_list(request, pLetter='A'):
    """
    Show a list of all bands beginning with the specified letter
    """
    cursor = connection.cursor()
    lResults = {}
    cursor.execute("select band_id, count(*) from contests_contestresult group by band_id")
    rows = cursor.fetchall()
    for row in rows:
        lResults[row[0]] = row[1]
    cursor.close()
    
    lBandsQuery = Band.objects.all().select_related()
    if pLetter == 'ALL':
        lBands = lBandsQuery
    elif pLetter == '0':
        lBands = lBandsQuery.extra(where=["substr(bands_band.name, 1, 1) in ('0','1','2','3','4','5','6','7','8','9')"])
        pLetter = "0-9"
    else:
        lBands = lBandsQuery.filter(name__istartswith=pLetter)
    for band in lBands:
        try:
            band.resultcount = lResults[band.id]
        except KeyError:
            band.resultcount = 0
    lBandCount = Band.objects.all().count()
    return render_auth(request, 'bands/bands.html', {"Bands" : lBands,
                                                     "ResultCount" : len(lBands),
                                                     "BandCount" : lBandCount,
                                                     "StartsWith" : pLetter})