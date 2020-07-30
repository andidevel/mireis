from django.shortcuts import render
from django.http import HttpResponseRedirect
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
    def f_wrapper(request):
        if 'user' in request.session:
            return f(request)
        else:
            messages.add_message(request, messages.WARNING, 'You must be logged in to access this resource!')
            return HttpResponseRedirect(reverse('core:index'))
    
    return f_wrapper


def index(request):
    context = {
        'messages': messages.get_messages(request)
    }
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
            return HttpResponseRedirect(reverse('core:journal'))
    except User.DoesNotExist:
        pass
    # Username and/or password invalid
    messages.add_message(request, messages.ERROR, 'User and/or password invalid!')
    return HttpResponseRedirect(reverse('core:index'))


def register(request):
    context = {
        'messages': messages.get_messages(request)
    }
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
                return HttpResponseRedirect(reverse('core:journal'))
        except Exception as e:
            messages.add_message(request, messages.ERROR, e)
        return HttpResponseRedirect(reverse('core:register'))
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


def logout(request):
    # Do the logout
    try:
        del request.session['user']
    except KeyError:
        pass
    request.session.flush()
    return HttpResponseRedirect(reverse('core:index'))
