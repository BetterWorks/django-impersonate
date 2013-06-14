'''
    Tests
    Factory creates 4 User accounts.
    user1:
        id = 1
        is_superuser = True
        is_staff = True
    user2:
        id = 2
        is_superuser = True
        is_staff = True
    user3:
        id = 3
        is_superuser = False
        is_staff = True
    user4:
        id = 4
        is_superuser = False
        is_staff = False
'''
from django.utils import six
from django.test import TestCase
from django.utils import unittest
from django.dispatch import receiver
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django.test.client import Client, RequestFactory
from django.conf.urls.defaults import patterns, url, include
from .signals import session_begin, session_end

try:
    # Python 3
    from urllib.parse import urlencode, urlsplit
except ImportError:
    import factory
    from urllib import urlencode
    from urlparse import urlsplit

try:
    # Django 1.5 check
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
else:
    User = get_user_model()


urlpatterns = patterns('',
    url(r'^test-view/$',
        'impersonate.tests.test_view',
        name='impersonate-test'),
    ('^', include('impersonate.urls')),
)


def test_view(request):
    return HttpResponse('OK {0}'.format(request.user))


def test_allow(request):
    ''' Used via the IMPERSONATE_CUSTOM_ALLOW setting.
        Simple check for the user to be auth'd and a staff member.
    '''
    return request.user.is_authenticated() and request.user.is_staff


def test_allow2(request):
    ''' Used via the IMPERSONATE_CUSTOM_ALLOW setting.
        Always return False
    '''
    return False


def test_qs(request):
    ''' Used via the IMPERSONATE_CUSTOM_USER_QUERYSET setting.
        Simple function to return all users.
    '''
    return User.objects.all()


if six.PY3:
    # Temporary until factory_boy gets Py3k support
    class UserFactory(object):
        @staticmethod
        def create(**kwargs):
            password = kwargs.pop('password', None)
            kwargs['email'] = \
                '{0}@test-email.com'.format(kwargs['username']).lower()
            user = User.objects.create(**kwargs)
            if password:
                user.set_password(password)
                user.save()
            return user
else:
    class UserFactory(factory.Factory):
        FACTORY_FOR = User

        email = factory.LazyAttribute(
            lambda a: '{0}@test-email.com'.format(a.username).lower()
        )

        @classmethod
        def _prepare(cls, create, **kwargs):
            password = kwargs.pop('password', None)
            user = super(UserFactory, cls)._prepare(create, **kwargs)
            if password:
                user.set_password(password)
                if create:
                    user.save()
            return user


class TestMiddleware(TestCase):
    def setUp(self):
        from impersonate.middleware import ImpersonateMiddleware

        self.superuser = UserFactory.create(
            username='superuser',
            is_superuser=True,
        )
        self.user = UserFactory.create(username='regular')
        self.factory = RequestFactory()
        self.middleware = ImpersonateMiddleware()

    def test_impersonated_request(self):
        request = self.factory.get('/')
        request.user = self.superuser
        request.session = {
            '_impersonate': self.user
        }
        self.middleware.process_request(request)

        # Check request.user and request.user.real_user
        self.assertEqual(request.user, self.user)
        self.assertEqual(request.impersonator, self.superuser)
        self.assertTrue(request.user.is_impersonate)


