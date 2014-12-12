====================================
 Django Registration Rest Framework
====================================
Clone of Django Resgistration flow for Django Rest Framework

Needs 'django.contrib.sites' and an email backend

Based on
========

StackOverflow answer http://stackoverflow.com/a/19337404

and

django-registration https://django-registration.readthedocs.org/

Install
=======

.. code-block::

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

    # This setting is mandatory
    REGISTRATION_API_ACTIVATION_SUCCESS_URL = '/'

urls.py
-------

.. code-block:: python

    urlpatterns = patterns(
    ...
    url(r'^accounts_api/', include('registration_api.urls')),
    ...
    )

Front-end
---------
From your front-end or mobile application send a post to the register
url 'accounts_api/register/'. The fields depends on your `AUTH_USER_MODEL` but should be
something like

.. code-block:: json

  [{"username": "john", "email": "john@example.com", "password": "verylongpassword"}]

This will trigger an email to the addess specified by the user. When
the user follows the link the account is activated.


Test
====
.. code-block::

    $ python tests/runtests.py [TestsCase[.test_method]]

or

.. code-block::

    $ python setup.py test
