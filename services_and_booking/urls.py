from django.urls import path
from services_and_booking.views import join_category, show_homepage, show_subkategori,show_booking_view,search_subcategory, create_order, cancel_booking, create_testimoni, delete_testimoni

#from users.views import 

app_name = "service"

urlpatterns = [
    path("homepage/", show_homepage, name="show_homepage"),
    path("search-subcategory/", search_subcategory, name='search_subcategory'),
    path("subkategori/<uuid:subcategory_id>/", show_subkategori, name="show_subkategori"),
    path("booking-view/", show_booking_view, name="show_booking_view"),
    path("join-category/<uuid:subcategory_id>/", join_category, name="join_category"),
    path("create-order/", create_order, name ="create_order"),
    path("cancel_booking/", cancel_booking, name ="cancel_booking"),
    path("create_testimoni/", create_testimoni, name="create_testimoni"),
    path("delete_testimoni/<uuid:testimoni_id>/<uuid:id_subkategori>/", delete_testimoni, name="delete_testimoni"),
]