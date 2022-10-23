import re


def extractVars(content, variables=None, varre=re.compile(r"^@([^:]*): (.+)")):
    """
    Extracts variable specification in the form "@varname: value\\n" from text content.
    >>> extractVars("normal content\\nmore content")
    ('normal content\\nmore content', {})
    >>> extractVars("normal content\\nmore content", dict(var="value"))
    ('normal content\\nmore content', {'var': 'value'})
    >>> extractVars("@var: value")
    ('', {'var': 'value'})
    >>> extractVars("@var: multiple word value")
    ('', {'var': 'multiple word value'})
    >>> extractVars("@var: value\\n@var2: value2")
    ('', {'var': 'value', 'var2': 'value2'})
    >>> extractVars("@var: value\\nmore content")
    ('more content', {'var': 'value'})
    """
    if variables is None:
        variables = dict()
    cleanContent = []
    for line in content.splitlines():
        match = varre.match(line)
        if match is None:
            cleanContent.append(line)
        else:
            variables.update([match.groups()])
    print(variables)
    return "\n".join(cleanContent), variables


def _test():
    import doctest

    failures, total = doctest.testmod()
    if not failures:
        print("\033[32m%s tests passed\033[0m" % total)


if __name__ == "__main__":
    _test()
