====================================
 Django Registration Rest Framework
====================================
Clone of Django Resgistration flow for Django Rest Framework

Based on
========

StackOverflow answer http://stackoverflow.com/a/19337404

and

django-registration https://django-registration.readthedocs.org/

Install
=======
::

    $ git clone git@github.com:tucarga/django-registration-rest-framework.git

    $ pip install -e django-registration-rest-framework

Usage
=====

settings.py
-----------

.. code-block:: python

    INSTALLED_APPS =
    ...
    'registration_api',
    ...

urls.py

.. code-block:: python

    urlpatterns += patterns(
    '',
    include('^registration_api/', include('registration_api.urls'))
    )


Test
====
::

    $ python tests/runtests.py [TestsCase[.test_method]]

or::

    $ python setup.py test
