#!/usr/bin/python

import glob, os, sys

# list of (from, to, list-of-commands-templates) tuples
# Ubuntu dependencies:
#  inkscape (inkscape) for svg to pdf/png conversion
#  dia (dia | dia-gnome) for dia to eps/png conversion
#  dot (graphviz) for dot to eps/png conversion
#  epstopdf (texlive-extra-utils) for eps to pdf conversion
converters = [
	(".dia", ".eps", [
		"dia -e '%(target)s' -t eps-builtin '%(source)s'",
		]),
	(".dia", ".png", [
		"dia -e '%(target)s' -t png '%(source)s'",
		]),
	(".dot", ".png", [
		"dot -Tpng '%(source)s' -o '%(target)s'",
		"dot -Timap '%(source)s' -o '%(basename)s.imap'",
		]),
	(".dot", ".eps", [
		"dot -Tps '%(source)s' -o '%(target)s'",
		]),
	(".eps", ".pdf", [
		"epstopdf '%(source)s' -o='%(target)s'",
		]),
	(".svg", ".pdf", [
		"inkscape '%(source)s' --without-gui --export-pdf='%(target)s'",
		]),
	(".svg", ".eps", [
		"inkscape '%(source)s' --without-gui --export-eps='%(target)s'",
		]),
	(".svg", ".png", [
		"inkscape '%(source)s' --without-gui --export-png='%(target)s'",
		]),
]

def needsRebuild(target, source, forceRebuild=False) :
	if forceRebuild: return True
	if not os.path.exists(target) : return True
	if os.path.getmtime(target)<os.path.getmtime(source): return True
	return False

def run(command, verbose=False) :
	if verbose : print "\033[1;34m:: %s\033[0m" % command
	return not os.system(command)
def norun(command, verbose=False) :
	if verbose: print "\033[33mXX %s\033[0m" % command
	return True
def phase(name) :
	print "\033[32m== %s\033[0m" % name

def main() :
	if "-h" in sys.argv or "--help" in sys.argv :
		print >> sys.stderr, "Usage: %s [-f|--force] [-v|--verbose] [-h|--help]"
		print >> sys.stderr, "Options:"
		print >> sys.stderr, "\t--force    Forces regeneration"
		print >> sys.stderr, "\t--verbose  Prints executed commands and reports uptodate images"
		print >> sys.stderr, "\t--help     Prints this help"
		exit(0)

	forceRebuild = "-f" in sys.argv
	verbose = "-v" in sys.argv

	for fromSuffix, toSuffix, commands in converters :
		sources = glob.glob("*"+fromSuffix)
		for source in sources :
			basename = os.path.splitext(source)[0]
			target = basename + toSuffix
			if not needsRebuild(target, source, forceRebuild) :
				if verbose : phase(target + " is uptodate")
				continue
			phase("Converting %s (%s -> %s)" % (source, fromSuffix, toSuffix) )
			vars = {}
			vars.update(
				source=source,
				target=target,
				basename=basename,
				fromSuffix=fromSuffix,
				toSuffix=toSuffix,
				)
			for command in commands :
				if run(command % vars, verbose) : continue
				print >> sys.stderr, "\033[31mCommand failed!\033[0m"
				break

if __name__=="__main__" :
	main()


