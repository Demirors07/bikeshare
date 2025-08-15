from decimal import Decimal
from django.db.models import Q
from django.utils import timezone
from .models import Bike, Booking, SMSLog

def minutes_between(a, b):
    return max(0, int((b - a).total_seconds() // 60))

def compute_planned_price(pricing, start_at, end_at):
    mins = minutes_between(start_at, end_at)
    return Decimal(mins) * pricing.base_rate_per_min

def compute_penalty(pricing, end_at, actual_return_at):
    if actual_return_at <= end_at:
        return Decimal("0.00")
    late_mins = minutes_between(end_at, actual_return_at)
    return Decimal(late_mins) * pricing.overtime_rate_per_min

def find_available_bike(station, start_at, end_at):
    """
    Verilen istasyonda, [start_at, end_at] aralığı ile çakışmayan bir bisiklet döndürür.
    Çakışma: rezervasyonun CONFIRMED/ACTIVE/RETURNED (gerçek dönüş zamanı end_at'tan önce olsa bile plan içinde işgal sayılır)
    """
    busy_bike_ids = Booking.objects.filter(
        status__in=["CONFIRMED", "ACTIVE"],
        bike__isnull=False,
        bike__station=station,
        start_at__lt=end_at,
        end_at__gt=start_at,
    ).values_list("bike_id", flat=True)

    return Bike.objects.filter(
        station=station,
        is_active=True
    ).exclude(id__in=list(busy_bike_ids)).first()

def send_sms(phone, message, booking=None):
    # Burada gerçek bir SMS sağlayıcısı entegre edebilirsiniz (Twilio, NetGSM, vs.)
    SMSLog.objects.create(to=phone, message=message, booking=booking)
    return True
