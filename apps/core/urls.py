from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
   # path('booking/', views.booking_view, name='booking'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('faq/', views.faq_view, name='faq'),
    path("booking/new/", views.booking_create, name="booking_create"),
    path("booking/<int:booking_id>/", views.booking_detail, name="booking_detail"),
    path("booking/<int:booking_id>/return/", views.booking_mark_returned_by_user, name="booking_mark_returned_by_user"),
    path("staff/booking/<int:booking_id>/", views.staff_booking_view, name="staff_booking_view"),
    path("staff/booking/<int:booking_id>/confirm/", views.staff_confirm_return, name="staff_confirm_return"),
    path('suruslerim/', views.my_bookings_view, name='my_bookings'),
    path('teslim-et/<int:booking_id>/', views.booking_mark_returned_by_user, name='booking_return'),
]
