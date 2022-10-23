#! /usr/bin/python
import glob
from PIL import Image
import os

galleries = [
	# title, output, imageDir, template, columns, thumbsize
	("Screenshots", "screenshots.html", "screenshots", "skeleton.html", 4, 210)
]

def main():
	for title, output, imageDir, skeleton, columns, thumbSize in galleries :
		thumbSize=210
		prefix = "thumb_"
		columns=4
		formats = ["*.png", "*.jpg"]

		files = [
			os.path.basename(filename) 
				for format in formats
				for filename in glob.glob(os.path.join(imageDir,format))
				if prefix not in filename ]

		for imagefile in files:
			im = Image.open(os.path.join(imageDir,imagefile))
			im.thumbnail((thumbSize, thumbSize), Image.ANTIALIAS)
			im.convert('RGB').save(os.path.join(imageDir,prefix+imagefile), "JPEG")


		table = [ "<table> <tr>" ]
		labels = []
		count=1
		for filename in files:
			print(filename)
			table += ["<td style='text-align:center'><a href='%s'><img src='%s'/></a></td>" % (
				os.path.join(imageDir,filename), 
				os.path.join(imageDir,prefix+filename),
				) ]
			labels += ["<td style='text-align:center'>%s</td>" % filename[:-4] ]
			if count == columns:
				table += ["</tr>", "<tr>"]
				table += labels
				table += ["</tr>", "<tr>"]
				labels = []
				count=0
			count+=1
		if labels :
				table += ["</tr>", "<tr>"]
				table += labels
		table += [
			"</tr></table>"
			]

		template = open(os.path.expanduser(skeleton)).read()

		import re
		context = dict( [(item.group(1),"") for item in re.compile(r"%\((.+?)\)s").finditer(template) ] )
		content = "\n".join(table)
		context.update({'title': title, 'content': content, 'author':'WiKo'})

		open(output,"w").write( template % context )


if __name__ == '__main__':
	main()

