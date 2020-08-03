from django.db import models

# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.TextField()


class Account(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    agency = models.CharField(max_length=50, null=True, blank=True)
    number = models.CharField(max_length=50, null=True, blank=True)


class Transaction(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    description = models.TextField()
    notes = models.TextField(null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    check_code = models.CharField(max_length=50)
    checked = models.SmallIntegerField()
    tags = models.TextField(null=True, blank=True)
