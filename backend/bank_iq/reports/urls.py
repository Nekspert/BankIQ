from django.urls import path

from .views import CheckValidDataAPIView, InterestRatesCreditAPIView, InterestRatesDepositAPIView


urlpatterns = [
    path("parse/check_params", CheckValidDataAPIView.as_view(), name="CheckValidDataAPIView"),
    path("parse/interest_rates_credit", InterestRatesCreditAPIView.as_view(),
         name="InterestRatesCreditAPIView"),
    path("parse/interest_rates_deposit", InterestRatesDepositAPIView.as_view(),
         name="InterestRatesDepositAPIView"),
]
