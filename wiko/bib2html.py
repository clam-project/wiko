#!/usr/bin/python

# this script processes a .bib file adding html anchors 
# to each bib entry so they can be linked.

import sys, re
header = """
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
    "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" >
<head>
<link rel='stylesheet' href='style.css' type='text/css'/>
</head>
<body>
<pre>
"""
footer = """
</body>
</html>
"""
import sys
bibfilename = "bibliography.bib"
result = []
result += [header]

entry = re.compile(r"@\w*{([^,]*),")
for line in file(bibfilename) :
	m = entry.search(line)
	if m and not 'comment' in line:
		id = m.group(1)
		result += ["<a id='%s'/>\n"%id]
	result += [line]
result += [footer]
file(bibfilename+".html", "w").writelines(result)
