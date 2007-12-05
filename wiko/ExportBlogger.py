#!/usr/bin/python

useTidy=False

try:
	from xml.etree import ElementTree # for Python 2.5 users
except:
	from elementtree import ElementTree

import gdata.service
import gdata
import sys
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *

def buddyFor(widget, labelText) :
	label = QLabel(labelText)
	label.setBuddy(widget)
	return label

class LoginPage(QWizardPage) :
	def __init__(self, parent=None) :
		QWizardPage.__init__(self, parent)
		self.setTitle("Validation")
		self.setSubTitle("Introduce the login information for blogger.com.")
		self.login = QLineEdit(self)
		loginLabel = buddyFor(self.login,"Login")
		self.passwd = QLineEdit(self)
		self.passwd.setEchoMode(self.passwd.Password)
		passwdLabel = buddyFor(self.passwd,"Password")

		self.errorMessage=QLabel("")

		layout = QGridLayout(self)
		self.setLayout(layout)
		layout.addWidget(loginLabel, 0, 0)
		layout.addWidget(self.login, 0, 1)
		layout.addWidget(passwdLabel, 1, 0)
		layout.addWidget(self.passwd, 1, 1)
		layout.addWidget(self.errorMessage, 2, 0, 1, 2)

		self.registerField("Login", self.login)
		self.registerField("Password", self.passwd)

		self.login.setText("dgarcia@iua.upf.edu")
		self.passwd.setText("nmadmp")
		self.setCommitPage(True)
		self.setButtonText(QWizard.CommitButton, "Connect")
		

	def validatePage(self) :
		self.errorMessage.setText("<span style='color:blue'>Validating user</span>")
		try :
			self.wizard().login(self.login.text(), self.passwd.text())
		except Exception, e:
			self.errorMessage.setText("<span style='color:red'>%s</span>"%e)
			return False
		self.errorMessage.setText("<span style='color:green'>Logged in</span>")
		return True

class BlogSelectionPage(QWizardPage) :
	def __init__(self, parent=None) :
		QWizardPage.__init__(self, parent)
		self.setTitle("Blog selection")
		self.setSubTitle("Choose the blog you want to export")

		self.blogList = QListWidget(self)
		layout = QVBoxLayout(self)
		self.setLayout(layout)
		layout.addWidget(self.blogList)

		self.registerField("Blog*", self.blogList)

	def initializePage(self) :
		blogs = self.wizard().getBlogList()
		for title, url, id in blogs :
			print title, url, id
			item = QListWidgetItem(title)
			item.setData(Qt.UserRole, QVariant(id))
			self.blogList.addItem(item)

	def validatePage(self) :
		item = self.blogList.item(self.blogList.currentRow())
		self.wizard().blogId = str(item.data(Qt.UserRole).toString())
		print item.text(), self.wizard().blogId
		return True

class DirectoryPage(QWizardPage) :
	def __init__(self, parent=None) :
		QWizardPage.__init__(self, parent)
		self.setTitle("Target")
		self.setSubTitle("Choose the directory whery you want to dump the blog")

		self.fileedit = QLineEdit(self)
		self.pushButton = QPushButton(self)
		self.pushButton.setText('Choose')
		layout = QHBoxLayout(self)
		self.setLayout(layout)
		layout.addWidget(self.fileedit)
		layout.addWidget(self.pushButton)
		self.connect(self.pushButton,QtCore.SIGNAL("clicked()"),
			self.chooseDirectory)
		self.registerField("Directory*", self.fileedit)

	def chooseDirectory(self) :
		directory = QFileDialog.getExistingDirectory(self, "Choose a directory")
		if directory : self.fileedit.setText(directory)
		pass	

	def initializePage(self) :
		self.fileedit.setText(self.wizard().targetDir)
	def validatePage(self) :
		from os.path import isdir
		from os import access, W_OK
		targetdir = str(self.fileedit.text())
		if not isdir(targetdir): return False
		if not access(targetdir, W_OK) : return False
		self.wizard().targetDir = targetdir
		return True

