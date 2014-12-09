from .base_searcher import SearchEngine
import time
import logging

class Engine(SearchEngine):
    """ allegro www rule:
          a) base_www/listing.php/?string=QUERYSTR (global search)
          b) base_www/listing.php/?string=QUERYSTR&BUILT_QUERY (global search with parameters)
          c) base_www/category/?BUILT_QUERY (in category browse with parameters)
          #  d) base_www/category/?q=QUERYSTR&BUILT_QUERY (in category search) (not anymore?)
          d) base_www/listing/listing.php?string=QUERYSTR&BUILT_QUERY (in category search)
    """

    def __init__(self, options, filters):
        #super().__init__(options, filters)

        #self.filters    = filters
        self.base_www   = "http://allegro.pl"
        self.pager_txt  = "p="
        self.list_start = "offers" #<section class='offers'>
        self.list_end   = "listing-options-bottom" #<div class='listing-options-bottom'>
        # tr && lambda: bool(subitem.parent != 'tbody')    // with find_all
        # tbody > tr                                       // with select
        # tr                                               // with find_all
        self.subitem    = "article"
        self.page_from  = int(filters["page_from"])
        self.page_to    = int(filters["page_to"])
        # category OR querystr must be set by user
        self.category   = ""
        # TODO:unfinished!
        self.querystr   = "" #"/oferty/q-"

        self.sort_by    = "order" #order=p/pd -cena,q/qd-popularnosc,t/td-czas,d/dd-cena z dost,n/nd-nazwa
        self.price_from = "price_from"
        self.price_to   = "price_to"

        self.query_fields = ["sort_by", "price_from", "price_to"] #+offers type (buy now/auction)

        # user settings override/append default_config settings:
        try:
            setattr(self, "category", options.pop("category"))
            options.pop("querystr")
            self.querystr = ""
        except KeyError:
            setattr(self, "querystr", getattr(self, "querystr") + options.pop("querystr"))

        for key in options:
            setattr(self, key, getattr(self, key) + '=' + options[key])

        self.incl = [fil.strip() for fil in filters["include"].replace('"', '').replace('\n','').split(',')]
        self.excl = [fil.strip() for fil in filters["exclude"].replace('"', '').replace('\n','').split(',')]
        try:
            self.incl.remove('')
        except ValueError:
            pass
        try:
            self.excl.remove('')
        except ValueError:
            pass

        self.query = self._query_builder()

    def _item_to_elements_parser(self, item):
        """ specializes base class function """
        elements = {}
        #print item.prettify()
        #items = ["title", "img", "link", "price_buynow", "price_auction", "popularity"] #+location
        #values = ["item.div.",]
        # for key, value in zip(items, values):
        #     try:
        #         elements.update({key:eval(value)})
        #     except (TypeError, AttributeError):
        #         elements.update({key:None})
        
        ## THIS NEEDS REGEX, too much of a mess for BS
        tmp1 = item.find_all('a')[-2]
        tmp2 = item.div.div["data-img"]
        elements = {"title":tmp1.span.string.strip(), # or tmp1.text (both work.)
                    "images":eval(tmp2), #insecure! => ast.literal_eval
                    "img":eval(tmp2)[0][0], #insecure!
                    "link":self.base_www+item.div.a["href"], 
                    "price":item.div.find(attrs={"class":"price"}).find(attrs={"class":"label"}).nextSibling.strip(), 
                    #"price_auction":, 
                    #"popularity":item.div.find(attrs={"class":"popularity"}).strong.text.strip()
                    }
        # Also need to find better way to pass keys to display function
        return elements


    def _query_builder(self):
        query = ["".join(getattr(self, item)) for item in self.query_fields]
        query.append(self.pager_txt)
        querystr = "".join([self.base_www, self.category, self.querystr, "/?", "&".join(query)])
        logging.debug(querystr)
        return querystr