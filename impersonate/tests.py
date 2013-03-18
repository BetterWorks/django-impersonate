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
from django.test import TestCase
from django.utils import unittest
from django.test.client import Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

try:
    # Django 1.5 check
    from django.contrib.auth import get_user_model
except ImportError:
    get_user_model = None


class TestImpersonation(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()
        self.user_model = get_user_model() if get_user_model else User

    def test_user_count(self):
        self.assertEqual(self.user_model.objects.count(), 4)

    def test_dont_impersonate_superuser(self):
        self.client.login(username='user1', password='foobar')
        self.client.get(reverse('impersonate-start', args=[2]))
        self.assertEqual(self.client.session.get('_impersonate'), None)
        self.client.logout()

    def test_successful_impersonation(self):
        self.client.login(username='user1', password='foobar')
        self.client.get(reverse('impersonate-start', args=[4]))
        self.assertEqual(self.client.session['_impersonate'].id, 4)
        self.client.get(reverse('impersonate-stop'))
        self.assertEqual(self.client.session.get('_impersonate'), None)
        self.client.logout()
