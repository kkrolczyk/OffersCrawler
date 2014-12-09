#!/usr/bin/env python
""" Search through offers in multiple pages, and filter those. """

import sys
import logging
import argparse
from importlib import import_module

#pyPDF2 # unmantained? reportlab tiresome but ok, pod => odt, rst2pdf, sphinx.

from tools.config_loader import MyConfig

def toFileWritter(results, output):
    def resultFeed(template=None):
        for item in results:
            items = (
                     item["img"],
                     item["title"],
                     item["price"],
                     item["link"],
                    )
            if template:
                yield template.format(*items)
            else:
                yield items #[item.encode('utf-8') for item in items]

    FILE = output['f']
    if output['t'] == "pdf":
        try:
            #from PIL import Image as image
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, ParagraphAndImage
            from reportlab.lib.styles import getSampleStyleSheet
        except ImportError:
            hints = "".join(["sudo apt-get install {}\n"
                             "".format(item) for item in ("PIL", "reportlab")])
            err = "Required modules are not accessible:" + hints
            logging.fatal(err)
        else:
            text = []
            doc = SimpleDocTemplate(FILE)
            style = getSampleStyleSheet()["Normal"]
            
            template = "{1} {2} <a color='blue' href='{3}'>{3}</a>"
            for item in resultFeed(template):
                text.append(ParagraphAndImage(
                                Paragraph(template.format(*item), style),
                                Image(item[0], 94, 72), side="left"
                                )
                            )
                text.append(Spacer(1, 5))
            doc.build(text)
            logging.info("file writer exported results to: file://" + FILE)

    elif output['t'] == "html":
            template = """
            \n<tr>
            <td><img width=94 height=72 src={}></img></td>
            <td>{}</td>
            <td>{}</td>
            <td><a href='{}'>LINK</a></td></tr>
            """
            FILE.truncate()
            FILE.write(bytearray("""<html><br>\n <table>\n""", encoding="utf-8"))
            for item in resultFeed(): # unicode pain below...
                FILE.write(template.format(*[i.encode("utf-8", "ignore") for i in item]))
            FILE.write(bytearray("\n</table></html>", encoding="utf-8"))
            FILE.close()
            logging.info("file writer exported results to: file://" + FILE.name)
    return

def run(engine, output):

    results = engine.run()
    if output == "terminal":
        print("="*20 + " results " + "="*20)
        for dictionary in results:
            for key, val in dictionary.items():
                print (key, val)
        print("="*21 + " done " + "="*21)
        return
    else:
        return toFileWritter(results, output)

def bootstrap(module_file, config_file, output):

    try:
        module = import_module(".".join(["servers_configs", module_file]))
    except ImportError as err:
        #parser.print_help()
        logging.fatal(err.message + " in ./servers_configs/")
        return
    try:
        options, filters = MyConfig(config_file)
    except RuntimeError as error:
        logging.fatal(error.message)
        return
    try:
        engine = module.Engine(options, filters)
    except (AttributeError, TypeError):
        logging.fatal("Module {} contains unrecoverable errors.")
        return

    return run(engine, output)

def main():

    logging.basicConfig(format='%(asctime)s '
                               '%(levelname)s:%(message)s',
                                level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("module_name", 
                         help="specifies target server and associated rules.")
    parser.add_argument("config_file", type=argparse.FileType('rb'),
                         help="specifies required filters for module")
    #parser.add_argument("output",  choices=["pdf","html","terminal"],
    #                    default="terminal", help="result format and location")
    subparsers = parser.add_subparsers(dest="output")
    file_parser = subparsers.add_parser("pdf")
    file_parser.add_argument("file_dest")
    file_parser = subparsers.add_parser("html")
    file_parser.add_argument("file_dest", type=argparse.FileType('wb'))
    just_parser = subparsers.add_parser("terminal")
    args = parser.parse_args()
    if not args.output == "terminal": 
        args.output = {"t":args.output, "f":args.file_dest}
    return bootstrap(args.module_name, args.config_file, args.output)

if __name__ == '__main__':
    main()