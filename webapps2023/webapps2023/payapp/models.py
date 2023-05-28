from django.db import models
from django.contrib.auth.models import User


currency_choices = (("GBP", "GBP"), ("USD", "USD"), ("EUR", "EUR"))


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.CharField(max_length=3, choices=currency_choices)
    balance = models.FloatField()


class TransactionRecord(models.Model):
    sender_name = models.CharField(max_length=100)
    recipient_name = models.CharField(max_length=100)
    points_to_transfer = models.IntegerField()
    sent_currency = models.CharField(max_length=3, choices=currency_choices)
    time_sending = models.DateTimeField(auto_now_add=True)


class Request(models.Model):
    request_from = models.CharField(max_length=100)
    request_to = models.CharField(max_length=100)
    points_requesting = models.IntegerField()
    requested_currency = models.CharField(max_length=3, choices=currency_choices)
    time_requesting = models.DateTimeField(auto_now_add=True)
    time_processing = models.DateTimeField(null=True, default=None)
    request_status = models.BooleanField(null=True)


