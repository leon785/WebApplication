from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect
from django.db import transaction
from django.views.decorators.clickjacking import xframe_options_exempt
import requests

# models
import payapp.models as payapp_models
from payapp.models import Account

# forms
from register.forms import RegisterForm
from payapp.forms import AccountForm


@xframe_options_exempt
@login_required(login_url='/register/login_user')
def home(request):
    if request.user.is_superuser:
        return render(request, 'register/home.html')
    this_user = Account.objects.filter(user__username=request.user.username).first()
    balance = this_user.balance
    currency = this_user.currency
    return render(request, 'register/home.html', {'user_balance': balance, 'user_currency': currency})


@csrf_protect
@xframe_options_exempt
@transaction.atomic
def register_user(request):
    if request.method == "POST":
        account_form = AccountForm(request.POST)
        register_form = RegisterForm(request.POST)
        if register_form.is_valid() and account_form.is_valid():
            account = account_form.save(commit=False)
            user = register_form.save()
            account.user = user
            # initialize the balance
            get_url = 'http://127.0.0.1:8000/payapp/convertcurrency/'
            r = requests.get(get_url, params={'originalCurrency': 'GBP', 'targetCurrency': str(account.currency), 'amount': 1000})
            print('1111111111111111111111')
            print(r)
            print(r.json())
            account.balance = r.json()['amount']
            account.save()
            logout(request)
            login(request, user)
            return redirect("home")
        else:
            return render(request, 'register/register.html', {'failed_signup': True, 'register_user': register_form,
                                                              'account_user': account_form})
    return render(request, "register/register.html", {"register_user": RegisterForm, "account_user": AccountForm})


@csrf_protect
@xframe_options_exempt
def login_user(request):
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                logout(request)
                login(request, user)
                return redirect('home')
            else:
                return render(request, 'register/login.html', {'failed_login': True, 'login_user': form})
    form = AuthenticationForm()
    return render(request, "register/login.html", {"login_user": form})


@xframe_options_exempt
@login_required(login_url='/register/login_user')
def logout_user(request):
    logout(request)
    return redirect("login_user")
