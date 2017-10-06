from django.contrib.sitemaps import Sitemap
from pieces.models import Composer

class ComposerSitemap(Sitemap):
    changefreq="weekly"
    priority="0.7"
    
    def items(self):
        return Composer.objects.all()
    
    def lastmod(self, obj):
        try:
            return obj.last_modified
        except IndexError:
            return None