from django.urls import path

from indicators.views import AllBanksAPIView, BankIndicatorAPIView, DatetimesAPIView, IndicatorsAPIView


urlpatterns = [
    path("indicators/all-banks/",
         AllBanksAPIView.as_view(),
         name='indicators.all_banks'),
    path("indicators/bank-datetimes/",
         DatetimesAPIView.as_view(),
         name='indicators.bank_datetimes'),
    path("indicators/form-indicators/",
         IndicatorsAPIView.as_view(),
         name='indicators.form.indicators'),
    path("indicators/bank-indicator-data/",
         BankIndicatorAPIView.as_view(),
         name='indicators.bank.indicator.data'),
]
