# Technical Documentation for Sossoldi Companion

## Index
1. How to develop an importer for a new bank

### How to develop an importer for a new bank
To develop an importer for a new bank, follow these steps:

1. Create a new file in the `importers` directory for the new bank (e.g., `transactionmanager/importers/new_bank.py`).

2. Define a new class in the file that inherits from `BaseImporter`

3. Fill the attributes of the class with the required CSV fields:
   - `BANK_NAME`: A string representing the name of the bank.
   - `CATEGORIES`: A list of categories that the bank supports.
   - `CSV_FIELDS`: A dictionary mapping field names to their respective indices in the CSV file.
   - `BANK_ICON`: A string representing the icon associated with the bank.

4. Base class have some defaults methods implemented, you need to implement all the methods that are required to parse the CSV file and have special handling for the bank's specific fields or formats. These methods include:
   - `get_description`
   - `get_transaction_type`
   - `get_transfer_account`
   - `get_amount`
   - `get_date`
   - `get_category`

See N26Importer as an example. Methods have been overridden, even if the base class provides a good default implementation.

5. In the `services/dispatcher.py` file, add an entry for the new bank in the `BANK_IMPORTERS` dictionary. The key should be the bank name without spaces or special characters, while the value should be the class you defined in step 2. Make sure to import the new class at the top of the file.

6. Add the new bank to the `BANK_CHOICES` in `transactionmanager/models.py` to ensure it is available in the database model.

7. Run `poetry run python3 manage.py makemigrations` and `poetry run python3 manage.py migrate` to update the database schema with the new bank.

8. Test the new importer by uploading a CSV file from the new bank through the "Import Transactions" page in the application.

