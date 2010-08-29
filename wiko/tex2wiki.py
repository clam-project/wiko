#!/usr/bin/python
"""
A helper script to convert some common constructs in LaTeX input files into
the equivalent wiko syntax.
It is provided by convenience but don't rely on this script for full
automated conversions because:
* It just converts some LaTeX constructs
* Analysis is line per line, multiline constructs may get you into trouble
* It is not recursive (embeded expressions), though multiple pass might do
"""

import re, sys

substitutions = [
	(r"{\\em\s([^{^}]*?)}", r"''\1''"),
	(r"{\\bf\s([^{^}]*?)}", r"'''\1'''"),
	(r"\\textbf{([^{^}]*?)}", r"'''\1'''"),
	(r"\\textit{([^{^}]*?)}", r"''\1''"),
	(r"\\textbf{([^{^}]*?)}", r"'''\1'''"),
	(r"\\cite{([^}^,]*),([^}^,]*),([^}^,]*),([^}^,]*,([^}^,]*)),([^}^,]*)}", r"@cite:\1 @cite:\2 @cite:\3 @cite:\4 @cite:\5 @cite:\6"),
	(r"\\cite{([^}^,]*),([^}^,]*),([^}^,]*),([^}^,]*),([^}^,]*)}", r"@cite:\1 @cite:\2 @cite:\3 @cite:\4 @cite:\5"),
	(r"\\cite{([^}^,]*),([^}^,]*),([^}^,]*),([^}^,]*)}", r"@cite:\1 @cite:\2 @cite:\3 @cite:\4"),
	(r"\\cite{([^}^,]*),([^}^,]*),([^}^,]*)}", r"@cite:\1 @cite:\2 @cite:\3"),
	(r"\\cite{([^}^,]*),([^}^,]*)}", r"@cite:\1 @cite:\2"),
	(r"\\cite{([^}]*)}", r"@cite:\1"),
]
substitutions = [ (re.compile(pattern), substitution)
	for pattern, substitution in substitutions ]


input = file(sys.argv[1]) if len(sys.argv)>1 else sys.stdin

output = []
for line in input :
	for pattern, substitution in substitutions :
		line = pattern.sub(substitution, line)
	output.append(line)

print "".join(output)


