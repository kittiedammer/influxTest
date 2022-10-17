from django.urls import re_path, path

from influx_api import views

from django.conf.urls.static import static
from django.conf import settings

from rest_framework import permissions

urlpatterns = [
                  path('shifts/<int:id>/<int:start>/<int:end>/', views.shifts, name='api-test'),
              ]
