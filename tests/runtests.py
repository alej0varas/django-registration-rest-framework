import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

test_dir = os.path.dirname(__file__)
sys.path.insert(0, test_dir)

from django.test.runner import DiscoverRunner


def runtests():

    if sys.argv[0] == 'runtests.py' and len(sys.argv) == 2:
        suite = ['registration_api.tests.' + sys.argv[1]]
    else:
        suite = []

    test_runner = DiscoverRunner()
    failures = test_runner.run_tests(suite, verbosity=1, interactive=True)

    sys.exit(failures)


if __name__ == '__main__':
    runtests()
