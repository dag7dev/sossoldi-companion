from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from ..models import BankAccount
class EnsureBankAccountMixin:
    """
    Ensure that the user has at least one bank account before accessing certain views.
    """

    redirect_url = "home_accounts"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not BankAccount.objects.filter(user=request.user).exists():
                messages.warning(request, "Per favore aggiungi un conto bancario per continuare.")
                return redirect(reverse(self.redirect_url), request=request)
        return super().dispatch(request, *args, **kwargs)
