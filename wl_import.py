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
    def __init__(self,attribute_whitelist=[]):
        super(HTMLBodyParser, self).__init__()
        self.document = etree.Element("div")
        # When we encounter a start tag we push to the stack, an end tag pulls
        # in this way we can properly mirror the HTML structure
        self._tag_stack = []
        self._tag_stack.append(self.document)
        # Attribute whitelist helps block malicious junk in imports
        if attribute_whitelist:
            self._attribute_whitelist = attribute_whitelist
        else:
            self._attribute_whitelist = ["href", "src"]
        self._in_body = False
        
    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self._in_body = True
        elif self._in_body:
            new_tag = etree.SubElement(self._tag_stack[-1],tag)
            for attribute in attrs:
                if attribute[0] in self._attribute_whitelist:
                    new_tag.set(attribute[0], attribute[1])
            self._tag_stack.append(new_tag)
            

    def handle_data(self, data):
        if self._in_body:
            self._tag_stack[-1].text = data

    def handle_endtag(self, tag):
        if tag == "body":
            self._in_body = False
        elif self._in_body:
            self._tag_stack.pop()
