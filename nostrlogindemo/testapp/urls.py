from django.urls import path

from . import views

urlpatterns = [
    # ex: /questions/
    path('', views.index, name='index'),
]
