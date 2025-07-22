# Sossoldi Companion App

A simple Django webapp to be used in tandem with the application "Sossoldi", available [on Github](https://github.com/RIP-Comm/sossoldi).

## Features
- **Import Transactions**: Import transactions from various banks.
- **Export all transactions**: Export all transactions to a CSV file compatible with Sossoldi.
- **Manage your bank accounts**: Add, edit, and delete bank accounts.

## Requirements
- Python 3.11 or higher
- Django 5.2 or higher
- Poetry for dependency management

## Installation
### Docker (Recommended)
1. Clone the repository:
   ```bash
   git clone https://github.com/dag7dev/sossoldi-companion-app.git
   cd sossoldi-companion-app
    ```
2. Set up environment variables:
    Create a `.env` file in the root directory and add the following variables:
    - `DJANGO_SECRET_KEY`: A secret key for Django.
    - `DEBUG`: Set to `True` for development, `False` for production.
    - `DJANGO_SUPERUSER_USERNAME`: The username for the Django superuser.
    - `DJANGO_SUPERUSER_EMAIL`: The email for the Django superuser.
    - `DB_NAME`: The name of the database.
    - `DB_USER`: The database user.
    - `DB_PASSWORD`: The password for the database user.
    - `DB_HOST`: The database host (default is `db`).
    - `DB_PORT`: The database port (default is `5432` for PostgreSQL).

    To setup django superuser password, you should generate a password using the command using Linux or WSL, and place it in the `.django-superuser-pw` file:
    ```bash
    openssl rand -base64 16
    ```

    If you don't, a generated password will be used, and you will manually need to check it through the .django-superuser-pw file (it will be created automatically after the first run of the app).

    See the [example .env file](.env.example) for reference.

3. Build and run the Docker container:
   ```bash
   docker-compose up --build
   ```

4. Access the app at `http://localhost:8000`. On first access, you will need to enter your name and surname exactly as they are in your bank accounts, otherwise the app will not work correctly.

### Local Development
1. Clone the repository:
   ```bash
   git clone https://github.com/dag7dev/sossoldi-companion-app.git
   cd sossoldi-companion-app
   ```

2. Create a virtual environment:
   ```bash
   poetry env activate
   ```

3. Install dependencies:
   ```bash
    poetry install
    ```
2. Set up environment variables:
    Create a `.env` file in the root directory and add the following variables:
    - `DJANGO_SECRET_KEY`: A secret key for Django.
    - `DEBUG`: Set to `True` for development, `False` for production.
    - `DB_NAME`: The name of the database.
    - `DB_USER`: The database user.
    - `DB_PASSWORD`: The password for the database user.
    - `DB_HOST`: The database host (default is `db`).
    - `DB_PORT`: The database port (default is `5432` for PostgreSQL).

    See the [example .env file](.env.example) for reference.

5. Run migrations:
   ```bash
    poetry run python3 manage.py migrate
    ```
6. Create a superuser:
   ```bash
    poetry run python3 manage.py createsuperuser
    ```

7. Run the development server:
   ```bash
    poetry run python3 manage.py runserver
    ```
    
8. Access the app at `http://localhost:8000`. On first access, you will need to enter your name and surname exactly as they are in your bank accounts, otherwise the app will not work correctly.

## Usage
1. First, add your bank accounts:
   - Navigate to the "Bank Accounts" page (home page).
   - Fill in the form with your bank account details, including the name, IBAN, and bank type (N26, Fineco, Revolut, Intesa, Poste...).
   - Click on "Add Bank Account".
   - Make sure to add all your bank accounts, as IBAN will be used to match "transfers" transactions.

2. Import transactions:
    - Navigate to the "Import Transactions" page, by clicking on the "Import Transactions" link in the navigation bar.
    - Select the bank account you want to import transactions for.
    - Upload the CSV file containing your transactions.
    - Click on "Import Transactions".
    - If everything goes well, the page will refresh with a success message

3. Export transactions:
    - Click on the "Export" button in the top right corner of the "Transactions" page. 
    - A CSV file will be downloaded. You can then import this file into Sossoldi.


## How can I contribute?
This project is open source and contributions are welcome! If you find a bug or have a feature request, please open an issue on GitHub. If you want to contribute code, please follow the steps below.

See technical details in the [Technical Documentation](TECHNICAL.md).

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/name-of-your-feature
   ```
3. Make your changes and commit them:
   ```bash
    git commit -m "Add your feature description"
    ```
4. Push to the branch:
    ```bash
    git push origin feature/name-of-your-feature
    ```
5. Create a pull request.

## License
MIT License. See the [LICENSE](LICENSE) file for details.