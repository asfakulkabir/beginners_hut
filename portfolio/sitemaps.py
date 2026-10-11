from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticPortfolioSitemap(Sitemap):
    def items(self):
        return ['portfolio', 'all_work', 'graphics_portfolio', 'about_us', 'contact_us']

    def location (self, item):
        return reverse(item)