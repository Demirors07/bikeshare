from django.contrib import admin
from .models import Station, Bike, PricingPlan, Booking, Payment, SMSLog

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ("name","is_active")

@admin.register(Bike)
class BikeAdmin(admin.ModelAdmin):
    list_display = ("tag","station","is_active")
    list_filter = ("station","is_active")

@admin.register(PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
    list_display = ("name","currency","base_rate_per_min","overtime_rate_per_min")

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("user","bike","station","start_at","end_at","status","planned_price","penalty_amount","total_price")
    list_filter = ("status","station")
    search_fields = ("user__username","bike__tag")

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("booking","amount","currency","status","created_at")

@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ("to","sent_at","booking")
    search_fields = ("to",)
