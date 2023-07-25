"""
URL configuration for adtfinal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

# urlpatterns = [
#     path('', views.index, name="index"),
#     path('car_detail', views.car_detail, name="Car Detail"),
#     path("car_delete", views.car_delete, name="Car Delete"),
#     path('car_detail/', views.default_car_detail, name='default_car_detail'),  # Add a default car_detail view
# ]

urlpatterns = [
    path('', views.index, name='index'),  # The root URL will lead to the home page
    path('car_list', views.car_list, name='car_list'),
    path('car_detail/', views.default_car_detail, name='default_car_detail'),  # Add a default car_detail view
    path('car_detail/<int:car_id>/', views.car_detail_by_id, name='car_detail'),  # Updated the URL pattern for car detail with car_id parameter
    path('car_delete/', views.car_delete, name='car_delete'),  # Ensure consistency with trailing slash
    # path('about/', views.about, name='about')
    # ... other URL patterns ...
]


