from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from obos.items import ObosItem, ObosLoader


class ObosSpider(CrawlSpider):
    name = 'obos'
    allowed_domains = ['obos.no']
    start_urls = ['http://www.obos.no/boliger-med-forkjopsrett']

    rules = (
        Rule(SgmlLinkExtractor(allow=r'boliger-med-forkjopsrett\?p=\d+')),
        Rule(SgmlLinkExtractor(allow=r'boligmedforkjopsrett\?id=\d+'), callback='parse_item'),
    )

    _BULLET_MAPPING = {
        u'Adresse:': "address",
        u'Areal:': "size",
        u'Prisantydning:': "price",
        u'Fastpris:': "price",
        u'Fellesgjeld:': "debt",
        u'Totalpris:': "total_price",
        u'Meldefrist:': "deadline",
        u'Ansiennitet pt:': "current_seniority"
    }

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)
        panels = hxs.select("//div[@id=\"ctl00_body_PanelDetails\"]")
        loader = ObosLoader(selector=panels, response=response)
        for bullet, field_name in self._BULLET_MAPPING.iteritems():
            loader.add_xpath(field_name, self._build_bullet_path(bullet))
        rooms_and_property_type_xpath = self._build_bullet_path(u'Boligtype:')
        loader.add_rooms_and_property_type(rooms_and_property_type_xpath)
        loader.add_value("link", response.url)
        return loader.load_item()

    def _build_bullet_path(self, bullet):
        return u"dl/dt[text()='%s']/../dd/text()" % bullet