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

You can now impersonate another user by hitting the following path:

/impersonate/<user-id>/

Replace <user-id> with the user id of the user you want to impersonate.

While in impersonation "mode" the request.user object will have an 
"_impersonate" attribute set to True. So if you wanted to check in your 
templates or view, you just do something like...

{% if user._impersonate %} .... {% endif %}

You can reference this URL with reverse() or the {% url %} template tag 
as 'impersonate-start'


To remove the impersonation, hit the following path:

/impersonate/stop/

You can reference this URL with reverse() or the {% url %} template tag 
as 'impersonate-stop'



Copyright & Warranty
--------------------
All documentation, libraries, and sample code are 
Copyright 2011 Peter Sanchez <petersanchez@gmail.com>. The library and 
sample code are made available to you under the terms of the BSD license 
which is contained in the included file, BSD-LICENSE.
