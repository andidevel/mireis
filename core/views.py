from django.shortcuts import (
    render,
    get_object_or_404,
    redirect
)
from django.http import Http404
from django.urls import reverse
from django.contrib import messages

from .lib import utils

# Models
from .models import (
    User,
    Account,
    Transaction
)

  
def require_login(f):
    def f_wrapper(request, **kw):
        if 'user' in request.session:
            return f(request, **kw)
        else:
            messages.add_message(request, messages.WARNING, 'You must be logged in to access this resource!')
            return redirect('core:index')
    
    return f_wrapper


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
            logged_user = User.objects.get(pk=request.session['user'].get('user_id'))
            account.username = logged_user
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


def logout(request):
    # Do the logout
    try:
        del request.session['user']
    except KeyError:
        pass
    request.session.flush()
    return redirect('core:index')
