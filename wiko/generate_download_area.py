#!/usr/bin/python
import os
import datetime

dirs = [
	("Downloads from ipracine ftp", "/home/racineftp/downloads/"),
#	("Acustica-BM downloads", "tmp/"),
]
blacklist = [
	"index.html",
	"style.css",
	"img",
]

def humanReadableSize(filename) :
	if os.path.isdir(filename) : return ""
	sufixes = [
		("P",1<<50),
		("T",1<<40),
		("G",1<<30),
		("M",1<<20),
		("K",1<<10),
	]
	size = os.path.getsize(filename)
	for suffix, scale in sufixes:
		if size/scale > 1.1:
			return "%.2f %sb"%(float(size)/scale, suffix)
	return str(size)+" b"

def humanReadableTime(filename) :
	if os.path.isdir(filename) : return ""
	return str(datetime.datetime.fromtimestamp(os.path.getmtime(filename)))


template = file(os.path.expanduser("scheleton_download.html")).read()

for title, dirname in dirs:
	dirname = os.path.expanduser(dirname)
	if not os.access(dirname, os.X_OK):
		print "Not available: %s"%dirname
		continue
	print "Generating index for %s"%dirname
	files = os.listdir(dirname)
	files = filter((lambda a : a not in blacklist ), files) # Filter blacklisted
	dirs = [dir+"/" for dir in filter((lambda a : os.path.isdir(os.path.join(dirname, a)) ), files) ]
	files = filter((lambda a : not os.path.isdir(os.path.join(dirname, a)) ), files) # Filter dirs
	files.sort()

	table = "\n".join( [ "<tr><td><a href='%(filename)s'>%(filename)s</a></td><td>%(size)s</td><td>%(date)s</td></tr>"%{
			'filename': filename,
			'size': humanReadableSize(os.path.join(dirname, filename)),
			'date': humanReadableTime(os.path.join(dirname, filename)),
		} for filename in dirs + files ])
	content = "<h1> Downloads </h1>"
	content += "<h2> %s </h2>"%title
	content += "\n".join(["<table width='100%'>",table,"</table>"])
	index = template%{'title': title, 'content': content, 'author':'generated'}
	open(os.path.join(dirname,"index.html"),"w").write(index)


