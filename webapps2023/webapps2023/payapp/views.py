from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from datetime import datetime
from django.views.decorators.clickjacking import xframe_options_exempt
import requests

# models
from payapp.models import Account
from payapp.models import TransactionRecord
from payapp.models import Request
from django.contrib.auth.models import User

# forms
from payapp.forms import TransactionRecordForm
from payapp.forms import RequestForm

# REST
from rest_framework.views import APIView
from rest_framework.response import Response


@csrf_protect
@xframe_options_exempt
@transaction.atomic
@login_required(login_url='/register/login_user')
def points_transfer(request):
    if request.method == 'POST':
        hint_msg = ''
        error_msg = ''
        record_form = TransactionRecordForm(request.POST)

        if record_form.is_valid():
            sender_name = request.user.username
            recipient_name = record_form.cleaned_data["recipient_name"]
            points_to_transfer = record_form.cleaned_data["points_to_transfer"]
            sent_currency = record_form.cleaned_data["sent_currency"]

            sender = Account.objects.filter(user__username=sender_name).first()
            recipient = Account.objects.filter(user__username=recipient_name).first()

            if recipient is None:
                error_msg = 'Failed, no such a user in the database'
            elif sender_name == recipient_name:
                error_msg = 'You cannot transfer money to yourself'
            elif sender.balance < points_to_transfer:
                error_msg = 'Failed, your balance is not enough'
            else:
                # process the transaction
                # sender minus money
                get_url = 'http://127.0.0.1:8000/payapp/convertcurrency/'
                r = requests.get(get_url, params={'originalCurrency': str(sent_currency),
                                                  'targetCurrency': str(sender.currency),
                                                  'amount': str(points_to_transfer)})
                pts_from_sender = r.json()['amount']
                sender.balance = sender.balance - pts_from_sender
                # recipient add money
                get_url = 'http://127.0.0.1:8000/payapp/convertcurrency/'
                r = requests.get(get_url, params={'originalCurrency': str(sent_currency),
                                                  'targetCurrency': str(recipient.currency),
                                                  'amount': str(points_to_transfer)})
                pts_to_recipient = r.json()['amount']
                recipient.balance = recipient.balance + pts_to_recipient
                # SAVE
                recipient.save()
                sender.save()
                hint_msg = 'transaction succeeded'

                # process the history record
                this_record = TransactionRecord()
                this_record.sender_name = sender_name
                this_record.recipient_name = recipient_name
                this_record.points_to_transfer = points_to_transfer
                this_record.sent_currency = sent_currency
                this_record.save()

        return render(request, "payapp/pointsTransfer.html", {"form": record_form, "hint_msg": hint_msg,
                                                              "error_msg": error_msg})
    else:
        record_form = TransactionRecordForm()
    return render(request, "payapp/pointsTransfer.html", {"form": record_form})


@csrf_protect
@xframe_options_exempt
@transaction.atomic
@login_required(login_url='/register/login_user')
def make_request(request):
    if request.method == 'POST':
        hint_msg = ''
        error_msg = ''
        request_form = RequestForm(request.POST)

        if request_form.is_valid():
            request_to = request_form.cleaned_data["request_to"]

            if len(User.objects.filter(username=request_to)) <= 0:
                error_msg = 'Failed, no such a user in database'
            elif request_to == request.user.username:
                error_msg = 'You cannot make a request with yourself'
            else:
                this_request = Request()
                this_request.request_from = request.user.username
                this_request.request_to = request_form.cleaned_data["request_to"]
                this_request.points_requesting = request_form.cleaned_data["points_requesting"]
                this_request.requested_currency = request_form.cleaned_data["requested_currency"]
                this_request.save()
                hint_msg = 'request set up successfully'

        else:
            error_msg = 'Failed, request form is not valid'

        return render(request, "payapp/makeRequest.html", {"form": request_form, "hint_msg": hint_msg,
                                                           "error_msg": error_msg})
    else:
        request_form = RequestForm()
    return render(request, "payapp/makeRequest.html", {"form": request_form})


