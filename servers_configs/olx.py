# base www + category + ? + built query

from .base_searcher import SearchEngine
import time


class OlxSearchEngine(SearchEngine):

    def __init__(self, options, filters):
        #super().__init__(options, filters)

        #self.filters    = filters
        self.base_www   = "http://olx.pl"
        self.pager_txt  = "page="
        self.list_start = "offers_table"
        self.list_end   = "pagerGoToPage"
        # tr && lambda: bool(subitem.parent != 'tbody')    // with find_all
        # tbody > tr                                       // with select
        # tr                                               // with find_all
        self.subitem    = "tbody > tr"
        self.page_from  = int(filters["page_from"])
        self.page_to    = int(filters["page_to"])
        # category OR querystr must be set by user
        self.category   = ""
        # TODO:unfinished!
        self.querystr   = "/oferty/q-"

        self.sort_by    = "search[order]"
        self.price_from = "search[filter_float_price:from]"
        self.price_to   = "search[filter_float_price:to]"


        self.query_fields = ["sort_by", "price_from", "price_to"]

        #print (dir(super()))  atrybuty dostepne ale ?? getattr(super(), key) - AttributeError. ???

        # user settings override/append default_config settings:
        try:
            setattr(self, "category", options.pop("category"))
            self.querystr = ""
        except KeyError:
            setattr(self, "querystr", getattr(self, "querystr") + options.pop("querystr"))

        for key in options:
            #self.query_fields.append(key)
            #print (key)
            #pass
            setattr(self, key, getattr(self, key) + '=' + options[key])

        # TODO: Fix and move to proper place.
        self.incl = [fil.strip() for fil in filters["include"].replace('"', '').replace('\n','').split(',')]
        self.excl = [fil.strip() for fil in filters["exclude"].replace('"', '').replace('\n','').split(',')]

        #image
        #description

        # allow user to utilize SOMEHOW options like:
        #  {"price_smallest":"filter_float_price:asc",
        #   "price_highest":"filter_float_price:desc",
        #   "newest_item":"created_at:desc"}

        # query builder => & search[item:type]=value => search[filter_float_price:from]=400
        # query builder => & search[order]=filter_float_price,asc"
        # query builder => & search[filter_enum_state][0]=used & search[filter_enum_state][1]=new
        # query builder => & search[photos]=1


        #template_1 = search[{}:{}]=xx
        #template_2 = search[{}]=yy
        #template_3 = search[{}][{}]=zz


        # for key in default_config:
        #     #logging.debug("Setting '{}':{}".format(key, default_config[key]))
        #     setattr(self, key, default_config[key]) # not using k,v for py2/py3

        # try:
        #     _ = requests.get(self.base_www)
        # except AttributeError:
        #     logging.fatal("Server configuration file is invalid.")
        # except request.ConnectionError:
        #     logging.fatal("Failed to connect " + base_www)
        # except request.MissingSchema:
        #     logging.fatal("Inproper address " + base_www)


        self.query = self._query_builder()

    def _item_to_elements_parser(self, item):
        """ specializes base class function """
        elements = {}

        ####### Sad solution - look for better one. #######
        items = ["data", "img", "title", "link", "price"]
        values = ("item.p.string.strip()", 'item.img["src"]', 'item.img["alt"]',
                   '''item.find("a", {"class":"detailsLink"})['href']''',
                   '''item.find('strong').string.strip()''')
        for key, value in zip(items, values):

            # CONVERT TIME
            # if key == "data":
            #     try:
            #         print (time.strptime(eval(value), "%d  %b"))
            #     except Exception as error:
            #         print (error) # time data '5  paz' does not match format '%d  %b'

            try:
                elements.update({key:eval(value)})
            except (TypeError, AttributeError):
                elements.update({key:None})


        # print()
        # for key, val in elements.items():
        #     print (key, val)
        # print()
        ###################################################
        return elements


    def _query_builder(self):
        query = ["".join(getattr(self, item)) for item in self.query_fields]
        query.append(self.pager_txt)
        return "".join([self.base_www, self.category, self.querystr, "/?", "&".join(query)])