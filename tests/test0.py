#!/usr/bin/python

import re

guid = "com.plexapp.agents.imdb://tt0366548?lang=en"

print re.search(r'tt(\d+)\?', guid).group(0)
print re.search(r'tt(\d+)\?', guid).group(1)
print re.search(r'tt(\d+)\?', guid).group(2)
