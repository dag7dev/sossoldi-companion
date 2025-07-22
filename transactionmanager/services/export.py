import csv
import io
from datetime import datetime

from ..models import BankAccount


class Exporter:
    """
    Base class for export functionality.
    """

    transactions = None
    user = None
    categories = None
    in_categories = None

    SOSSOLDI_HEADER = (
        "table_name,id,name,symbol,color,startingValue,active,mainAccount,createdAt,updatedAt,"
        "countNetWorth,date,amount,type,note,idCategory,idBankAccount,idBankAccountTransfer,"
        "recurring,idRecurringTransaction,fromDate,toDate,recurrency,lastInsertion,parent,"
        "amountLimit,code,mainCurrency"
    )

    def __init__(self, transactions, user, categories=None, in_categories=None):
        self.transactions = transactions
        self.user = user
        self.categories = categories or []
        self.in_categories = in_categories or []

    def now(self):
        """
        Returns the current timestamp formatted as a string.
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    def render_transactions_to_csv(self):
        """
        Renders transactions and bank accounts to a CSV format compatible with SOSSOLDI.
        """
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(self.SOSSOLDI_HEADER.split(","))

        # 1. Bank accounts
        for account in BankAccount.objects.filter(user=self.user):
            writer.writerow(
                [
                    "bankAccount",
                    account.id,
                    account.name,
                    "payments",
                    account.id,
                    0.0,
                    1,
                    1 if account.main_account else 0,
                    self.now(),
                    self.now(),
                    "",
                    "1",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                ]
            )

        # 2. Transactions
        for tx in self.transactions:
            writer.writerow(
                [
                    "transaction",
                    tx.id,
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    tx.date.strftime("%Y-%m-%d %H:%M:%S.%f"),
                    tx.date.strftime("%Y-%m-%d %H:%M:%S.%f"),
                    "",
                    tx.date.strftime("%Y-%m-%d %H:%M:%S.%f"),
                    abs(tx.amount),
                    tx.txn_type,
                    tx.description or "",
                    tx.category.id if tx.category else "",
                    tx.bank_account.id,
                    tx.transfer_account.id if tx.transfer_account else "",
                    0,
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                ]
            )

        # 3. Optional categories
        if self.categories:
            base_id = 10
            for idx, cat in enumerate(self.categories):
                txn_type = "IN" if cat.name in self.in_categories else "OUT"
                writer.writerow(
                    [
                        "categoryTransaction",
                        base_id + idx,
                        cat.name,
                        cat.icon,
                        idx,
                        "",
                        "",
                        "",
                        self.now(),
                        self.now(),
                        "",
                        "",
                        "",
                        txn_type,
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                    ]
                )

        return buffer.getvalue()
