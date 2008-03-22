#!/usr/bin/env python

import getopt
import htmlentitydefs
import os
import re
import sys
import urllib

from BeautifulSoup import BeautifulSoup

# This is a nice published snippet to unescape the HTML:
# http://effbot.org/zone/re-sub.htm
#
# TextMate snippets have to be escaped because they're in XML. Yasnippets,
# though, can not, so without this the literal escape text is inserted.
def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

class Snippet(object):
    def __init__(self, trigger, content):
        self.trigger = trigger
        self.content = content

    def __str__(self):
        return self.trigger

    def save_as_yasnippet(self, path):
        # Find empty file name
        filename = "%s/%s" % (path, self.trigger)

        if os.path.exists(filename):
            i = 1
            while os.path.exists(filename+"."+str(i)):
                i += 1
            filename += "." + str(i)

        snippet_file = open(filename, 'w')
        snippet_file.write("# This was cloned from a TextMate bundle for "
                           "yasnippet.\n# --\n")
        snippet_file.write(self.content)
        snippet_file.close()

class TextMateBundle(object):
    URI_BASE = "http://macromates.com/svn/Bundles/trunk/Bundles" \
        "/%s.tmbundle/Snippets/"

    def __init__(self, bundle):
        self.bundle = bundle

    def _create_soup(self, uri):
        sock = urllib.urlopen(uri)
        soup = BeautifulSoup(sock.read())
        sock.close()
        return soup

    def _snippet_uris(self):
        soup = self._create_soup(self.URI_BASE % self.bundle)
        return [self.URI_BASE % self.bundle +
                a.a["href"] for a in soup.findAll('li')[1:]]

    def download_snippets(self):
        snippets = []
        for uri in self._snippet_uris():
            try:
                snippets.append(self.create_snippet(uri))
            except NotImplementedError:
                pass
        return snippets

    def create_snippet(self, uri):
        soup = self._create_soup(uri)

        try:
            return Snippet(
                soup.find("key", text="tabTrigger").findNext("string").string,
                unescape(soup.find("key", text="content").findNext("string")
                         .string)
            )
        except AttributeError:
            # This is probably a keyboard-based snippet. Don't even bother...
            raise NotImplementedError

if __name__ == '__main__':
    def usage():
        print "Download TextMate bundle snippets and save them in path as " \
            "yasnippets."

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hb:p:",
                                   ["help", "bundle=", "path="])

        bundle, path = None, None
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                usage()
                sys.exit()
            elif opt in ("-b", "--bundle"):
                bundle = arg
            elif opt in ("-p", "--path"):
                path = arg

        if not bundle or not path:
            usage()
            sys.exit(2)

        bndl = TextMateBundle(bundle)
        for snippet in bndl.download_snippets():
            snippet.save_as_yasnippet(path)
    except getopt.GetoptError:
        usage()
        sys.exit(2)
