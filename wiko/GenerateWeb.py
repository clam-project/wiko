#!/usr/bin/python

# bugs: @cite:some at end of line
import glob
import os.path
import re
import sys

enableLaTeX = True
enableHtml = True

inlineHtmlSubstitutions = [  # the order is important
	(r"'''(([^']|'[^']|''[^'])*)'''", r"<b>\1</b>"),
	(r"''(([^']|'[^'])*)''", r"<em>\1</em>"),
	(r"\[(\S*)\s(.+)\]", r"<a href='\1'>\2</a>"),
	(r"\[(\S*)\]", r"<a href='\1'>\1</a>"),
	(r"@cite:([-_a-zA-Z0-9]*)", r"<a href='dataflow.bib.html#\1'>[\1]</a>"), # TODO: hover box with bib info
	(r"`([^`]*)`", r"<img src=http://www.forkosh.dreamhost.com/mimetex.cgi?\1 />"),
]
inlineLatexSubstitutions = [  # the order is important
	(r"'''(([^']|'[^']|''[^'])*)'''", r"{\\bf \1}"),
	(r"''(([^']|'[^'])*)''", r"{\\em \1}"),
	(r"\[(\S*)\s(.+)\]", r"\2\\footnote{\\hyperef{\1}{\1}}"),
	(r"\[(\S*)\]", r"\\hyperef{\1}{\1}"),
	(r"@cite:([-_a-zA-Z0-9]*)", r"\cite{\1}"),
	(r"`([^`]*)`", r"$\1$"),
]

header = re.compile(r"^(=+)([*]?)\s*([^=]+?)\s*\1\s*$")
headersHtml = [
	r"<h1 id='toc_%(n)s'>%(title)s</h1>",
	r"<h2 id='toc_%(n)s'>%(title)s</h2>",
	r"<h3 id='toc_%(n)s'>%(title)s</h3>",
	r"<h4 id='toc_%(n)s'>%(title)s</h4>",
]
headersLatex = [
	r"\chapter{%(title)s}",
	r"\section{%(title)s}",
	r"\subsection{%(title)s}",
	r"\subsubsection{%(title)s}",
]

li  = re.compile(r"^([*#]+)(.*)")
pre = re.compile(r"^[ \t](.*)")
var = re.compile(r"^@([^:]*): (.*)")
fig = re.compile(r"^Figure:[\s]*([^\s]+)[\s]*([^\s]+)(.*)");
todo = re.compile(r"^TODO:[\s]*(.*)");
label = re.compile(r"^Label:[\s]*([^\s]+)");
div = re.compile(r"^([a-zA-Z0-9]+):$")
cite = re.compile(r"\[[a-zA-Z0-9]+\]");

divMarkersLatex = {
	'Abstract' : ('\\begin{abstract}', '\\end{abstract}'),
	'Keywords' : ('\\begin{keywords}', '\\end{keywords}'),
	'Equation' : ('\\begin{equation}', '\\end{equation}'),
	'Math' : ('\\[', '\\]'),
}

divMarkersHtml = {
	'Abstract' : ('<div class="abstract"><b>Abstract:</b>', '</div>'),
	'Keywords' : ('<div class="keywords"><b>Keywords:</b>', '</div>'),
	'Equation' : ('<div class="equation"><b>Equation:</b>', '</div>'),
	'Math' :     ('<div class="equation"><b>Equation:</b>', '</div>'),
}

def stripUtfMarker(content) :
	import codecs
	if content.startswith( codecs.BOM_UTF8 ):
		encoded = unicode(content,"utf8")
		stripped = encoded.lstrip( unicode( codecs.BOM_UTF8, "utf8" ) )
		return stripped.encode("utf8")
	return content
#		content = content[3:] # remove the utf8 marker

