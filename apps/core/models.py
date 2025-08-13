from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class Station(models.Model):
    name = models.CharField(max_length=120)
    address = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Bike(models.Model):
    station = models.ForeignKey(Station, on_delete=models.PROTECT, related_name="bikes")
    tag = models.CharField(max_length=50, unique=True)  # fiziksel etiket/kod
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.tag} @ {self.station.name}"


class PricingPlan(models.Model):
    name = models.CharField(max_length=80, default="Default")
    currency = models.CharField(max_length=8, default="TRY")
    base_rate_per_min = models.DecimalField(max_digits=8, decimal_places=2)       # planlanan süre
    overtime_rate_per_min = models.DecimalField(max_digits=8, decimal_places=2)   # gecikme

    def __str__(self):
        return f"{self.name} ({self.currency})"


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        ACTIVE = "ACTIVE", "Active"
        RETURNED = "RETURNED", "Returned"
        CANCELED = "CANCELED", "Canceled"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="bookings")
    station = models.ForeignKey(Station, on_delete=models.PROTECT, related_name="bookings")
    bike = models.ForeignKey(Bike, on_delete=models.PROTECT, related_name="bookings", null=True, blank=True)

    pricing = models.ForeignKey(PricingPlan, on_delete=models.PROTECT)

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()

    # Kullanıcının bastığı teslim butonundaki zaman:
    actual_return_at_user = models.DateTimeField(null=True, blank=True)
    # Görevli onayladığında kesin kabul edilen zaman:
    actual_return_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    planned_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    penalty_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.end_at <= self.start_at:
            raise ValidationError("Bitiş tarihi başlangıçtan sonra olmalı.")

    def __str__(self):
        bike = self.bike.tag if self.bike_id else "TBD"
        return f"{self.user} | {bike} | {self.start_at}→{self.end_at}"

    @property
    def is_late(self):
        if self.actual_return_at and self.end_at:
            return self.actual_return_at > self.end_at
        return False


class Payment(models.Model):
    class Status(models.TextChoices):
        INITIATED = "INITIATED", "Initiated"
        PAID = "PAID", "Paid"
        FAILED = "FAILED", "Failed"

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="payment")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=8, default="TRY")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.INITIATED)
    created_at = models.DateTimeField(auto_now_add=True)


class SMSLog(models.Model):
    to = models.CharField(max_length=32)
    message = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now)
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name="sms_logs")
