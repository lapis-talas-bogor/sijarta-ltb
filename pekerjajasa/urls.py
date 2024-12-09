from django.urls import path
from pekerjajasa.views import pekerjajasa_view, status_view, update_status, ambil_pekerjaan, get_subcategories

app_name = "pekerjajasa"

urlpatterns = [
    path("", pekerjajasa_view, name="pekerjajasa_view"),
    path("status/", status_view, name="status_view"),
    path("update_status/", update_status, name="update_status"),
    path("ambil_pekerjaan/", ambil_pekerjaan, name="ambil_pekerjaan"),
    path('get-subcategories/', get_subcategories, name='get_subcategories')
]
