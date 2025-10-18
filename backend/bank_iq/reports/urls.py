from django.urls import path

from .views import InterestRatesCreditAPIView


urlpatterns = [
    path("parse/publication/interest_rates_credit", InterestRatesCreditAPIView.as_view(),
         name="publication-InterestRatesCreditAPIView"),
]
