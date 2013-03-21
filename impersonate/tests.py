'''
    Tests
    test_data.json contains 4 User accounts.
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
import urllib
import factory
from urlparse import urlsplit
from django.test import TestCase
from django.utils import unittest
from django.test.client import Client
from django.test.utils import override_settings
from django.core.urlresolvers import reverse

try:
    # Django 1.5 check
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
else:
    User = get_user_model()


class UserFactory(factory.Factory):
    FACTORY_FOR = User

    username = ''
    first_name = ''
    last_name = ''
    email = factory.LazyAttribute(
        lambda a: '{0}@test-email.com'.format(a.username).lower()
    )
    is_superuser = False
    is_staff = False

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user


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
            url += '?{}'.format(urllib.urlencode(qwargs))
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

    def test_successsful_impersonation_by_staff(self):
        response = self._impersonate_helper('user3', 'foobar', 4)
        self.assertEqual(self.client.session['_impersonate'].id, 4)
        self.client.get(reverse('impersonate-stop'))
        self.assertEqual(self.client.session.get('_impersonate'), None)
        self.client.logout()

    def test_unsuccessful_impersonation(self):
        response = self._impersonate_helper('user4', 'foobar', 3)
        self.assertEqual(self.client.session.get('_impersonate'), None)
        self.client.logout()

    @override_settings(LOGIN_REDIRECT_URL='/test-redirect/')
    def test_unsuccessful_impersonation_restricted_uri(self):
        response = self._impersonate_helper('user1', 'foobar', 4)
        self.assertEqual(self.client.session['_impersonate'].id, 4)
        response = self.client.get(reverse('impersonate-list'))
        self._redirect_check(response, '/test-redirect/')
        self.client.logout()

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
