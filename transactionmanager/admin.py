from django.contrib import admin

from .models import BankAccount, Category, Transaction

# Register your models here.
admin.site.register(BankAccount)
admin.site.register(Category)
admin.site.register(Transaction)