class WikiCompiler :

	def compileInlines(self, inlines) :
		self.inlines = [ (re.compile(wikipattern), substitution) 
			for wikipattern, substitution in inlines  ]
	def substituteInlines(self, line) :
		for compiledPattern, substitution in self.inlines :
			line = compiledPattern.sub(substitution, line)
		return line


	def closeAnyOpen(self) :
		if self.closing == "" : return
		self.result.append(self.closing)
		self.closing=""
	def openBlock(self,opening,closing):
		self.closeAnyOpen()
		self.result.append(opening)
		self.closing=closing

	def addToc(self, level, title) :
		self.toc.append( (level, title) )
		return len(self.toc)
	def buildToc(self) :
		"""Default, empty toc"""
		return ""

	def process(self, content) :
		self.itemLevel = ""
		self.closing=""
		self.result=[]
		self.spanStack = []
		self.toc = []
		self.vars = {
			'title': '',
			'author': '',
		}
		for line in content.splitlines() :
			self.processLine(line)
		self.processLine("")
		self.vars["content"] = ("\n".join(self.result)) % {
			'toc': self.buildToc(),
		}
		return self.vars


class LaTeXCompiler(WikiCompiler) :
	def __init__(self) :
		self.compileInlines(inlineLatexSubstitutions)
		self.headerPatterns = headersLatex
	def processLine(self, line) :
		newItemLevel = ""
		liMatch = li.match(line)
		preMatch = pre.match(line)
		headerMatch = header.match(line)
		varMatch = var.match(line)
		figMatch = fig.match(line)
		todoMatch = todo.match(line)
		labelMatch = label.match(line)
		divMatch = div.match(line)
		if liMatch :
			self.closeAnyOpen()
			newItemLevel = liMatch.group(1)
			line = "%s\item %s" %("\t"*len(newItemLevel), liMatch.group(2) )
		while len(newItemLevel) < len(self.itemLevel) or  \
				self.itemLevel != newItemLevel[0:len(self.itemLevel)]:
#			print "pop '", self.itemLevel, "','", newItemLevel, "'"
			tag = "itemize" if self.itemLevel[-1] is "*" else "enumerate"
			self.result.append("%s\\end{%s}"%("\t"*(len(self.itemLevel)-1),tag))
			self.itemLevel=self.itemLevel[0:-1]
		if line=="" :
			self.closeAnyOpen()
		elif preMatch:
			if self.closing != "\\end{quote}" :
				self.openBlock("\\begin{quote}", "\\end{quote}")
			line=line[1:] # remove the pre indicator space
		elif varMatch :
			self.vars[varMatch.group(1)] = varMatch.group(2)
			print "Var '%s': %s"%(varMatch.group(1),varMatch.group(2))
			return
		elif figMatch :
			self.closeAnyOpen()
			flags = [ flag.strip() for flag in figMatch.group(3).split() if flag.strip() ]
			imageFlags = []
			if "rotated90" in flags :
				imageFlags.append("angle=90")
			if "halfSize" in flags:
				imageFlags.append("scale=.5")
			else:
				imageFlags.append("width=4.8in")
			sizeSpecifier = "[" + ",".join(imageFlags) + "]"
			print "flags:", sizeSpecifier
			self.openBlock(
				"\\begin{figure*}[htbp]\n"
				"\\begin{center}\\includegraphics%(size)s{%(img)s}\end{center}\n"
				"\\caption{%%%%"%{
					'img': figMatch.group(2),
					'size': sizeSpecifier,
					},
				"}\n\\label{%(id)s}\n"
				"\\end{figure*}\n"%{
					'id':figMatch.group(1)},
				)

			return
		elif todoMatch :
			line="\\marginpar{\\footnotesize TODO: %s}"%todoMatch.group(1)
		elif labelMatch :
			line="\label{%s}"%labelMatch.group(1)
		elif headerMatch :
			self.closeAnyOpen()
			title = headerMatch.group(3)
			level = len(headerMatch.group(1))
			n=self.addToc(level,title)
			line = self.headerPatterns[level-1]%{
				"title": title,
				"label": n,
				"level": level,
			}
		elif not liMatch : 
			if divMatch :
				divType = divMatch.group(1)
				try :
					opening, closing = divMarkersLatex[divType]
					self.openBlock(opening, closing)
					return
				except: 
					print "Not supported block class", divType
		# Equilibrate the item level
		while len(self.itemLevel) != len(newItemLevel) :
			self.closeAnyOpen()
