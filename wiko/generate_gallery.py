#! /usr/bin/python
import glob
import Image
import os

dir ="borra/"

size=210
prefix = "thumb_"
columns=4

files = [os.path.basename(filename) for filename in glob.glob(dir+"*.jpg")+glob.glob(dir+"*.png") if prefix not in filename]

for imagefile in files:
	im = Image.open(dir+imagefile)
	im.thumbnail((size, size), Image.ANTIALIAS)
	im.save(dir + prefix + imagefile, "JPEG")


table = [
	"<table> <tr>"
]
count=1
for filename in files:
	table += ["<td style='text-align:center'><a href='%s' <img src='%s'/></a><br />%s </td>" % (
		filename, 
		prefix+filename,
		filename[:-4])
		]
	if count == columns:
		table += ["</tr>", "<tr>"]
		count=0
	count+=1

table += [
	"</tr></table>"
	]
template = file(os.path.expanduser("skeleton_gallery.html")).read()
content = "\n".join(table)
index = template%{'title': 'screenshots', 'content': content, 'author':'generated'}

file(dir+"/index.html","w").write( index )
