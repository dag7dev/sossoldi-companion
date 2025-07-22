import csv
import io
from abc import ABC
from datetime import datetime

from ..models import BankAccount, Category, Transaction

import requests

from django.conf import settings

class BaseBankImporter(ABC):
    BANK_NAME = "Base Bank"
    EXAMPLES_PER_CATEGORY = {
        "Entrata": [
                "BONIFICO DA: MARCO ROSSI", "BONIFICO UNICREDIT", "INCASSO FATTURA", "ACCREDITO PAGA",
                "DONAZIONE LIBERA", "PAGAMENTO DA CLIENTE", "VENDITA EBAY", "RICARICA HYPE",
                "GIROCONTO ENTRATA", "RIMBORSO SPESE"
        ],
        "Uscita": [
                "ENEL SERVIZIO ELETTRICO", "HERA GAS E LUCE", "AFFITTO MENSILE", "CONDOMINIO SPA",
                "FASTWEB CASA", "ACQUA HERA", "VODAFONE CASA", "LUCE E GAS AXPO", "IMU COMUNE DI MILANO", "TASSA RIFIUTI DOMESTICA"
        ],
    }
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
        return datetime.strptime(row[self.CSV_FIELDS["date"]], "%Y-%m-%d")

    def get_category(self,row,name=None,model="llama3",examples_per_category=None,fallback="Altro", categories=None):
        """
        Get or create a Category object based on a predicted or provided category name.
        """
        if name is None and settings.OLLAMA_ENABLE:
            print(f"Predicting category for row: {row}")
            name = self.predict_category(
                    row,
                    examples_per_category=examples_per_category,
                    model=model,
                    categories=categories or self.CATEGORIES
            )

        final_name = name if name in self.CATEGORIES else fallback
        data = self.CATEGORIES.get(final_name)

        category, _ = Category.objects.get_or_create(
            name=final_name,
            importer=self.BANK_NAME,
            txn_type="IN" if data["is_income"] else "OUT",
            created_by=self.user,
            defaults={"icon": data["icon"]},
        )

        return category


    def predict_category(self, row, examples_per_category=None, model="llama3", categories=None):
        """
        Predict the category using a language model.
        """
        examples_per_category = examples_per_category or self.EXAMPLES_PER_CATEGORY

        prompt = (
            f"Questa è una transazione:\n{str(row)}\n\n"
            f"Categorie possibili: {', '.join(list(categories.keys()))}\n"
            "Scegli la categoria più adatta. Rispondi solo con il nome esatto della categoria, senza spiegazioni.\n"
            "Se l'importo è positivo è un'entrata, se negativo è un'uscita.\n"
            "L'utente è una persona comune, con transazioni private, non aziendali.\n"
            "Se riconosci che una categoria è una possibile entrata, allora considera che le categorie in entrata\n"
            "sono " + ", ".join([name for name, data in categories.items() if data["is_income"]]) + ".\n"
            "Se riconosci che una categoria è una possibile uscita, allora considera che le categorie in uscita\n"
            "sono " + ", ".join([name for name, data in categories.items() if not data["is_income"]]) + ".\n"
            # f"Ecco alcuni esempi:\n{examples_per_category}\n\n"
        )
        print(f"Prompt for category prediction: {prompt}")
        response = requests.post(
            settings.OLLAMA_API_URL,
            json={"model": model, "prompt": prompt, "stream": False},
        )
        response.raise_for_status()
        return response.json()["response"].strip()
