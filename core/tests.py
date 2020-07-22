from django.test import TestCase
from django.urls import reverse
from core.models import (
    User,
    Account,
    Transaction
)
from core.lib import utils

# Create your tests here.

class LoginTest(TestCase):

    def setUp(self):
        self.test_username = 'usertest@test.app'
        self.test_password = 'test_password'
        passw_digest = utils.password_digest(self.test_password)
        User.objects.create(username=self.test_username, password=passw_digest)
    
    def test_login_action_success(self):
        response = self.client.post(reverse('core:login'), {'username': self.test_username, 'password': self.test_password})
        self.assertRedirects(response, reverse('core:journal'))
    
    def test_login_action_fail(self):
        response = self.client.post(reverse('core:login'), {'username': 'User does not exist', 'password': self.test_password})
        self.assertRedirects(response, reverse('core:index'))
