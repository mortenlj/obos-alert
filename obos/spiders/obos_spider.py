from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from obos.items import ObosItem

# [u'Adresse:']
# [u'Bygg\xe5r:']
# [u'Areal:']
# [u'Boligtype:']
# [u'Diverse:']
# [u'Prisantydning:']
# [u'Fellesgjeld:']
# [u'Totalpris:']
# [u'Felleskost:']
# [u'Forkj\xf8psrett:']
# [u'Meldefrist:']
# [u'Ansiennitet pt:']


class ObosSpiderSpider(CrawlSpider):
    name = 'obos'
    allowed_domains = ['obos.no']
    start_urls = ['http://www.obos.no/boliger-med-forkjopsrett']

    rules = (
        Rule(SgmlLinkExtractor(allow=r'boliger-med-forkjopsrett\?p=\d+')),
        Rule(SgmlLinkExtractor(allow=r'boligmedforkjopsrett\?id=\d+'), callback='parse_item'),
    )

    _BULLET_MAPPING = {
        u'Adresse:': "location",
        u'Areal:': "area",
        u'Boligtype:': "property_type",
        u'Prisantydning:': "price",
        u'Fellesgjeld:': "debt",
        u'Totalpris:': "total_price",
        u'Meldefrist:': "deadline",
        u'Ansiennitet pt:': "current_seniority"
    }

    def __init__(self, *a, **kw):
        super(ObosSpiderSpider, self).__init__(*a, **kw)

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)
        i = ObosItem()
        panels = hxs.select("//div[@id=\"ctl00_body_PanelDetails\"]")
        bullets = panels.select("dl")
        for bullet in bullets:
            self.parse_bullet(bullet, i)
        return i

    def parse_bullet(self, bullet, i):
        name = bullet.select("dt/text()").extract()[0]
        value = bullet.select("dd/text()").extract()[0]
        field = self._BULLET_MAPPING.get(name, None)
        if field:
            i[field] = value
