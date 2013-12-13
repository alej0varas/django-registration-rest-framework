version = (0, 1, 0)


def get_version():
    """returns a pep compliant version number"""
    return '.'.join(str(i) for i in version)

__version__ = get_version()
