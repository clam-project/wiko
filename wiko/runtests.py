#!/usr/bin/env python

import os
import glob
import subprocess
import sys


def runOrDie(command):
    print("Running: \033[33m", command, "\033[0m", file=sys.stderr)
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
    )
    output, _ = process.communicate()
    if process.returncode:
        print("Error running: \033[33m" + command + "\033[0m", file=sys.stderr)
        print("\033[31m" + output.decode("utf8") + "\033[0m", file=sys.stderr)
        sys.exit(-1)


wikoRoot = os.path.abspath(os.path.dirname(__file__))
testSamplesRoot = os.path.join(wikoRoot, "testsamples")

os.chdir(testSamplesRoot)
testCases = glob.glob("*")
for case in testCases:
    print("===== ", case)
    os.chdir(case)
    runOrDie("../../wiko --force")
    os.chdir(testSamplesRoot)

print("==== Changes")
os.chdir(wikoRoot)
subprocess.call("git status testsamples", shell=True)
