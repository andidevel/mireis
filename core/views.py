from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

# Create your views here.

def index(request):
    context = {}
    return render(request, 'core/index.html.j2', context)


def register(request):
    context = {}
    return render(request, 'core/register.html.j2', context)


def login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')


def logout(request):
    # Do the logout
    return HttpResponseRedirect(reverse('core:index'))
