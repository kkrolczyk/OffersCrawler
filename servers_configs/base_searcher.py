"""
    1. filter whole listing
    2. TODO: filter data provided via service's search option
    TODO: argparse
    TODO: line 38 add search = two types allegro/olx different query
    TODO: handle multiple categories
"""

import importlib
import logging

import requests                 # sudo apt-get install requests
from bs4 import BeautifulSoup   # sudo apt-get install BeautifulSoup4


class SearchEngine(object):
    """
        todo: check boolean logic according to ie
        http://nlp.stanford.edu/IR-book/html/\
        htmledition/processing-boolean-queries-1.html """

    def _page_to_items_parser(self, page):
        logging.debug("_page_to_items_parser, page len: {}".format(len(page)))
        # shorten BS parsing by stripping to only interesting html part
        try:
            start = page.index(self.list_start)
            end = page.index(self.list_end)
        except ValueError:
            logging.debug("Unable to find list_start/list_end for "
                          "this server. Parsing whole page...")
            page_strip = page
        else:
            page_strip = page[start:end]

        #with open("test.txt", "w") as out_file:
        #    out_file.write(page_strip)

        soup = BeautifulSoup(page_strip)
        # body = soup.find("tbody")
        #print (soup)
        try:
            #items = soup.find_all(self.subitem) #+ recursive = False ?
            items = soup.select(self.subitem)

        except Exception as error:
            print(str(error), str(type(error)))
            items = []
        return items

    def _item_to_elements_parser(self, item):
        # THIS PROBABLY TOO SHOULD BE SPECIALIZED
        #     print (item.name, item.attrs, sep=' ', end=" ")
        #     print (item.prettify())
        logging.error("This function should be specialized! {}".format(self))
        return None

    def _page_getter(self):
        logging.debug("_page_getter")
        for page_no in range(self.page_from, self.page_to):
            logging.debug("getting: {}{}".format(self.query, page_no))
            req = requests.get(self.query + str(page_no))
            req.encoding = "utf-8"
            yield req

    def _apply_filter(self, item):
        # TODO : UGLY
        haystack = item
        flag = False
        if any( [(x in haystack) for x in self.incl] ):
            flag = True
        if any( [(x in haystack) for x in self.excl] ):
            flag = False
        return flag

    def run(self):
        """ provide all results at once (blocks) """
        self.non_filtered_results = []
        self.filtered_results = []

        for page in self._page_getter():
            assert page.status_code == 200
            group_of_items = self._page_to_items_parser(page.text)
            logging.debug("Page contains {} parsable items.\
              ".format(len(group_of_items)))
            for item in group_of_items[1:]:
                ############################ FIX THIS
                subitems_dict = self._item_to_elements_parser(item)
                self.non_filtered_results.append(subitems_dict)
                # duplicate values...
                #print (subitems_dict)

                # # FILTER ITEM
                if subitems_dict["title"] and self._apply_filter(subitems_dict["title"].lower()):
                     self.filtered_results.append(subitems_dict)
                else:
                     continue
        return self.filtered_results
