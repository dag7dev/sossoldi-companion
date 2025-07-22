import csv
import io
from abc import ABC
from datetime import datetime

from ..models import BankAccount, Category, Transaction

class BaseBankImporter(ABC):
    BANK_NAME = "Base Bank"
    CATEGORIES = {
        "Altro": {"icon": "category", "is_income": False},
        "Entrata": {"icon": "attach_money", "is_income": True},
        "Uscita": {"icon": "money_off", "is_income": False},
    }
    CSV_FIELDS = {
        "date": 0,
        "partner_name": 1,
        "description": 2,
        "amount": 3,
        "currency": 4,
    }

    def __init__(self, user, file, iban=None):
        self.user = user
        self.file = file
        self.iban = iban

    def create_bank_categories(self):
        """
        Create default categories for the bank if they do not exist."""
        for name, data in self.CATEGORIES.items():
            Category.objects.get_or_create(
                name=name,
                icon=data["icon"],
                importer=self.BANK_NAME,
                txn_type="IN" if data["is_income"] else "OUT",
                created_by=self.user,
            )

    def get_or_create_main_account(self):
        """
        Get or create the main bank account for the user based on the IBAN.
        """
        account = BankAccount.objects.filter(iban=self.iban, user=self.user).first()
        if not account:
            account = BankAccount.objects.create(user=self.user, iban=self.iban, name=self.BANK_NAME)
        return account

    def get_description(self, row):
        """
        Get the transaction description from the CSV row or return a default value if empty.
        """
        description = row[self.CSV_FIELDS["description"]].strip()
        return description if description else "No description"

    def get_transaction_type(self, row, amount):
        """
        Determine the transaction type based on the amount.
        If the amount is positive, it's an income; if negative, it's an expense.
        """
        if amount >= 0:
            return "IN"
        return "OUT"

    def get_transfer_account(self, row):
        """
        Get the transfer account based on the partner name in the CSV row.
        If no partner name is provided, return None.
        """
        return None
    
    def import_transactions(self):
        """
        Import transactions from the CSV file.
        This method reads the CSV content, processes each row, and creates Transaction objects.
        It also creates default categories if they do not exist.
        """

        # Ensure categories are created before importing transactions
        self.create_bank_categories()

        # Read the CSV content
        rows = self.read_csv_content()

        for row in rows:
            if not self.is_valid_row(row):
                continue

            amount = self.get_amount(row)
            description = self.get_description(row)
            txn_type = self.get_transaction_type(row, amount)
            date = self.get_date(row)

            account = self.get_or_create_main_account()
            transfer_account = self.get_transfer_account(row)
            category = self.get_category(row)

            Transaction.objects.get_or_create(
                bank_account=account,
                transfer_account=transfer_account,
                amount=abs(amount),
                txn_type=txn_type,
                date=date,
                description=description,
                category=category,
            )

        return {"categories": self.CATEGORIES}

    def read_csv_content(self):
        """
        Read the CSV content from the file and return a CSV reader object.
        """
        content = self.file.read().decode("ISO-8859-1")
        reader = csv.reader(io.StringIO(content))
        next(reader)    # Skip header row
        return reader

    def is_valid_row(self, row):
        """
        Validate the CSV row by checking required fields.
        """
        try:
            self.get_amount(row)
            return True
        except Exception:
            return False

    def get_amount(self, row):
        """
        Parse the amount from the CSV row.
        The amount is expected to be in the specified field and should be a valid float with dots as decimal separators.
        """
        return float(row[self.CSV_FIELDS["amount"]])

    def get_date(self, row):
        """
        Get the transaction date from the CSV row.
        """
        return datetime.strptime(row[self.CSV_FIELDS["booking_date"]], "%Y-%m-%d")

    def get_category(self, name, fallback="Altro"):
        """
        Get or create a category based on the name.
        If the category does not exist, create it with a fallback name and default icon.
        """
        try:
            return Category.objects.get(name=name, importer=self.BANK_NAME)
        except Category.DoesNotExist:
            return Category.objects.create(name=fallback, icon="category", importer=self.BANK_NAME, txn_type="OUT", created_by=self.user)