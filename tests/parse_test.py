#!/usr/bin/env python

from lxml.html import parse

#tree = parse("http://www.imdb.com/list/ls069751712/")
tree = parse("http://www.imdb.com/list/ls009668531/")
#custom_ids = tree.xpath("//div[contains(@class, 'lister-item-image ribbonize')]/@data-tconst")
name = tree.xpath("//h1[contains(@class, 'header list-name')]")[0].text.strip()

print type(tree)
print tree
print name