class TestImpersonation(TestCase):

    def setUp(self):
        self.client = Client()
        user_data = (
            ('John', 'Smith', True, True),
            ('John', 'Doe', True, True),
            ('', '', False, True),
            ('', '', False, False),
        )
        for cnt, data in enumerate(user_data):
            UserFactory.create(**{
                'username': 'user{0}'.format(cnt + 1),
                'first_name': data[0],
                'last_name': data[1],
                'is_superuser': data[2],
                'is_staff': data[3],
                'password': 'foobar',
            })

    def _impersonate_helper(self, user, passwd,
                            user_id_to_impersonate, qwargs={}):
        self.client.login(username=user, password=passwd)
        url = reverse('impersonate-start', args=[user_id_to_impersonate])
        if qwargs:
            url += '?{0}'.format(urlencode(qwargs))
        return self.client.get(url)

    def _redirect_check(self, response, new_path):
        ''' Needed because assertRedirect fails because it checks
            that the new path is able to be fetched. That's going
            to raise a TemplateDoesNotExist exception (usually).
            This is just a work around.
        '''
        url = response['Location']
        scheme, netloc, path, query, fragment = urlsplit(url)
        self.assertEqual(path, new_path)

    def test_user_count(self):
        self.assertEqual(User.objects.count(), 4)

    def test_dont_impersonate_superuser(self):
        response = self._impersonate_helper('user1', 'foobar', 2)
        self.assertEqual(self.client.session.get('_impersonate'), None)
        self.client.logout()

        # Try again with normal staff user
        response = self._impersonate_helper('user3', 'foobar', 2)
        self.assertEqual(self.client.session.get('_impersonate'), None)
        self.client.logout()

    def test_successful_impersonation(self):
        response = self._impersonate_helper('user1', 'foobar', 4)
        self.assertEqual(self.client.session['_impersonate'].id, 4)
        self.client.get(reverse('impersonate-stop'))
        self.assertEqual(self.client.session.get('_impersonate'), None)
        self.client.logout()

    def test_successful_impersonation_signals(self):

        # flags used to determine that signals have been sent
        self.session_begin_fired = False
        self.session_end_fired = False

        def on_session_begin(sender, **kwargs):
            self.session_begin_fired = True
            self.assertIsNone(sender)
            self.assertIsNotNone(kwargs.pop('request', None))
            self.assertEqual(kwargs.pop('impersonator').username, 'user1')
            self.assertEqual(kwargs.pop('impersonating').username, 'user4')

        def on_session_end(sender, **kwargs):
            self.session_end_fired = True
            self.assertIsNone(sender)
            self.assertIsNotNone(kwargs.pop('request', None))
            self.assertEqual(kwargs.pop('impersonator').username, 'user1')
            self.assertEqual(kwargs.pop('impersonating').username, 'user4')

        self.assertFalse(self.session_begin_fired)
        self.assertFalse(self.session_end_fired)
        session_begin.connect(on_session_begin)
        session_end.connect(on_session_end)

        # start the impersonation and check that the _begin signal is sent
        response = self._impersonate_helper('user1', 'foobar', 4)
        self.assertEqual(self.client.session['_impersonate'].id, 4)
        self.assertTrue(self.session_begin_fired)
        self.assertFalse(self.session_end_fired)

        # now stop the impersonation and check that the _end signal is sent
        self.client.get(reverse('impersonate-stop'))
        self.assertEqual(self.client.session.get('_impersonate'), None)
        self.assertTrue(self.session_end_fired)
        self.client.logout()
        session_begin.disconnect(on_session_begin)
        session_end.disconnect(on_session_end)

    def test_successsful_impersonation_by_staff(self):
        response = self._impersonate_helper('user3', 'foobar', 4)
        self.assertEqual(self.client.session['_impersonate'].id, 4)
        self.client.get(reverse('impersonate-stop'))
        self.assertEqual(self.client.session.get('_impersonate'), None)
        self.client.logout()

    @override_settings(IMPERSONATE_REQUIRE_SUPERUSER=True)
    def test_unsuccessful_impersonation_by_staff(self):
        response = self._impersonate_helper('user3', 'foobar', 4)
        self.assertEqual(self.client.session.get('_impersonate'), None)
        self.client.logout()

    def test_unsuccessful_impersonation(self):
        response = self._impersonate_helper('user4', 'foobar', 3)
        self.assertEqual(self.client.session.get('_impersonate'), None)
        self.client.logout()

    def test_unsuccessful_impersonation_restricted_uri(self):
        response = self._impersonate_helper('user1', 'foobar', 4)
        self.assertEqual(self.client.session['_impersonate'].id, 4)

        # Don't allow impersonated users to use impersonate views
        with self.settings(LOGIN_REDIRECT_URL='/test-redirect/'):
            response = self.client.get(reverse('impersonate-list'))
            self._redirect_check(response, '/test-redirect/')

        # Don't allow impersonated users to use restricted URI's
        with self.settings(IMPERSONATE_URI_EXCLUSIONS=r'^test-view/'):
            response = self.client.get(reverse('impersonate-test'))
            self.assertEqual(('user1' in str(response.content)), True) # !user4

        self.client.logout()

    def test_unsuccessful_request_unauth_user(self):
        response = self.client.get(reverse('impersonate-list'))
        self._redirect_check(response, '/accounts/login/')

    def test_successful_impersonation_redirect_url(self):
        with self.settings(IMPERSONATE_REDIRECT_URL='/test-redirect/'):
            response = self._impersonate_helper('user1', 'foobar', 4)
            self.assertEqual(self.client.session['_impersonate'].id, 4)
            self._redirect_check(response, '/test-redirect/')
            self.client.get(reverse('impersonate-stop'))
            self.assertEqual(self.client.session.get('_impersonate'), None)
            self.client.logout()

        with self.settings(LOGIN_REDIRECT_URL='/test-redirect-2/'):
            response = self._impersonate_helper('user1', 'foobar', 4)
            self.assertEqual(self.client.session['_impersonate'].id, 4)
            self._redirect_check(response, '/test-redirect-2/')
            self.client.get(reverse('impersonate-stop'))
            self.assertEqual(self.client.session.get('_impersonate'), None)
            self.client.logout()

        with self.settings(IMPERSONATE_REDIRECT_FIELD_NAME='next'):
            response = self._impersonate_helper(
                'user1',
                'foobar',
                4,
                {'next': '/test-next/'},
            )
            self.assertEqual(self.client.session['_impersonate'].id, 4)
            self._redirect_check(response, '/test-next/')
            self.client.get(reverse('impersonate-stop'))
            self.assertEqual(self.client.session.get('_impersonate'), None)
            self.client.logout()

    def test_user_listing_and_pagination(self):
        self.client.login(username='user1', password='foobar')
        response = self.client.get(reverse('impersonate-list'))
        self.assertEqual(response.context['users'].count(), 4)

        with self.settings(IMPERSONATE_PAGINATE_COUNT=2):
            response = self.client.get(reverse('impersonate-list'))
            self.assertEqual(response.context['paginator'].num_pages, 2)

        # Out of range page number
        response = self.client.get(reverse('impersonate-list'), {'page': 10})
        self.assertEqual(response.context['page_number'], 10)
        self.assertEqual(response.context['page'], None)

        # Invalid integer
        response = self.client.get(reverse('impersonate-list'), {'page': 'no'})
        self.assertEqual(response.context['page_number'], 1)
        self.assertEqual(len(response.context['page'].object_list), 4)

        self.client.logout()

    def test_user_search_and_pagination(self):
        self.client.login(username='user1', password='foobar')
        response = self.client.get(
            reverse('impersonate-search'),
            {'q': 'john'},
        )
        self.assertEqual(response.context['users'].count(), 2)

        response = self.client.get(
            reverse('impersonate-search'),
            {'q': 'doe'},
        )
        self.assertEqual(response.context['users'].count(), 1)

        response = self.client.get(
            reverse('impersonate-search'),
            {'q': 'noresultsfound'},
        )
        self.assertEqual(response.context['users'].count(), 0)

        with self.settings(IMPERSONATE_PAGINATE_COUNT=2):
            response = self.client.get(
                reverse('impersonate-search'),
                {'q': 'test-email'},
            )
            self.assertEqual(response.context['paginator'].num_pages, 2)
            self.assertEqual(response.context['users'].count(), 4)
        self.client.logout()

    @override_settings(IMPERSONATE_REDIRECT_FIELD_NAME='next')
    def test_redirect_field_name(self):
        self.client.login(username='user1', password='foobar')
        response = self.client.get(reverse('impersonate-list'))
        self.assertEqual(response.context['redirect'], '')

        # Add redirect value to query
        response = self.client.get(
            reverse('impersonate-list'),
            {'next': '/test/'},
        )
        self.assertEqual(response.context['redirect'], '?next=/test/')
        self.client.logout()

    @override_settings(IMPERSONATE_CUSTOM_ALLOW='impersonate.tests.test_allow')
    def test_custom_user_allow_function(self):
        self.client.login(username='user1', password='foobar')
        response = self.client.get(reverse('impersonate-list'))
        self.assertEqual(response.context['users'].count(), 4)
        self.client.logout()

    def test_custom_user_allow_function_false(self):
        ''' Edge case test.
        '''
        response = self._impersonate_helper('user1', 'foobar', 4)
        with self.settings(
                IMPERSONATE_CUSTOM_ALLOW='impersonate.tests.test_allow2'):
            response = self.client.get(reverse('impersonate-test'))
            self.assertEqual(('user1' in str(response.content)), True) # !user4

    @override_settings(
        IMPERSONATE_CUSTOM_USER_QUERYSET='impersonate.tests.test_qs')
    def test_custom_user_queryset_function(self):
        self.client.login(username='user1', password='foobar')
        response = self.client.get(reverse('impersonate-list'))
        self.assertEqual(response.context['users'].count(), 4)
        self.client.logout()
