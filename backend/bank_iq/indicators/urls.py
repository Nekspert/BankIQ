from django.urls import path

from indicators.views import BankIndicator101APIView, BankIndicator123APIView, BankIndicator810APIView, \
    Indicators101APIView, Indicators123APIView, UniqueIndicators101APIView


urlpatterns = [
    path("indicators/f810/bank-indicator-data/",
         BankIndicator810APIView.as_view(),
         name="indicators.f810.bank.indicator.data"),
    path("indicators/f101/form-indicators/",
         Indicators101APIView.as_view(),
         name='indicators.f101.form.indicators'),
    path("indicators/f101/unique-form-indicators",
         UniqueIndicators101APIView.as_view(),
         name='indicators.f101.unique.form.indicators'),
    path("indicators/f101/bank-indicator-data/",
         BankIndicator101APIView.as_view(),
         name='indicators.f101.bank.indicator.data'),

    path("indicators/f123/form-indicators/",
         Indicators123APIView.as_view(),
         name='indicators.f123.form.indicators'),
    path("indicators/f123/bank-indicator-data/",
         BankIndicator123APIView.as_view(),
         name='indicators.f123.bank.indicator.data'),

]
