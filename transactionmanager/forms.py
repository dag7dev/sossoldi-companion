from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .models import BANK_CHOICES, BankAccount

User = get_user_model()


class CSVImportForm(forms.Form):
    file = forms.FileField(
        label="File CSV",
        widget=forms.ClearableFileInput(attrs={"class": "form-control"}),
    )
    account = forms.ModelChoiceField(
        queryset=BankAccount.objects.none(),
        label="Account",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["account"].queryset = BankAccount.objects.filter(
                user=user, bank_type__in=[choice[0] for choice in BANK_CHOICES]
            )

            print(self.fields["account"].queryset.first().bank_type)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]
        labels = {
            "first_name": "Nome",
            "last_name": "Cognome",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update(
                {
                    "class": "form-control",
                    "placeholder": field.label,
                }
            )


class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ["name", "iban", "bank_type"]
        labels = {
            "name": "Nome Conto",
            "iban": "IBAN",
            "bank_type": "Tipo di Banca",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "iban": forms.TextInput(attrs={"class": "form-control"}),
            "bank_type": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        iban = cleaned_data.get("iban")
        bank_type = cleaned_data.get("bank_type")

        if name and iban and bank_type:
            if BankAccount.objects.filter(
                name=name, iban=iban, user=self.user, bank_type=bank_type
            ).exists():
                raise ValidationError(
                    "You already have an account with this name, IBAN, and bank type."
                )

        return cleaned_data


class SetMainAccountForm(forms.Form):
    account_id = forms.IntegerField(widget=forms.HiddenInput)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_account_id(self):
        account_id = self.cleaned_data.get("account_id")

        if not BankAccount.objects.filter(pk=account_id, user=self.user).exists():
            raise ValidationError("Conto non valido o non appartenente all'utente.")
        return account_id

    def save(self):
        """
        Set the selected account as the main account for the user.
        """
        # Remove the 'main' status from all user accounts
        BankAccount.objects.filter(user=self.user).update(main_account=False)
        # Imposta il nuovo conto principale
        account = BankAccount.objects.get(
            pk=self.cleaned_data["account_id"], user=self.user
        )
        account.main_account = True
        account.save()
