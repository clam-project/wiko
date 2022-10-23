# Wiko, the Wiki Compiler: Usage

By David García and Pau Arumi

%(toc)s

## Modes

WiKo enables different modes of execution
depending on what it founds on the working directory.

### Wrapping HTML content

This is the simplest mode of usage.
WiKo takes each .html file at the subdirectory 'content'
and creates an homonym html files at the working
directory by inserting such files into the skeleton
at the point where you inserted the '''%%<!-- -->(content)s''' tag.

This way you can fully update the look and feel of you web site
just by updating the skeleton without having to edit every html file
but still being an static page.

<!-- [[wikosample-htmlcontent.zip Sample WiKo project using html content]] -->

### Generating HTML from wiki files

WiKo also takes any .wiki file in the working directory
and will reformat it to an .html file also using the skeleton.
In the example files you can take a look at the syntax we are using
which is very similar to the one on Wikimedia and Moin-Moin wiki.

Just take a quick look at this [[Sample.wiki]] which has most syntax elements.
It renders into [[Sample.html this html file]].

<!-- [[wikosample-wikicontent.zip Sample WiKo project using wiki content]] -->

### Generating PDF (LaTeX) from wiki files

WiKo can also generate PDF through LaTeX. LaTeX document skeletons are a bit different from html ones:
* In a document skeletons the user must include the generated file using the normal LaTeX facilities: '''\input{file}''' (and not with '''%%<!-- -->(content)s''' as in the html case)
* WiKo will consider document skeleton any .tex file in the working directory that both contains the '''\documentclass''' directive '''and''' its basename does not match with any of the .wiki files.

An example of a working directory:
* document.tex (document skeleton that will be compiled. It contains '''\documentclass''' and '''\input{chapter1}''' )
* chapter1.tex (generated)
* chapter1.wiki (source)

Then WiKo will execute pdflatex and bibtex for the LaTeX skeleton.



<!-- [[wikosample-article.zip Sample WiKo project for a PDF article]] -->

### Generating Blogs

Blog entries can be defined by adding files into the
''blog'' subdirectory of the working directory.
WiKo analyzes such files and generates:
* Blog front page with the newer entries.
* An individual pages for each entry.
* Pages with the entries which contain a given tag.
* An [[http://en.wikipedia.org/wiki/Rss RSS]] file for news syndication.

It requires some page variables to be defined in each entry.
See the sample for details.

The blog mode is currently under heavy development.
We would like to evolve it in two directions:
* Allowing comments
* User definable side bar widgets
* Interacting with [[http://www.blogger.com blogger]] and [[http://www.wordpress.org wordpress]] API's to export and import

<!-- [[wikosample-blog.zip Sample WiKo project for a blog]] -->

### Generating download zones

A download zone is a folder with a set of files you want to list and download.
WiKo generate directory listings which integrates on the web page look and feel.

You should create a file named ''downloadZones.wiko'' on the working directory
just like that:
```python
 {
	'dirs' : [
		("WiKo files", "download/"),
	],
	'blacklist' : [
		"index.html",
		"style.css",
		"img",
	],
	'skeletonFile' : "scheleton.html"
 }
```


''dirs'' is a list of python tuples containing titles and paths for the download zones.
The ''blacklist'' contains the files which should be ignored when generating the file index.
And, ''skeletonFile'' is the html skeleton to be used with such pages.
Be carefull as if you use the same skeleton, relative paths used for some links, images and styles,
might be wrong.


## Other features

### Page dependent code on the skeleton

By using the wiki format you can also use variables to be inserted
on the skeleton.
You should introduce a line like this in the .wiki file.

	{{{
	@variableName: value to use
	}}}

and then using the tag '''%%<!-- -->(variableName)s''' wherever you want to use it on the skeleton.

### Inserting an html table of content

By inserting in a wiki content file the '''%%<!-- -->(toc)s''' tag you can get
in the html ouput a table of content which links to the headings of each section.
Just like this manual.

### Refering bibliography

The wiki format allows referencing [[http://en.wikipedia.org/wiki/Bibtex BibTeX]] entries
with the ''@cite'' directive.
In the LaTeX mode, that has a direct mapping to the ''\cite'' command.
In the HTML mode, a link is created to a web page called ''bibliography.bib.html''
which is an aggregation of every .bib file it founds in the working directory.
The ''@cite'' directive points to the proper entry.

### Access to the wiki source code

If you want to place a link to the wiki source in the skeleton
use the '''%%<!-- -->(wikiSource)s''' tag to get its url.

### Using WiKo with version control system

WiKo increase its potential when you use it in combination of a
[[http://en.wikipedia.org/wiki/Version_control_system version control system]]
such as [[http://subversion.tigris.org/ subversion]].
Subversion allows to write your WiKo based project collaborativelly.
Project members have their own copy of the project in their own computer.
They can modify it locally, confirm the changes remotelly to a central repository,
and update other's changes.
It also provides means for tracing changes and merging versions.

Just an advice, in order to avoid conflicts,
put under the version control just those files that are not generated.

#### Revision and last modification

Subversion allows you to include on the file information on the revision
number and the last modification date and author.

Code: bash
svn propset svn:keywords "Revision Date Author" aFile.wiki


then you can insert in the wiki file text like this:

	{{{
	$Revision$
	$Date$
	$Author$
	}}}
	And subversion will rewrite it on update as:
	{{{
	$Revision: 242$
	$Date: 2002-07-22 21:42:37 -0700 (Mon, 22 Jul 2002)$
	$Author: vokimon$
	}}}

A nice way of using it is placing such tags in @ variables
so that you can place them in a fixed location in the skeleton.

#### Automatic update on commit

If you are using subversion, it is very convenient having
the web updated automatically on every subversion commit.
You will require:

* Having shell access to your server
* Having python installed on your server (most servers have)
* Having rights to use crontab (scheduled tasks)
* A copy of wiko committed into your repository root

Given that:

* ''/var/www'' is where you can place your web files in your web service,
* ''/var/www/myweb'' is where your project is gonna live
* ''svn+ssh://svnuser@mysvnserver.com/home/svn/myproject/web'' is your svn repository

You should issue the following commands on your server:

```bash
cd /var/www/
ssh-keygen       # and then, return, return, return, return...
ssh-copy-id svnuser@mysvnserver.com
svn co svn+ssh://svnuser@mysvnserver.com/home/svn/myproject/web myweb
(crontab -l ; echo '5,15,25,35,45,55 * * * * (cd /var/www/myweb && svn up && ./wiko) 2>&1 | cat > /var/www/myweb/err') | crontab -
```






