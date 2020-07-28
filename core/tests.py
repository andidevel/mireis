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
        print('Testing e-mail validate:')
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

class RegisterTest(TestCase):

    def setUp(self):
        self.test_username = 'usertest@test.app'
        self.test_password = 'test_password'
        passw_digest = utils.password_digest(self.test_password)
        User.objects.create(username=self.test_username, password=passw_digest)

    def test_register_success(self):
        response = self.client.post(reverse('core:register'),{
            'username': 'new.user@example.com',
            'password': 'secret-1234',
            'password_again': 'secret-1234'
        })
        self.assertRedirects(response, reverse('core:journal'))
    
    def test_register_fail_user_exist(self):
        response = self.client.post(reverse('core:register'),{
            'username': self.test_username,
            'password': 'secret-1234',
            'password_again': 'secret-1234'
        })
        self.assertRedirects(response, reverse('core:register'))

    def test_register_fail_invalid_email(self):
        response = self.client.post(reverse('core:register'),{
            'username': 'test_example@',
            'password': 'secret-1234',
            'password_again': 'secret-1234'
        })
        self.assertRedirects(response, reverse('core:register'))

    def test_register_fail_passw_not_equal(self):
        response = self.client.post(reverse('core:register'),{
            'username': 'test_example@example.com',
            'password': 'secret-1234',
            'password_again': 'secret-'
        })
        self.assertRedirects(response, reverse('core:register'))
