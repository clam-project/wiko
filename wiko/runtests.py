#!/usr/bin/env python

import os
import glob
import subprocess
import sys

def runOrDie(command) :
	print >> sys.stderr,"Running: \033[33m", command, "\033[0m"
	process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
	output, _ = process.communicate()
	if process.returncode :
		print >> sys.stderr,"Error running: \033[33m" + command + "\033[0m"
		print >> sys.stderr, "\033[31m" + output + "\033[0m"
		sys.exit(-1)

wikoRoot = os.path.abspath(os.path.dirname(__file__))
testSamplesRoot = os.path.join(wikoRoot,"testsamples")

os.chdir(testSamplesRoot)
testCases = glob.glob("*")
for case in testCases :
	print "===== ", case
	os.chdir(case)
	runOrDie("../../wiko --force")
	os.chdir(testSamplesRoot)

print "==== Changes"
os.chdir(wikoRoot)
subprocess.call("svn stat testsamples", shell=True)


