# -*- coding: utf-8 -*-
# (c) 2012 Tim Sawyer, All Rights Reserved

from django.contrib.sitemaps import Sitemap
from adjudicators.models import Adjudicator

class AdjudicatorSitemap(Sitemap):
    changefreq="weekly"
    priority="0.8"
    
    def items(self):
        return Adjudicator.objects.all().select_related()
    
    def lastmod(self, obj):
        try:
            return obj.contestadjudicator_set.all().order_by('-id')[0].last_modified
        except IndexError:
            return None