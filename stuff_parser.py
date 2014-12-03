#-*- coding: utf-8 -*-
""" This module: """

import sys
import logging
#import importlib

from tools.config_loader import MyConfig
# It would be nice to dynamically load those classes depending on needs ...
from servers_configs.olx import OlxSearchEngine as olx
#from servers_configs.allegro import AllegroSearchEngine as allegro
#from servers_configs.ebay import EbaySearchEngine as ebay

def main(Engine, options, filters, output):

    engine = Engine(options, filters)
    try:
        results = engine.run()
    except ValueError as error:
        results = []
        logging.error("SearchEngine run() failed: " + str(error))

    if output == "terminal":
        print("="*20 + " results " + "="*20)
        for dictionary in results:
            for key, val in dictionary.items():
                print (key, val)
        print()
    elif output == "pdf":
        pass
    elif output == "html":
        FILENAME = "/tmp/stuff_parser.html"

        with open(FILENAME, "wb") as file_:
            file_.truncate()
            file_.write(bytes("""<html><br>\n <table>\n""",'utf-8'))
            template = """
            \n<tr>
            <td><img width=94 height=72 src={}></img></td>
            <td>{}</td>
            <td>{}</td>
            <td><a href='{}''>LINK</a></td></tr>
            """
                #for key, val in dictionary.items():??
            for dictionary in results:
                
                file_.write(bytes(template.format(
                    dictionary["img"],#.decode('utf8', 'ignore').encode('utf8', 'replace'),
                    dictionary["title"],#.decode('utf8', 'ignore').encode('utf8', 'replace'),
                    dictionary["price"],#.decode('utf8', 'ignore').encode('utf8', 'replace'),
                    dictionary["link"],#.encode("utf-8").encode('utf8', 'replace')
                    ), 'utf-8'))
                    

            file_.write(bytes("\n</table></html>", 'utf-8'))
            logging.info("file writer exported results to: file://" + FILENAME)
    else:
        logging.debug("Error.")
    return 0

if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s '
                               '%(levelname)s:%(message)s',
                                level=logging.DEBUG)

    proper_syntax = "Syntax is {} {} {}".format(sys.argv[0],
                                        "config_file",
                                        "item_details_file",
                                        "[pdf|html|terminal=default]")

    # TODO: argparse

    try:
        module_name = sys.argv[1]
    except IndexError:
        print (proper_syntax)
        module_name, config = None, None
    else:
        # TODO: dynamically assign module to variable from variable name?
        if module_name == "olx":
            config = olx
        elif module_name == "allegro":
            config = allegro
        else:
            config = None

    try:
        options, filters = MyConfig(sys.argv[2])
    except IndexError:
        print (proper_syntax)
        filters = None
        options = None
    except ValueError:
        logging.fatal("Config for '{}' not found.".format(sys.argv[2]))
        sys.exit(-1)
    # except MyConfig.ParsingError:
    #     logging.fatal("Config for '{}' not found.".format(file_))
    # with open(sys.argv[1]) as config_file:
    #         config = MyConfigParser(config_file)
    # except (IOError, OSError, IndexError):
    #     config = None
    try:
        if sys.argv[3] in ("pdf", "html", "terminal"):
            output = sys.argv[3]
        else:
            output = "terminal"
    except IndexError:
        output = "terminal"

    sys.exit(main(config, options, filters, output))
