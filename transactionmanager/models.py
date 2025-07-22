from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

BANK_CHOICES = [
    ("n26", "N26"),
]


class BankAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    iban = models.CharField(max_length=34, unique=True)
    main_account = models.BooleanField(default=False)
    bank_type = models.CharField(
        max_length=32, choices=BANK_CHOICES, blank=True, default=""
    )

    def __str__(self):
        return f"{self.name} ({self.iban})"

    def save(self, *args, **kwargs):
        if self.main_account:
            BankAccount.objects.filter(user=self.user).update(main_account=False)
        super().save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=128)
    icon = models.CharField(max_length=64)
    txn_type = models.CharField(
        max_length=4, choices=[("IN", "Entrata"), ("OUT", "Uscita")]
    )
    importer = models.CharField(choices=BANK_CHOICES, max_length=10, default="n26")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="categories"
    )

    def __str__(self):
        return f"{self.name} ({self.txn_type}) - {self.importer}"

    @classmethod
    def input_categories(cls):
        return cls.objects.filter(txn_type="IN")


class Transaction(models.Model):
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.SET_NULL
    )
    transfer_account = models.ForeignKey(
        BankAccount,
        null=True,
        blank=True,
        related_name="transfer",
        on_delete=models.SET_NULL,
    )
    date = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    txn_type = models.CharField(
        max_length=4,
        choices=[("IN", "Entrata"), ("OUT", "Uscita"), ("TRSF", "Trasferimento")],
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.date.strftime('%Y-%m-%d')} - {self.bank_account.name} - {self.amount} {self.txn_type} - {self.description}"
