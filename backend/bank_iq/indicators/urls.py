from django.urls import path

from indicators.views import AllBanksAPIView, BankIndicator101APIView, BankIndicator123APIView, Datetimes101APIView, \
    Datetimes123APIView, \
    Indicators101APIView, \
    Indicators123APIView, UniqueIndicators101APIView


urlpatterns = [
    path("indicators/all-banks/",
         AllBanksAPIView.as_view(),
         name='indicators.all_banks'),

    path("indicators/f101/bank-datetimes/",
         Datetimes101APIView.as_view(),
         name='indicators.f101.bank_datetimes'),
    path("indicators/f101/form-indicators/",
         Indicators101APIView.as_view(),
         name='indicators.f101.form.indicators'),
    path("indicators/f101/unique-form-indicators",
         UniqueIndicators101APIView.as_view(),
         name='indicators.f101.unique.form.indicators'),
    path("indicators/f101/bank-indicator-data/",
         BankIndicator101APIView.as_view(),
         name='indicators.f101.bank.indicator.data'),

    path("indicators/f123/bank-datetimes/",
         Datetimes123APIView.as_view(),
         name='indicators.f123.bank_datetimes'),
    path("indicators/f123/form-indicators/",
         Indicators123APIView.as_view(),
         name='indicators.f123.form.indicators'),
    path("indicators/f123/bank-indicator-data/",
         BankIndicator123APIView.as_view(),
         name='indicators.f123.bank.indicator.data'),

]
