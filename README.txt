django-impersonate
------------------

Simple application to allow superusers to "impersonate" other 
non-superuser accounts.


Dependencies
------------

It was written for Python 2.4+ and Django 1.2.4 but it should 
work just fine with Django 1.1+

It depends on your project using the django.contrib.session framework.


Install
-------

PIP:

pip install django-impersonate


Basic Manual Install:

  $ python setup.py build
  $ sudo python setup.py install

Alternative Install (Manually):

Place impersonate directory in your Python path. Either in your Python 
installs site-packages directory or set your $PYTHONPATH environment 
variable to include a directory where the webutils directory lives.


Use
---
1) Add 'impersonate' to your INSTALLED_APPS

2) Add 'impersonate.middleware.ImpersonateMiddleware' to your MIDDLEWARE_CLASSES

3) Add 'impersonate.urls' somewhere in your url structure. Example:

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^impersonate/', include('impersonate.urls')),

    ... (all your other urls here) ...
)


** HOW TO USE **

== You can now impersonate another user by hitting the following path:

/impersonate/<user-id>/

Replace <user-id> with the user id of the user you want to impersonate.

While in impersonation "mode" the request.user object will have an 
"is_impersonate" attribute set to True. So if you wanted to check in your 
templates or view, you just do something like...

{% if user._impersonate %} .... {% endif %}

You can reference this URL with reverse() or the {% url %} template tag 
as 'impersonate-start'


== To remove the impersonation, hit the following path:

/impersonate/stop/

You can reference this URL with reverse() or the {% url %} template tag 
as 'impersonate-stop'


== To list all users you can go to:

/impersonate/list/

This will render the template 'impersonate/list_users.html' and will pass 
the following in the context:

* users - queryset of all users
* paginator - Django Paginator instance
* page - Current page of objects (from Paginator) 
* page_number - Current page number, defaults to 1

You can reference this URL with reverse() or the {% url %} template tag
as 'impersonate-list'


== To search all users you can go to:

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


Settings
--------

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

Note: Regardless of this setting, a 'is_staff' user will *not* be 
allowed to impersonate a 'is_superuser' user.

Value should be a boolean (True/False)


Copyright & Warranty
--------------------
All documentation, libraries, and sample code are 
Copyright 2011 Peter Sanchez <petersanchez@gmail.com>. The library and 
sample code are made available to you under the terms of the BSD license 
which is contained in the included file, BSD-LICENSE.