#			print "push '", self.itemLevel, "','", newItemLevel, "'"
			levelToAdd = newItemLevel[len(self.itemLevel)]
			tag = "itemize" if levelToAdd is "*" else "enumerate"
			self.result.append("%s\\begin{%s}"%("\t"*len(self.itemLevel),tag))
			self.itemLevel += levelToAdd
		line = self.substituteInlines(line)	
		self.result.append(line)


class HtmlCompiler(WikiCompiler) :
	def __init__(self) :
		self.compileInlines(inlineHtmlSubstitutions)
		self.headerPatterns = headersHtml
	def buildToc(self) :
		result = []
		lastLevel = 0
		i=1
		result+=["<h2>Index</h2>"]
		result+=["<div class='toc'>"]
		for (level, item) in self.toc :
			while lastLevel < level :
				result += ["<ul>"]
				lastLevel+=1
			while lastLevel > level :
				result += ["</ul>"]
				lastLevel-=1
			result+=["<li><a href='#toc_%i'>%s</a></li>"%(i,item)]
			i+=1
		while lastLevel > 0 :
			result += ["</ul>"]
			lastLevel-=1
		result += ["</div>"]
		return "\n".join(result)

	def processLine(self, line) :
		newItemLevel = ""
		liMatch = li.match(line)
		preMatch = pre.match(line)
		headerMatch = header.match(line)
		varMatch = var.match(line)
		figMatch = fig.match(line)
		todoMatch = todo.match(line)
		labelMatch = label.match(line)
		divMatch = div.match(line)
		if liMatch :
			self.closeAnyOpen()
			newItemLevel = liMatch.group(1)
			line = "%s<li>%s</li>" %("\t"*len(newItemLevel), liMatch.group(2) )
		while len(newItemLevel) < len(self.itemLevel) or  \
				self.itemLevel != newItemLevel[0:len(self.itemLevel)]:
#			print "pop '", self.itemLevel, "','", newItemLevel, "'"
			tag = "ul" if self.itemLevel[-1] is "*" else "ol"
			self.result.append("%s</%s>"%("\t"*(len(self.itemLevel)-1),tag))
			self.itemLevel=self.itemLevel[0:-1]
		if line=="" :
			self.closeAnyOpen()
		elif preMatch:
			if self.closing != "</pre>" :
				self.openBlock("<pre>","</pre>")
			line=line[1:] # remove the pre indicator space
		elif varMatch :
			self.vars[varMatch.group(1)] = varMatch.group(2)
			return
		elif figMatch :
			self.closeAnyOpen()
			self.openBlock(
				"<div class='figure' id='%(id)s'><img src='%(img)s' alt='%(id)s'/><br />"%{
						'id':figMatch.group(1),
						'img': figMatch.group(2),
						},
				"</div>")
			return
		elif todoMatch :
			line=" <span class='todo'>TODO: %s</span> "%todoMatch.group(1)
		elif labelMatch :
			line=" <a name='#%s'></a>"%labelMatch.group(1)
		elif headerMatch :
			self.closeAnyOpen()
			title = headerMatch.group(3)
			level = len(headerMatch.group(1))
			n=self.addToc(level,title)
			line = self.headerPatterns[level-1]%{
				"title": title,
				"n": n,
				"level": level,
			}
		elif not liMatch : 
			if divMatch :
				divType = divMatch.group(1)
				try :
					opening, closing = divMarkersHtml[divType]
					self.openBlock(opening, closing)
					return
				except: 
					print "Not supported block class", divType
			elif self.closing == "" :
				self.openBlock("<p>","</p>")
		# Equilibrate the item level
		while len(self.itemLevel) != len(newItemLevel) :
			self.closeAnyOpen()
