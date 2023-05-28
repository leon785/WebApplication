from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.clickjacking import xframe_options_exempt

# models
from payapp.models import Account
from django.contrib.auth.models import User
from payapp.models import Request
from payapp.models import TransactionRecord

# forms
from register.forms import RegisterForm


@xframe_options_exempt
@transaction.atomic
@login_required(login_url='/register/login_user')
def view_all_accounts(request):
    user_list = User.objects.all()
    account_list = Account.objects.all()
    return render(request, "admin/allAccounts.html", {"user_list": user_list,
                                                      "account_list": account_list})


@xframe_options_exempt
@transaction.atomic
@login_required(login_url='/register/login_user')
def view_all_transactions(request):
    transaction_list = TransactionRecord.objects.all()
    return render(request, "admin/allTransactions.html", {"transaction_list": transaction_list})


@xframe_options_exempt
@transaction.atomic
@login_required(login_url='/register/login_user')
def view_all_requests(request):
    request_list = Request.objects.all()
    return render(request, "admin/allRequests.html", {"request_list": request_list})


@csrf_protect
@xframe_options_exempt
@transaction.atomic
@login_required(login_url='/register/login_user')
def create_new_admin(request):
    msg = ''
    if request.method == "POST":
        msg = ''
        register_form = RegisterForm(request.POST)
        try:
            if register_form.is_valid():
                admin = register_form.save(commit=False)
                admin.is_superuser = True
                admin.save()
                msg = msg + 'Successfully create admin user ' + admin.username
            else:
                msg = 'form not valid'
                return render(request, 'admin/createNewAdmin.html', {'register_user': register_form, 'error_msg': msg})
        except SystemError:
            msg = msg + 'something wrong happened in the register form'
            return render(request, "admin/createNewAdmin.html", {"register_user": register_form, 'error_msg': msg})
    else:
        register_form = RegisterForm(request.POST)
    return render(request, 'admin/createNewAdmin.html', {'register_user': register_form, 'hint_msg': msg})

