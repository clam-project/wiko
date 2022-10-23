# Wiko, the Wiki Compiler

![](wiko/web/wikologo.svg)

By David Garcia and Pau Arumi

* [The original Sourceforge project](https://sourceforge.net/projects/wiko/)

## Description

**We do not recommended to use Wiko in new projects.
This is a quite deprecated zombie project from 2007.
It is kept alive because it is still being used to generate some websites pending to be migrated to modern static generators.**

WiKo is a very simple but powerful python script
which takes files with _wiki_ content in a given directory
and either builds a _web_, a _LaTeX article_ or a _blog_.
It is very recommended to use it in tandem
with a collaborative versioning systems
in order to publish on commit.

Main benefits of using WiKo are:

* An easy and readable wiki like format that generates LaTeX and HTML indistinctly
* You can use your favourite text editor instead web forms to edit content
* You don't need to reformat content to reuse it from the web to a LaTeX article or to a blog.
* You can change the look of your entire site by changing common headers, side bars, footers and styling in a pair of files which are content independent. And still it is an static web site.
* You can put your web site or your article under a versioning system (cvs, svn...) for collaborative elaboration and having a published version that updates on commit.

- [Usage](docs/usage.md)
- [Examples](docs/examples.md)
- [Screenshots](docs/screenshots.md)

## Features

### Common formatting

* Text formating: `'''bold'''`, `''italics''`...
* Hypertext and anchoring: `[[http://lalala.com links]]` and the like
* Lists and enumerations
* Table of content generation for HTML pages
* LaTeX constructs supported on both formats: figures, formulae, bibliography, footnotes...
* Automatic recompilation of some image formats (dia->eps/png, dot->eps/png, eps->pdf...)
* User definable paragraphs types
* Useful constructs for elaboration such as to-do notes and reviewers notes
* Gallery generation

### Blogging

The blog mode takes the wiki files as blog entries and
combines and distributes them in different pages and RSS's
according to attributes you can define for each entry
such as publication date, author, tags...

* a front page with newer entries,
* [RSS](http://en.wikipedia.org/wiki/RSS) file with the last entries
* filtered pages with entries by the same author or with a given tag,
* graphical import tool from Blogger and Wordpress
* objects for the sidebar with archived entries and tags list

## Authors

This script has been developed mainly by ''David Garcia Garzon'' and ''Pau Arumi Albo''.
They developed the script for their own personal use
on their webs, scientific articles and even their thesis.
See at the [WiKo examples page](wiko/web/examples.html).