@xframe_options_exempt
@transaction.atomic
@login_required(login_url='/register/login_user')
def show_history(request):
    username = request.user.username
    user_send_list = TransactionRecord.objects.filter(sender_name=username)
    user_receive_list = TransactionRecord.objects.filter(recipient_name=username)
    return render(request, "payapp/history.html", {"send_list": user_send_list, "receive_list": user_receive_list})


@xframe_options_exempt
@transaction.atomic
@login_required(login_url='/register/login_user')
def show_request(request):
    username = request.user.username
    received_requests = Request.objects.filter(request_to=username)
    sent_requests = Request.objects.filter(request_from=username)
    return render(request, "payapp/requestList.html", {'received_requests': received_requests,
                                                       'sent_requests': sent_requests})


@xframe_options_exempt
@transaction.atomic
@login_required(login_url='/register/login_user')
def button_accept(request):
    request_id = request.GET["request_id"]
    target_request = Request.objects.get(pk=request_id)

    sender_name = target_request.request_to
    recipient_name = target_request.request_from
    points_to_transfer = target_request.points_requesting
    currency_used = target_request.requested_currency

    sender = Account.objects.filter(user__username=sender_name).first()
    recipient = Account.objects.filter(user__username=recipient_name).first()
    msg = ''

    get_url = 'http://127.0.0.1:8000/payapp/convertcurrency/'
    r = requests.get(get_url, params={'originalCurrency': str(currency_used),
                                      'targetCurrency': str(sender.currency),
                                      'amount': str(points_to_transfer)})
    pts_from_sender = r.json()['amount']

    get_url = 'http://127.0.0.1:8000/payapp/convertcurrency/'
    r = requests.get(get_url, params={'originalCurrency': str(currency_used),
                                      'targetCurrency': str(recipient.currency),
                                      'amount': str(points_to_transfer)})
    pts_to_recipient = r.json()['amount']

    if sender.balance < pts_from_sender:
        msg = msg + 'Failed, your balance is not enough'
    else:
        # process the transaction
        sender.balance = sender.balance - pts_from_sender
        recipient.balance = recipient.balance + pts_to_recipient
        sender.save()
        recipient.save()

        # process the history record
        this_record = TransactionRecord()
        this_record.sender_name = sender_name
        this_record.recipient_name = recipient_name
        this_record.points_to_transfer = points_to_transfer
        this_record.sent_currency = currency_used
        this_record.save()

        target_request.request_status = True
        target_request.time_processing = datetime.now()
        target_request.save()

    received_requests = Request.objects.filter(request_to=request.user.username)
    sent_requests = Request.objects.filter(request_from=request.user.username)
    return render(request, "payapp/requestList.html", {'received_requests': received_requests,
                                                       'sent_requests': sent_requests, 'msg': msg})


@xframe_options_exempt
@transaction.atomic
@login_required(login_url='/register/login_user')
def button_decline(request):
    request_id = request.GET["request_id"]
    target_request = Request.objects.get(pk=request_id)
    target_request.request_status = False
    target_request.time_processing = datetime.now()
    target_request.save()
    return redirect("past_request")


class CurrencyChange(APIView):

    def get(self, request):
        original_currency = request.query_params.get('originalCurrency')
        target_currency = request.query_params.get('targetCurrency')
        amount = float(request.query_params.get('amount'))

        if original_currency == target_currency:
            return Response({'amount': amount})
        elif original_currency == "GBP" and target_currency == "USD":
            return Response({'amount': amount*1.22})
        elif original_currency == "GBP" and target_currency == "EUR":
            return Response({'amount': amount*1.13})
        elif original_currency == "USD" and target_currency == "GBP":
            return Response({'amount': amount*0.82})
        elif original_currency == "USD" and target_currency == "EUR":
            return Response({'amount': amount*0.93})
        elif original_currency == "EUR" and target_currency == "GBP":
            return Response({'amount': amount*0.88})
        elif original_currency == "EUR" and target_currency == "USD":
            return Response({'amount': amount*1.08})