#			print "push '", self.itemLevel, "','", newItemLevel, "'"
			levelToAdd = newItemLevel[len(self.itemLevel)]
			tag = "ul" if levelToAdd is "*" else "ol"
			self.result.append("%s<%s>"%("\t"*len(self.itemLevel),tag))
			self.itemLevel += levelToAdd
		line = self.substituteInlines(line)	
		self.result.append(line)


scheletonFileName = "scheleton.html"
scheleton = file(scheletonFileName).read()

def needsRebuild(target, source) :
	return True
	if not os.path.exists(target) : return True
	if os.path.getmtime(target)<os.path.getmtime(source): return True
	if os.path.getmtime(target)<os.path.getmtime(scheletonFileName) : return True
	return False

# Generate HTML with HTML content files + scheleton
for contentFile in glob.glob("content/*.html") :
	target = os.path.basename(contentFile)
	if not needsRebuild(target, contentFile) :
		print target, "is up to date."
		continue
	print "Generating", target, "from", contentFile, "..."
	content = file(contentFile).read()
	file(target,"w").write(scheleton%{'title':'', 'content':content})

# Generate LaTeX and HTML from wiki files
for contentFile in glob.glob("*.wiki") :
	base = os.path.basename(contentFile)
	target = "".join(os.path.splitext(base)[0:-1])+".html"
	targetTex = "".join(os.path.splitext(base)[0:-1])+".tex"
	if not needsRebuild(target, contentFile) :
		print target, "is up to date."
		continue
	print "Generating", target, "from", contentFile, "..."
	content = file(contentFile).read()
	content = stripUtfMarker(content)
	if enableHtml :
		htmlResult = HtmlCompiler().process(content)
		file(target,"w").write(scheleton%htmlResult)
	if enableLaTeX :
		texResult = LaTeXCompiler().process(content)
		file(targetTex,"w").write(texResult['content'])

blogEntries = []
for contentFile in glob.glob("blog/*.wiki") :
	blogDict = HtmlCompiler().process(stripUtfMarker(file(contentFile).read()))
	blogDict['name'] = os.path.splitext(os.path.split(contentFile)[-1])[0]
	blogEntries.append(blogDict)

def compareTimeStamps(x,y) :
	from datetime import datetime
	xTime = datetime.strptime(x['timestamp'], "%d/%m/%Y %H:%M")
	yTime = datetime.strptime(y['timestamp'], "%d/%m/%Y %H:%M")
	return yTime.toordinal()-xTime.toordinal()

blogEntries.sort(compareTimeStamps)

blogEntryScheleton = file("blogEntryScheleton.html").read()
blogScheleton = file("blogScheleton.html").read()

blogFrontPage = []

for entry in blogEntries :
	from datetime import datetime
	entry['timestamp'] = str(datetime.strptime(entry['timestamp'], "%d/%m/%Y %H:%M"))
	if not entry.has_key("tags") : entry["tags"] = ""
	print entry['timestamp'], entry['name'] , "|" , entry['title'] , "[", entry["tags"], ']'
	entry['link'] = "blog.%s.html"%entry["name"]
	targetBlog = "blog."+entry["name"]+".html"
	composed = blogEntryScheleton%entry
	file(targetBlog,"w").write(blogScheleton%{'content':composed})
	blogFrontPage.append(composed)

file("blog.index.html","w").write(blogScheleton%{'content':"\n".join(blogFrontPage)})


#os.system("(cd img; bash ./generateImages.sh)")
#os.system("bibtex TICMA_master_thesis_DavidGarcia")
#os.system("pdflatex TICMA_master_thesis_DavidGarcia")


