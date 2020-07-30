from django.test import TestCase
from django.urls import reverse
from core.models import (
    User,
    Account,
    Transaction
)
from core.lib import utils

class BaseRequestTestCase(TestCase):

    def setUp(self):
        # Default username
        self.test_username = 'usertest@test.app'
        self.test_password = 'test_password'
        self.test_user = self.create_user(username=self.test_username, password=self.test_password)

    def authenticated_session(self):
        session = self.client.session
        session['user'] = {
            'user_id': self.test_user.id,
            'username': self.test_username
        }
        session.save()
    
    def create_user(self, username, password):
        passwd = utils.password_digest(password)
        return User.objects.create(
            username=username,
            password=passwd
        )
    
    def create_account(self, user, name, agency, number):
        return Account.objects.create(
            username=user,
            name=name,
            agency=agency,
            number=number
        )
    
        
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


class LoginRequestTest(BaseRequestTestCase):
   
    def test_login_action_success(self):
        # print('Testing Login Success....')
        response = self.client.post(reverse('core:login'), {'username': self.test_username, 'password': self.test_password})
        self.assertIs('user' in self.client.session, True)
        self.assertRedirects(response, reverse('core:journal'))
    
    def test_login_action_fail(self):
        # print('Testing Login Fail....')
        response = self.client.post(reverse('core:login'), {'username': 'User does not exist', 'password': self.test_password})
        self.assertIs('user' in self.client.session, False)
        self.assertRedirects(response, reverse('core:index'))


class RegisterRequestTest(BaseRequestTestCase):

    def test_register_success(self):
        response = self.client.post(reverse('core:register'),{
            'username': 'new.user@example.com',
            'password': 'secret-1234',
            'password_again': 'secret-1234'
        })
        self.assertIs('user' in self.client.session, True)
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


class AccountRequestTest(BaseRequestTestCase):
    
    def test_account_list_success(self):
        self.authenticated_session()
        test_account = self.create_account(
            user=self.test_user,
            name='Account Test Success',
            agency='0001',
            number='1'
        )
        response = self.client.get(reverse('core:account-list'))
        self.assertIs('account_list' in response.context, True)
        self.assertEqual(response.context['account_list'][0].name, test_account.name)

    def test_account_list_fail(self):
        self.authenticated_session()
        test_account = self.create_account(
            user=self.test_user,
            name='Account Test Success',
            agency='0001',
            number='1'
        )
        another_user = self.create_user(username='other_user_test@test.com', password='secret-321')
        another_user_account = self.create_account(
            user=another_user,
            name='Another Account Test - Fail',
            agency='0002',
            number='2'
        )
        response = self.client.get(reverse('core:account-list'))
        self.assertIs('account_list' in response.context, True)
        for acc in response.context['account_list']:
            print(f'Checking account against: {acc.name}')
            self.assertNotEqual(acc.name, another_user_account.name)
