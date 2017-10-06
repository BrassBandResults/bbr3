from django.contrib.sitemaps import Sitemap
from conductors.models import Conductor

class ConductorSitemap(Sitemap):
    changefreq="weekly"
    priority="0.7"
    
    def items(self):
        return Conductor.objects.all().select_related()
    
    def lastmod(self, obj):
        try:
            return obj.contestresult_set.all().order_by('-id')[0].last_modified
        except IndexError:
            return None