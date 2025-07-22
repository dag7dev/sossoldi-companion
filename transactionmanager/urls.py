from django.urls import path

from .views import (
    BankAccountCreateView,
    BankAccountDeleteView,
    BankAccountListCreateView,
    CompleteProfileView,
    CSVExportView,
    CSVImportView,
    SetMainAccountView,
)

urlpatterns = [
    path("", BankAccountListCreateView.as_view(), name="home_accounts"),
    path("complete-profile/", CompleteProfileView.as_view(), name="complete_profile"),
    path("accounts/new/", BankAccountCreateView.as_view(), name="create_account"),
    path(
        "account/<int:pk>/delete/",
        BankAccountDeleteView.as_view(),
        name="delete_account",
    ),
    path(
        "account/<int:pk>/main/", SetMainAccountView.as_view(), name="set_main_account"
    ),
    path("account/set-main/", SetMainAccountView.as_view(), name="set_main_account"),
    path("import/", CSVImportView.as_view(), name="import_csv"),
    path("export/", CSVExportView.as_view(), name="export_csv"),
]
