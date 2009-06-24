#!/usr/bin/env python
r"""
=======================
eclipse_to_yasnippet.py
=======================

A script which converts exported Eclipse template files to `YASnippet`_ format.

Note that this script in its current form  will not convert Eclipse templates
perfectly and the YASnippet files will likely require editing.

Credits
=======

This script was written by `Nilesh Kapadia`_, but borrows code from:

``snippet_copier.py`` script written by `Jeff Wheeler`_ (which converts
Textmate bundles to `YASnippet`_ format).  The code in this script was generally
inspired by that script.

The ``unescape`` function is originally from 
`this site <http://effbot.org/zone/re-sub.htm>`_.

The `YASnippet`_ package was written by Chiyuan Zhang (a.k.a. *pluskid*) for
Emacs.

.. _YASnippet: http://code.google.com/p/yasnippet/
.. _Nilesh Kapadia: http://www.nileshk.com
.. _Jeff Wheeler: http://nokrev.com
"""

import htmlentitydefs
import optparse
import os
import re

from BeautifulSoup import BeautifulSoup

def unescape(text):
    """Replace HTML entities with original special characters.

    The entities are used in TextMate bundles because they're XML documents;
    placing characters like ``<`` and ``>`` would throw off a parser.

    This snippet was found at http://effbot.org/zone/re-sub.htm; many thanks!
    """
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

def write_snippet_to_file(path, snippet):
    """Write snippet to a file in YASnippet format
    
    Arguments:
    - `path`: Path to save snippets
    - `snippet`: Tuple containing snippet name and content
    """
    # Find empty file name
    filename = "%s/%s" % (os.path.abspath(path), snippet[0])

    if os.path.exists(filename):
        i = 1
        while os.path.exists(filename+"."+str(i)):
            i += 1
        filename += "." + str(i)

    snippet_file = open(filename, 'w')
    snippet_file.write("# This was cloned from an Eclipse template for "
                       "yasnippet.\n# --\n")
    snippet_file.write(snippet[1])
    snippet_file.close()

def eclipse_to_yasnippet(path, filename):
    """Convert an exported Eclipse templates file to YASnippet files
    
    Arguments:
    - `filename`: Exported Eclipse templates file
    """
    templates_file = open(filename)
    templatesSoup = BeautifulSoup(templates_file.read())
    templates_file.close()

    templates = templatesSoup.findAll('template')
    snippets = []
    for template in templates:
        snippet = template['name'], unescape(template.contents[0])
        write_snippet_to_file(path, snippet)
        snippets.append(snippet)
    
if __name__ == '__main__':
    print "Beginning conversion..."
    p = optparse.OptionParser(description = "Clone Eclipse templates for "                                                                   "YASnippet")
    p.add_option("--template", "-t", help = "Template file")
    p.add_option("--path", "-p", help="Path where YASnippets will be saved")

    options, arguments = p.parse_args()

    if not options.template:
        p.error("Template file must be specified")
    if not options.path:
        p.error("Path for YASnippets must be specified")
    
    eclipse_to_yasnippet(options.path, options.template)
    print "Done converting"
