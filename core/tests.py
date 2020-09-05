import json

from datetime import datetime
from decimal import Decimal

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

    def test_account_list_only_logged(self):
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
        self.assertIn('account_list', response.context)
        for acc in response.context['account_list']:
            print(f'Checking account "{another_user_account.name}" against: "{acc.name}"')
            self.assertNotEqual(acc.name, another_user_account.name)

    def test_account_save_new(self):
        self.authenticated_session()
        response = self.client.post(reverse('core:save-account-add'), {
            'account_name': 'New Account',
            'account_agency': 'AG',
            'account_number': '1'
        })
        self.assertRedirects(response, reverse('core:edit-account', args=(1,)))

    def test_account_save_edit(self):
        self.authenticated_session()
        test_account = self.create_account(
            user=self.test_user,
            name='Account Test',
            agency='0001',
            number='1'
        )
        response = self.client.post(reverse('core:save-account-edit', args=(1,)), {
            'account_name': 'Account [edited]',
            'account_agency': 'AG [edited]',
            'account_number': '1'
        })
        self.assertRedirects(response, reverse('core:edit-account', args=(1,)))
        edited_account = Account.objects.get(pk=1)
        print(f'Edited? {test_account.name} != {edited_account.name}')
        self.assertNotEqual(test_account.name, edited_account.name)

    def test_account_delete(self):
        self.authenticated_session()
        test_account = self.create_account(
            user=self.test_user,
            name='Account Test to Delete',
            agency='0001',
            number='1'
        )
        response = self.client.get(reverse('core:del-account', args=(1,)))
        self.assertRedirects(response, reverse('core:account-list'))
        with self.assertRaisesMessage(Account.DoesNotExist, 'Account matching query does not exist.'):
            Account.objects.get(pk=1)


class TransactionRequestTest(BaseRequestTestCase):

    def test_get_transaction_success(self):
        self.authenticated_session()
        test_transaction = Transaction.objects.create(
            username=self.test_user,
            date=datetime.today().date(),
            description='Transaction Test',
            amount=120.15,
            checked=0,
        )
        test_json_response = json.dumps(
            {
                'error_message': '',
                'data': utils.model_as_dict([test_transaction]),
            },
            ensure_ascii=False
        )
        response = self.client.get(reverse('core:transaction', args=(test_transaction.id,)))
        self.assertEqual(test_json_response, response.content.decode('utf-8'))

    def test_transaction_add_success(self):
        self.authenticated_session()
        data_test = {
            'date': datetime.today().date().strftime('%Y-%m-%d'),
            'description': 'Add transaction test',
            'amount': '121.16',
            'checked': '0',
        }
        response = self.client.post(reverse('core:save-transaction-add'), data_test)
        response_obj = json.loads(response.content.decode('utf-8'))
        data = response_obj['data'][0]
        saved_model = Transaction.objects.get(pk=int(data.get('id')))
        self.assertEqual(saved_model.username, self.test_user)
        self.assertEqual(saved_model.description, data_test['description'])
        self.assertEqual(saved_model.amount, Decimal(data_test['amount']))
        self.assertEqual(saved_model.date, datetime.strptime(data_test['date'], '%Y-%m-%d').date())
        self.assertEqual(saved_model.checked, int(data_test['checked']))

    def test_transaction_edit_success(self):
        self.authenticated_session()
        today = datetime.today().date()
        data_test = {
            'date': today.strftime('%Y-%m-%d'),
            'description': 'Description Updated',
            'amount': '1.16',
            'checked': '1',
        }
        test_transaction = Transaction.objects.create(
            username=self.test_user,
            date=today,
            description='Transaction Test',
            amount=120.15,
            checked=0,
        )
        response = self.client.post(reverse('core:save-transaction-edit', args=(test_transaction.id,)), data_test)
        response_obj = json.loads(response.content.decode('utf-8'))
        data = response_obj['data'][0]
        saved_model = Transaction.objects.get(pk=test_transaction.id)
        self.assertEqual(saved_model.username, self.test_user)
        self.assertEqual(saved_model.description, data_test['description'])
        self.assertEqual(saved_model.amount, Decimal(data_test['amount']))
        self.assertEqual(saved_model.date, datetime.strptime(data_test['date'], '%Y-%m-%d').date())
        self.assertEqual(saved_model.checked, int(data_test['checked']))
