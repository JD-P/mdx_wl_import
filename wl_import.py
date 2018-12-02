from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.util import etree
from urllib import request
from html.parser import HTMLParser

import_pattern = r'\{import +([A-Za-z1-9_]+) (.*:\/\/.*) ?\}'

class WhistlingLobstersImport(Extension):
    def extendMarkdown(self, md, unknown):
        md.registerExtension(self)
        md.inlinePatterns.register(ImportProcessor(import_pattern, self),
                                   "WLImportInline",
                                   10)
        
class ImportProcessor(InlineProcessor):
    def handleMatch(self, match, full_text):
        """Find a import statement in the text, if it's there we extract the
        import type and its associated URL."""
        import_type, url = match.group(1,2)
        if import_type == "html":
            source = request.urlopen(url)
            parser = HTMLBodyParser()
            parser.feed(source.read().decode("UTF-8"))
            source.close()
            return parser.document, match.start(), match.end()

class HTMLBodyParser(HTMLParser):
    def __init__(self):
        super(HTMLBodyParser, self).__init__()
        self.document = ""
        self._in_body = False
        
    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self._in_body = True
        elif self._in_body:
            attributes = ' '.join(
                ["{}=\"{}\"".format(attr[0],attr[1]) for attr in attrs]
            )
            self.document += "<{} {}>".format(tag, attributes)

    def handle_data(self, data):
        if self._in_body:
            self.document += data

    def handle_endtag(self, tag):
        if tag == "body":
            self._in_body = False
        elif self._in_body:
            self.document += "</{}>".format(tag)
