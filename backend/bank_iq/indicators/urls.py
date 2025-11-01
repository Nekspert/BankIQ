from django.urls import path

from indicators.views import AllBanksAPIView


urlpatterns = [
    path("indicators/all-banks/",
         AllBanksAPIView.as_view(),
         name='indicators.all_banks'),
]
