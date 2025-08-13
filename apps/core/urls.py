from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("booking/new/", views.booking_create, name="booking_create"),
    path("booking/<int:booking_id>/", views.booking_detail, name="booking_detail"),
    path("booking/<int:booking_id>/return/", views.booking_mark_returned_by_user, name="booking_mark_returned_by_user"),
    path("staff/booking/<int:booking_id>/", views.staff_booking_view, name="staff_booking_view"),
    path("staff/booking/<int:booking_id>/confirm/", views.staff_confirm_return, name="staff_confirm_return"),
]
