from django import forms
from django.forms import ModelForm
from payapp.models import Account
from payapp.models import TransactionRecord
from payapp.models import Request


class AccountForm(ModelForm):
    class Meta:
        model = Account
        fields = ['currency']


class TransactionRecordForm(ModelForm):
    class Meta:
        model = TransactionRecord
        fields = ["recipient_name", "points_to_transfer", "sent_currency"]


class RequestForm(ModelForm):
    class Meta:
        model = Request
        fields = ["request_to", "points_requesting", "requested_currency"]


