==================
django-impersonate
==================
:Info: Simple application to allow superusers to "impersonate" other non-superuser accounts.
:Version: 0.7.0
:Author: Peter Sanchez (http://www.petersanchez.com)


Dependencies
============

* It was written for Python 2.6.5+ and Django 1.4+
* Python 3.3+ is supported (Django 1.5+ required for Python 3.3+)
* It depends on your project using the django.contrib.session framework.

**NOTE:** If you need to use this with Django older than 1.4, please use version django-impersonate == 0.5.3


Installation
============

PIP::

    pip install django-impersonate

Basic Manual Install::

    $ python setup.py build
    $ sudo python setup.py install

Alternative Install (Manually):

Place impersonate directory in your Python path. Either in your Python installs site-packages directory or set your $PYTHONPATH environment variable to include a directory where the webutils directory lives.


Use
===

#. Add 'impersonate' to your INSTALLED_APPS

#. Add 'impersonate.middleware.ImpersonateMiddleware' to your MIDDLEWARE_CLASSES

#. Add 'impersonate.urls' somewhere in your url structure. Example::

    urlpatterns = patterns('',
        url(r'^admin/', include(admin.site.urls)),
        url(r'^impersonate/', include('impersonate.urls')),
        ... (all your other urls here) ...
    )


Functionality
=============

**You can now impersonate another user by hitting the following path:**

    /impersonate/<user-id>/

Replace <user-id> with the user id of the user you want to impersonate.

While in impersonation "mode" the request.user object will have an 
"is_impersonate" attribute set to True. So if you wanted to check in your 
templates or view, you just do something like...

    {% if user.is_impersonate %} .... {% endif %}

The original user is available as "request.impersonator".

    {{ request.user }} ({{ request.impersonator }})

You can reference this URL with reverse() or the {% url %} template tag 
as 'impersonate-start'


**To remove the impersonation, hit the following path:**

    /impersonate/stop/

You can reference this URL with reverse() or the {% url %} template tag 
as 'impersonate-stop'


**To list all users you can go to:**

    /impersonate/list/

This will render the template 'impersonate/list_users.html' and will pass 
the following in the context:

* users - queryset of all users
* paginator - Django Paginator instance
* page - Current page of objects (from Paginator) 
* page_number - Current page number, defaults to 1

You can reference this URL with reverse() or the {% url %} template tag
as 'impersonate-list'


**To search all users you can go to:**

    /impersonate/search/

This will render the template 'impersonate/search_users.html' and will pass 
the following in the context:

* users - queryset of all users
* paginator - Django Paginator instance
* page - Current page of objects (from Paginator) 
* page_number - Current page number, defaults to 1
* query - The search query that was entered

The view will expect a GET request and look for the 'q' variable being passed. 
If present, it will search the user entries with the value of 'q'. The fields 
searched are:

User.username, User.first_name, User.last_name, User.email

You can reference this URL with reverse() or the {% url %} template tag
as 'impersonate-search'


**To allow some users to impersonate other users**

You can optionally allow only some non-superuser and non-staff users to impersonate by adding a **IMPERSONATE_CUSTOM_ALLOW** setting. Create a function that takes a request object, and based on your rules, returns True if the user is allowed to impersonate or not.

**To limit what users a user can impersonate**

By, optionally, setting the **IMPERSONATE_CUSTOM_USER_QUERYSET** you can control what users can be impersonated. It takes a request object of the user, and returns a QuerySet of users. This is used when searching for users to impersonate, when listing what users to impersonate, and when trying to start impersonation.


Settings
========

The following settings are available for django-impersonate:


    IMPERSONATE_REDIRECT_URL

This is the URL you want to be redirected to after you have chosen to 
impersonate another user. If this is not present it will check for 
the LOGIN_REDIRECT_URL setting and fall back to '/' if neither is 
present. Value should be a string containing the redirect path.


    IMPERSONATE_PAGINATE_COUNT

This is the number of users to paginate by when using the list or 
search views. This defaults to 20. Value should be an integer.


    IMPERSONATE_REQUIRE_SUPERUSER

If this is set to True, then only users who have 'is_superuser' set 
to True will be allowed to impersonate other users. Default is False. 
If False, then any 'is_staff' user will be able to impersonate other 
users.

**Note:** Regardless of this setting, a 'is_staff' user will **not** be 
allowed to impersonate a 'is_superuser' user.

Value should be a boolean (True/False)

If the IMPERSONATE_CUSTOM_ALLOW is set, then that custom function is used, and
this setting is ignored.


    IMPERSONATE_URI_EXCLUSIONS

Set to a list/tuple of url patterns that, if matched, user 
impersonation is not completed. It defaults to:

(r'^admin/',)

If you do not want to use even the default exclusions then set 
the setting to an emply list/tuple.


    IMPERSONATE_CUSTOM_USER_QUERYSET

A string that represents a function (e.g. 'module.submodule.mod.function_name')
that allows more fine grained control over what users a user can impersonate.
It takes one argument, the request object, and should return a QuerySet. Only
the users in this queryset can be impersonated.

This function will not be called when the request has an unauthorised users,
and will only be called when the user is allowed to impersonate (cf.
IMPERSONATE_REQUIRE_SUPERUSER and IMPERSONATE_CUSTOM_ALLOW )

Regardless of what this function returns, a user cannot impersonate a
superuser, even if there are superusers in the returned QuerySet.

It is optional, and if it is not present, the user can impersonate any user
(i.e. the default is User.objects.all())


    IMPERSONATE_CUSTOM_ALLOW

A string that represents a function (e.g. 'module.submodule.mod.function_name')
that allows more fine grained control over who can use the impersonation. It
takes one argument, the request object, and should return True to allow
impesonation. Regardless of this setting, the user must be logged in to
impersonate. If this setting is used, IMPERSONATE_REQUIRE_SUPERUSER is ignored.

It is optional, and if it is not present, the previous rules about superuser
and IMPERSONATE_REQUIRE_SUPERUSER apply.


    IMPERSONATE_REDIRECT_FIELD_NAME

A string that represents the name of a request (GET) parameter which contains
the URL to redirect to after impersonating a user. This can be used to redirect
to a custom page after impersonating a user. Example:

    # in settings.py
    IMPERSONATE_REDIRECT_FIELD_NAME = 'next'
    
    # in your view
    <a href="{% url 'impersonate-list' %}?next=/some/url/">switch user</a>

To return always to the current page after impersonating a user, use request.path: 

    <a href="{% url 'impersonate-list' %}?next={{request.path}}">switch user</a>


Testing
=======

You need factory_boy installed for tests to run. To install, use:

    $ pip install factory_boy

**Note:** This currently not required for Python 3.3. For more info on factory_boy, see: https://github.com/dnerdy/factory_boy

From the repo checkout, ensure you have Django in your PYTHONPATH and  run:

    $ python runtests.py

To get test coverage, use::

    $ coverate run --branch runtests.py
    $ coverage html  <- Pretty HTML files for you
    $ coverage report -m  <- Ascii report

If you're bored and want to test all the supported environments, you'll need tox.::

    $ pip install tox
    $ tox

And you should see::

    py3.3-django1.5: commands succeeded
    py2.7-django1.5: commands succeeded
    py2.6-django1.5: commands succeeded
    py2.7-django1.4: commands succeeded
    py2.6-django1.4: commands succeeded
    congratulations :)


Copyright & Warranty
====================
All documentation, libraries, and sample code are 
Copyright 2011 Peter Sanchez <petersanchez@gmail.com>. The library and 
sample code are made available to you under the terms of the BSD license 
which is contained in the included file, BSD-LICENSE.
