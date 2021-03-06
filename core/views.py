import functools
import datetime

from django.shortcuts import (
    render,
    get_object_or_404,
    redirect
)
from django.http import (
    JsonResponse,
    Http404
)
from django.urls import reverse
from django.contrib import messages

from .lib import utils

# Models
from .models import (
    User,
    Account,
    Transaction
)

  
def require_login(_func=None, *, response_type=None):
    def real_decorator(f):
        @functools.wraps(f) # Keep original information about decorated function
        def f_wrapper(request, **kw):
            if 'user' in request.session:
                return f(request, **kw)
            else:
                if response_type == 'json':
                    return JsonResponse(
                        {
                            'error_message':'You must be logged in to access this resource',
                            'data': []
                        }
                    )
                messages.add_message(request, messages.WARNING, 'You must be logged in to access this resource!')
                return redirect('core:index')
        return f_wrapper
    if _func is None:
        return real_decorator
    else:
        return real_decorator(_func)


# def ajax_require_login(f):
#     def f_wrapper(request, **kw):
#         if 'user' in request.session:
#             return f(request, **kw)
#         else:
#             return JsonResponse(
#                 {
#                     'error_message':'You must be logged in to access this resource',
#                     'data': []
#                 }
#             )
#     return f_wrapper


def index(request):
    context = {}
    return render(request, 'core/index.html', context)


def login(request):
    username = request.POST.get('username')
    in_password = request.POST.get('password')
    password = None
    if in_password:
        password = utils.password_digest(in_password)
    try:
        user = User.objects.get(username=username)
        if user and user.password == password:
            request.session['user'] = {
                'user_id': user.id,
                'username': user.username
            }
            return redirect('core:journal')
    except User.DoesNotExist:
        pass
    # Username and/or password invalid
    messages.add_message(request, messages.ERROR, 'User and/or password invalid!')
    return redirect('core:index')


def register(request):
    context = {}
    if request.POST:
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            password_again = request.POST.get('password_again')
            if not utils.email_validate(username):
                raise Exception(f'{username} is not a valid e-mail!')
            if password != password_again:
                raise Exception('Password does not match!')
            username = username.lower()
            try:
                User.objects.get(username=username)
                messages.add_message(request, messages.ERROR, f'{username} already exists. Try another e-mail!')
            except User.DoesNotExist:
                # OK, username does not exist, so lets add him
                user = User(username=username, password=utils.password_digest(password))
                user.save()
                request.session['user'] = {
                    'user_id': user.id,
                    'username': user.username
                }
                return redirect('core:journal')
        except Exception as e:
            messages.add_message(request, messages.ERROR, e)
        return redirect('core:register')
    return render(request, 'core/register.html', context)


@require_login
def journal(request):
    context = {}
    return render(request, 'core/journal.html', context)


@require_login
def account_list(request):
    context = {}
    context['account_list'] = Account.objects.filter(username=request.session['user'].get('user_id'))
    return render(request, 'core/account-list.html', context)


@require_login
def add_account(request):
    context = {
        'form': {
            'account_id': '',
            'account_name': '',
            'account_agency': '',
            'account_number': '',
        }
    }
    return render(request, 'core/edit-account.html', context)


@require_login
def edit_account(request, pk):
    account = get_object_or_404(Account, username=request.session['user'].get('user_id'), pk=pk)
    context = {
        'form': {
            'account_id': account.id,
            'account_name': account.name,
            'account_agency': account.agency,
            'account_number': account.number,
        }
    }
    return render(request, 'core/edit-account.html', context)


@require_login
def save_account(request, pk=None):
    if request.POST:
        if pk:
            account = get_object_or_404(Account, username=request.session['user'].get('user_id'), pk=pk)
        else:
            account = Account()
            account.username_id = request.session['user'].get('user_id') 
        account.name = request.POST.get('account_name')
        account.agency = request.POST.get('account_agency')
        account.number = request.POST.get('account_number')
        account.save()
        messages.add_message(request, messages.SUCCESS, 'Account save successfuly!')
        return redirect('core:edit-account', pk=account.id)
    raise Http404('Resource not found')


@require_login
def del_account(request, pk):
    account = get_object_or_404(Account, username=request.session['user'].get('user_id'), pk=pk)
    account.delete()
    return redirect('core:account-list')


@require_login(response_type='json')
def get_transaction(request, pk):
    json_response = {
        'error_message': '',
        'data': []
    }

    try:
        trs = Transaction.objects.get(username=request.session['user'].get('user_id'), pk=pk)
        json_response['data'].append(utils.model_row_as_dict(trs))
    except Transaction.DoesNotExist:
        json_response['error_message'] = 'Transaction not found'
        json_response['data'] = []
    return JsonResponse(json_response)


@require_login(response_type='json')
def save_transaction(request, pk=None):
    if request.POST:
        json_response = {
            'error_message': '',
            'data': []
        }
        if pk:
            transaction = get_object_or_404(Transaction, username=request.session['user'].get('user_id'), pk=pk)
        else:
            transaction = Transaction()
            transaction.username_id = request.session['user'].get('user_id')
        transaction.date = datetime.datetime.strptime(request.POST.get('date'), '%Y-%m-%d').date()
        transaction.description = request.POST.get('description')
        transaction.amount = float(request.POST.get('amount'))
        transaction.checked = int(request.POST.get('checked'))
        transaction.account_id = int(request.POST.get('account_id')) if request.POST.get('account_id') else None
        transaction.save()
        json_response['data'].append(utils.model_row_as_dict(transaction))
        return JsonResponse(json_response)
    raise Http404('Resource not found')


def logout(request):
    # Do the logout
    try:
        del request.session['user']
    except KeyError:
        pass
    request.session.flush()
    return redirect('core:index')
