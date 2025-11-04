from django.urls import path

from indicators.views import AllBanksAPIView, BankIndicatorAPIView, DatetimesAPIView, IndicatorsAPIView, \
    UniqueIndicatorsAPIView


urlpatterns = [
    path("indicators/all-banks/",
         AllBanksAPIView.as_view(),
         name='indicators.all_banks'),
    path("indicators/f101/bank-datetimes/",
         DatetimesAPIView.as_view(),
         name='indicators.f101.bank_datetimes'),
    path("indicators/f101/form-indicators/",
         IndicatorsAPIView.as_view(),
         name='indicators.f101.form.indicators'),
    path("indicators/f101/unique-form-indicators",
         UniqueIndicatorsAPIView.as_view(),
         name='indicators.f101.unique.form.indicators'),
    path("indicators/f101/bank-indicator-data/",
         BankIndicatorAPIView.as_view(),
         name='indicators.f101.bank.indicator.data'),
]
