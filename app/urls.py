from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^rates/$', views.GetRatesView.as_view(), name='get-rates-view'),
]

