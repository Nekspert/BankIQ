from django.urls import path

from .views import InterestRatesCreditAPIView


urlpatterns = [
    path("parse/interest_rates_credit", InterestRatesCreditAPIView.as_view(),
         name="InterestRatesCreditAPIView"),
]