class BloggerImportWizard (QWizard) :

	def login(self, user, password) :
		self.service = gdata.service.GDataService(user, password)
		self.service.source = 'Blogger_Python_Sample-1.0'
		self.service.service = 'blogger'
		self.service.server = 'www.blogger.com'
		self.service.ProgrammaticLogin()

	def getBlogList(self) :
		query = gdata.service.Query()
		query.feed = '/feeds/default/blogs'
		feed = self.service.Get(query.ToUri())
		blogs = [ 
			(
				entry.title.text, 
				entry.GetSelfLink().href,
				entry.GetSelfLink().href.split('/')[-1],
			) for entry in feed.entry ]
		return blogs
		
	def __init__(self, parent=None) :
		QWizard.__init__(self)
		self.setWindowTitle("Blogger.com to WiKo")
		self.setPixmap(self.LogoPixmap, QPixmap("blogger_logo_small.png"))
		self.setPixmap(self.WatermarkPixmap, QPixmap("wikologo.png"))
		self.blogId = None
		self.service = None
		self.targetDir = ""

		page = QWizardPage(self)
		page.setTitle("Introduction")
		layout = QVBoxLayout()
		page.setLayout(layout);
		label = QLabel(
			"""<p>This wizard will help you export your blog at blogger.com
				into a set of files which are able to be processed by WiKo.
				Note that once you export the files, you can still keep them
				up to date.</p>
				<p>Visit <a href='http://wiko.sourceforge.net'>WiKo web page</a>
				for further information.</p>
			""")
		label.setWordWrap(True)
		layout.addWidget(label)

		self.introPage  = self.addPage(page)
		self.loginPage  = self.addPage(LoginPage(self))
		self.blogPage   = self.addPage(BlogSelectionPage(self))
		self.targetPage = self.addPage(DirectoryPage(self))

	def dump(self) :
		print "Fetching blog %s"%self.blogId
		feed = self.service.GetFeed('/feeds/%s/posts/default' % self.blogId )

		print "Generator:", feed.generator.text
		print "Category:", [category.text for category in feed.category]
		print "Contributor:", [contributor.text for contributor in feed.contributor]
		print "Id:", feed.id.text
		print "Title:", feed.title and feed.title.text
		print "Subtitle:", feed.subtitle and feed.subtitle.text
		print "Link:", [link.href for link in feed.link]
		print "Updated:", feed.updated.text
		import string
		import os.path
		for entry in feed.entry:
			title = entry.title.text or "No title"
			id = entry.id.text.split("-")[-1]
			filename = "blog-"+id+"-"+title.title().translate(string.maketrans("",""),"! ,./:?")
			if entry.content.type=="html" : filename+=".wiki"
			else : filename+=".wiki"
			print self.targetDir, filename
			fullfilename = os.path.join(self.targetDir,filename)
			import codecs
			blogfile=codecs.open(fullfilename,'w','utf-8')
			print "Generating", fullfilename
			print >> blogfile, "@id:", id
			
			print >> blogfile, "@author:", (", ".join([author.name.text for author in entry.author]))
#			print >> blogfile, "@email:", (", ".join([author.email.text for author in entry.author if author.email]))
#			print >> blogfile, "@authoruri:", (", ".join([author.uri.href for author in entry.author if author.uri]))
#			print >> blogfile, "@contributor:", (", ".join([contrib.name.text for contrib in entry.contributor]))
#			print >> blogfile, "@source:", entry.source and entry.source.text
			print >> blogfile, "@title: " + entry.title.text
			print >> blogfile, "@updated:", entry.updated.text
			print >> blogfile, "@published:", entry.published.text
			print >> blogfile, "@category:", (", ".join([category.term for category in entry.category]))
			print >> blogfile
			content = self.wikify(entry.content.text)
			print >> blogfile, content
#			self.getComments(entry.id.text.split("-")[-1])
#			print dir(entry)
		print self.getComments()
	def wikify(self, content) :
		if useTidy:
			# TODO: This crashes (core dump!) for some files
			import tidy
			tidyOptions = dict(
				output_xhtml=1, 
				show_body_only=1,
				indent=1,
				tidy_mark=0,
				)
			tidy.parseString(content+"\n", **tidyOptions)
		import re
		substitutions = [
			(r'<a\s+href\s*=\s*"([^"]+)">([^<]+)\s*<\s*/\s*a\s*>', r"[[\1 \2]]"),
			(r"<a\s+href\s*=\s*'([^']+)'>([^<]+)\s*<\s*/\s*a\s*>", r"[[\1 \2]]"),
			(r'<br />', "\n"),
			('<p>', "\n\n"),
		]
		substitutions = [(re.compile(old), new) for old, new in substitutions]
		for old, new in substitutions :
			print "Content:", content
			content = old.sub(new, content)
		return content

	def getComments(self, postId=None) :
		# Build comment feed URI and request comments on the specified post
		feed_url = '/feeds/' + self.blogId
		feed_url+= "" if postId is None else '/' + postId
		feed_url+='/comments/default'
		feed = self.service.Get(feed_url)
		return [ dict(
			id = entry.id.text.split("-")[-1],
			title = entry.title.text,
			updated = entry.updated.text,
			content = self.wikify(entry.content.text),
			author = ",".join([author.name.text for author in entry.author])
			) for entry in feed.entry ]

def main():
	app=QtGui.QApplication(sys.argv)
	wizard = BloggerImportWizard()
	wizard.targetDir="blogdump/"
	if wizard.exec_() != QDialog.Accepted :
		return
	wizard.dump()


if __name__ == '__main__':
	main()

