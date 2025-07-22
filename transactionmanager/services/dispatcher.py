from transactionmanager.importers.n26_importer import N26Importer

PARSERS = {
    "n26": N26Importer,
}


def dispatch_import(user, file, bank_format, iban=None):
    """
    Dispatches the correct importer based on bank_format.
    """
    bank_format = bank_format.lower()

    importer = PARSERS.get(bank_format)
    if not importer:
        raise ValueError(f"Unsupported bank format: {bank_format}")

    return importer(user=user, file=file, iban=iban).import_transactions()
