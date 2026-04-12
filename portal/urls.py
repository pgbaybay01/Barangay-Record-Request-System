from django.urls import path

from . import views

app_name = "portal"

urlpatterns = [
    path("", views.home, name="home"),
    path("request/", views.request_form, name="request_form"),
    path("track/", views.tracker, name="tracker"),
    path("admin/login/", views.admin_login, name="admin_login"),
    path("admin/logout/", views.admin_logout, name="admin_logout"),
    path("admin/dashboard/", views.admin_dash, name="admin_dash"),
]
