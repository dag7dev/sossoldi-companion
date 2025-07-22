from .base_importer import BaseBankImporter
from ..models import BankAccount
from datetime import datetime

class N26Importer(BaseBankImporter):
    BANK_NAME = "N26"

    CATEGORIES = {
        "Entrata": {"icon": "attach_money", "is_income": True},
        "Trasporto & Auto": {"icon": "directions_car", "is_income": False},
        "Stipendio": {"icon": "payments", "is_income": True},
        "Casa & Utenze": {"icon": "home", "is_income": False},
        "Tasse e multe": {"icon": "gavel", "is_income": False},
        "Altro": {"icon": "category", "is_income": False},
        "Cibo & Spesa": {"icon": "shopping_cart", "is_income": False},
        "ATM": {"icon": "atm", "is_income": False},
        "Assicurazioni & Finanza": {"icon": "account_balance", "is_income": False},
        "Shopping": {"icon": "store", "is_income": False},
        "Bar & Ristoranti": {"icon": "restaurant", "is_income": False},
        "Spese aziendali": {"icon": "business_center", "is_income": False},
        "Cash26": {"icon": "credit_card", "is_income": False},
        "Educazione": {"icon": "school", "is_income": False},
        "Famiglia & Amici": {"icon": "people", "is_income": False},
        "Cure sanitarie & Farmacia": {"icon": "local_hospital", "is_income": False},
        "Tempo libero & Intrattenimento": {"icon": "sports_esports", "is_income": False},
        "Multimedia & Elettronica": {"icon": "devices", "is_income": False},
        "N26 sponsorizzazioni": {"icon": "star", "is_income": True},
        "Risparmio & Investimenti": {"icon": "trending_up", "is_income": False},
        "Sottoscrizioni & Donazioni": {"icon": "favorite", "is_income": False},
        "Viaggi & vacanze": {"icon": "flight", "is_income": False},
    }
    CSV_FIELDS = {
        "booking_date": 0,
        "value_date": 1,
        "partner_name": 2,
        "partner_iban": 3,
        "type": 4,
        "payment_ref": 5,
        "account_name": 6,
        "amount": 7,
        "original_amount": 8,
        "original_currency": 9,
        "exchange_rate": 10,
    }


    def get_description(self, row):
        partner = row[self.CSV_FIELDS["partner_name"]]
        ref = row[self.CSV_FIELDS["payment_ref"]].strip()
        return f"{partner} | {ref}" if partner and ref else partner or ref

    def get_transaction_type(self, row, amount):
        txn_type_raw = row[self.CSV_FIELDS["type"]]
        partner_name = row[self.CSV_FIELDS["partner_name"]]
        if txn_type_raw == "Debit Transfer" and partner_name:
            return "TRSF"
        return "IN" if amount >= 0 else "OUT"

    def get_transfer_account(self, row):
        txn_type = self.get_transaction_type(row, float(row[self.CSV_FIELDS["amount"]]))
        if txn_type != "TRSF":
            return None

        partner_iban = row[self.CSV_FIELDS["partner_iban"]]
        partner_name = row[self.CSV_FIELDS["partner_name"]]

        account = BankAccount.objects.filter(user=self.user, iban=partner_iban).first()
        if not account and partner_name == f"{self.user.first_name} {self.user.last_name}":
            account = BankAccount.objects.create(
                user=self.user,
                iban=partner_iban,
                name="GENERATED_TRANSFER_ACCOUNT",
            )
        return account
    
    def get_date(self, row):
        return datetime.strptime(row[self.CSV_FIELDS["booking_date"]], "%Y-%m-%d")

    def get_amount(self, row):
        return float(row[self.CSV_FIELDS["amount"]])

    def get_category(self, row):
        try:
            category_name = row[self.CSV_FIELDS["category"]]
        except KeyError:
            return super().get_category("Altro")

        return super().get_category(category_name, fallback="Altro")