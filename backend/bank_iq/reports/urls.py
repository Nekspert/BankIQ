from django.urls import path

from .views import CheckValidDataAPIView, InterestRatesCreditAPIView, InterestRatesDepositAPIView


urlpatterns = [
    path("reports/parameters/check/",
         CheckValidDataAPIView.as_view(),
         name="reports.parameters.check"),

    path("reports/interest-rates/credit/",
         InterestRatesCreditAPIView.as_view(),
         name="reports.interest_rates.credit"),

    path("reports/interest-rates/deposit/",
         InterestRatesDepositAPIView.as_view(),
         name="reports.interest_rates.deposit"),
]
