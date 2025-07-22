from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.encoding import smart_str
from django.views.generic import CreateView, DeleteView, FormView, ListView, UpdateView
from django.views.generic.list import BaseListView

from .forms import BankAccountForm, CSVImportForm, SetMainAccountForm, UserProfileForm
from .models import BANK_CHOICES, BankAccount, Category, Transaction
from .services.dispatcher import dispatch_import
from .services.export import Exporter
from .utils.complete_profile_required_mixin import CompleteProfileRequiredMixin
from .utils.ensure_bank_account_mixin import EnsureBankAccountMixin

User = get_user_model()


class CompleteProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "transactionmanager/complete_profile.html"
    success_url = reverse_lazy("home_accounts")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profilo aggiornato con successo.")
        return super().form_valid(form)


class BankAccountCreateView(
    CompleteProfileRequiredMixin, LoginRequiredMixin, CreateView
):
    model = BankAccount
    form_class = BankAccountForm
    template_name = "transactionmanager/bankaccount_form.html"
    success_url = reverse_lazy("home_accounts")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class BankAccountListCreateView(
    LoginRequiredMixin, CompleteProfileRequiredMixin, CreateView, ListView
):
    model = BankAccount
    form_class = BankAccountForm
    template_name = "transactionmanager/home_accounts.html"
    success_url = reverse_lazy("home_accounts")
    context_object_name = "accounts"

    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["accounts"] = self.get_queryset()
        context["BANK_CHOICES"] = BANK_CHOICES

        if not self.get_queryset().filter(main_account=True).exists() and self.get_queryset().count() > 0:
            messages.warning(
                    self.request, "Per favore, seleziona un conto principale per continuare."
            )

        return context


class BankAccountDeleteView(
    LoginRequiredMixin, EnsureBankAccountMixin, CompleteProfileRequiredMixin, DeleteView
):
    model = BankAccount
    success_url = reverse_lazy("home_accounts")

    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)


class SetMainAccountView(LoginRequiredMixin, EnsureBankAccountMixin, CompleteProfileRequiredMixin, FormView):
    form_class = SetMainAccountForm
    template_name = "accounts/set_main_account.html"
    success_url = reverse_lazy("home_accounts")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Conto principale aggiornato con successo.")
        return super().form_valid(form)


class CSVImportView(LoginRequiredMixin, EnsureBankAccountMixin, CompleteProfileRequiredMixin, FormView):
    form_class = CSVImportForm
    template_name = "transactionmanager/import_csv.html"
    success_url = reverse_lazy("import_csv")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        csv_file = form.cleaned_data["file"]
        account = form.cleaned_data["account"]

        try:
            result = dispatch_import(
                user=self.request.user,
                file=csv_file,
                bank_format=account.bank_type,
                iban=account.iban,
            )
        except AttributeError:
            messages.error(
                self.request,
                f"Parser non esistente per: {account.bank_type}.",
            )
            return self.form_invalid(form)

        except Exception as e:
            messages.error(self.request, f"Errore durante l'importazione: {str(e)}")
            return self.form_invalid(form)

        if "categories" in result:
            self.request.session["last_categories"] = result["categories"]

        messages.success(self.request, "Evviva! Importazione completata!")
        return super().form_valid(form)


class CSVExportView(LoginRequiredMixin, EnsureBankAccountMixin, CompleteProfileRequiredMixin, BaseListView):
    model = Transaction

    def get_queryset(self):
        return Transaction.objects.filter(
            bank_account__user=self.request.user
        ).select_related("bank_account", "transfer_account")

    def render_to_response(self, context, **response_kwargs):
        transactions = context["object_list"]
        categories = Category.objects.filter(
            created_by=self.request.user
        ).select_related("created_by")

        csv_string = Exporter(
            transactions,
            self.request.user,
            categories=categories,
            in_categories=Category.input_categories(),
        ).render_transactions_to_csv()

        return HttpResponse(
            smart_str(csv_string),
            content_type="text/csv",
            headers={
                "Content-Disposition": 'attachment; filename="export.csv"',
            },
        )
