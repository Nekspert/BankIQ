from django.urls import path

from .views import AllBanksAPIView, Datetimes101APIView, Datetimes123APIView


urlpatterns = [
    path("indicators/all-banks/",
         AllBanksAPIView.as_view(),
         name='indicators.all_banks'),

    path("indicators/f101/bank-datetimes/",
         Datetimes101APIView.as_view(),
         name='indicators.f101.bank_datetimes'),
    path("indicators/f123/bank-datetimes/",
         Datetimes123APIView.as_view(),
         name='indicators.f123.bank_datetimes'),
]
