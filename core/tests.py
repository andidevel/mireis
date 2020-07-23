from django.test import TestCase
from django.urls import reverse
from core.models import (
    User,
    Account,
    Transaction
)
from core.lib import utils


class ValidateTest(TestCase):

    def test_email_validate(self):
        emails_to_test = [
            ('test_example@test.com', True),
            ('test.example@t.io', True),
            ('testexample.t@test.com.br', True),
            ('test_example', False),
            ('test_example@', False),
            ('test_example@test.com.', False),
            ('test_example@test.', False),
        ]
        for email in emails_to_test:
            print('Checking:', email)
            self.assertEqual(utils.email_validate(email[0]), email[1])


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
