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
            return HttpResponseRedirect(reverse('core:index'))
    
    return f_wrapper


def index(request):
    context = {
        'messages': messages.get_messages(request)
    }
    return render(request, 'core/index.html.j2', context)


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
    context = {}
    return render(request, 'core/register.html.j2', context)

@require_login
def journal(request):
    context = {}
    return render(request, 'core/journal.html.j2', context)


def logout(request):
    # Do the logout
    try:
        del request.session['user']
    except KeyError:
        pass
    request.session.flush()
    return HttpResponseRedirect(reverse('core:index'))
