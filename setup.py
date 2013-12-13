from distutils.core import setup

from setuptools import find_packages

from registration_api import __version__


setup(name='django-registration-rest-framework',
      version=__version__,
      packages=find_packages(),
      requires=['djangorestframework'],
      test_suite='tests.runtests.runtests',
      install_requires=['djangorestframework==2.3.10'],
      tests_require=[
          'mock==1.0.1',
          'Django>=1.5',
          ],
      url='https://github.com/tucarga/django-registration-rest-framework',
      author='Alejandro Varas',
      author_email='alej0varas@gmail.com',
      keywords='django registration rest framework',
      description=('Clone of Django Resgistration flow for Django Rest '
                   'Framework',),
      license='GPL',
      classifiers=[
          'Development Status :: 1 - Planning',
          'Intended Audience :: Developers',
          'Framework :: Django',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python',
          'Natural Language :: English',
          ('License :: OSI Approved :: '
           'GNU General Public License v3 or later (GPLv3+)'),
          'Topic :: Software Development :: Libraries',
          ],
      )
