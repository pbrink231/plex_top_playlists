#!/usr/bin/env python

from lxml.html import parse

#tree = parse("http://www.imdb.com/list/ls069751712/")
tree = parse("http://www.imdb.com/list/ls021389231/")
custom_ids = tree.xpath("//div[contains(@class, 'lister-item-image ribbonize')]/@data-tconst")

print type(tree)
print tree
print custom_ids
