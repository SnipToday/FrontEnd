from django.contrib.sitemaps import Sitemap
from .models import Snip

class SnipSitemap(Sitemap):
    changefreq = "monthly" # TODO check this! maybe should be never or daily
    priority = 0.5

    def items(self):
        return Snip.objects.filter(live=True)

    def lastmod(self, obj):
        return obj.latest_revision_created_at