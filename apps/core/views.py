from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.urls import reverse
from django.db import transaction

from .forms import BookingForm, ReturnConfirmForm, SignUpForm, LoginForm
from .models import Booking, Payment
from .services import (
    find_available_bike,
    compute_planned_price,
    compute_penalty,
    send_sms,
)

# 🏠 Anasayfa
def home(request):
    return render(request, 'core/home.html')


# 🔑 Giriş yap
def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, 'Kullanıcı adı veya şifre yanlış.')

    return render(request, 'core/login.html', {'form': form})

# 🚪 Çıkış yap
def logout_view(request):
    logout(request)
    return redirect('home')

# 📅 Rezervasyon (Login zorunlu)
#@login_required(login_url='login')
#def booking_view(request):
 #   return render(request, 'booking.html')

# ℹ️ Hakkımızda
def about_view(request):
    return render(request, 'core/about.html')

# ❓ Sıkça Sorulan Sorular
def contact_view(request):
    return render(request, 'core/contact.html')

# ❓ Sıkça Sorulan Sorular
def faq_view(request):
    return render(request, 'core/faq.html')

@login_required
def booking_create(request):
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            station = form.cleaned_data["station"]
            pricing = form.cleaned_data["pricing"]
            start_at = form.cleaned_data["start_at"]
            end_at = form.cleaned_data["end_at"]

            with transaction.atomic():
                bike = find_available_bike(station, start_at, end_at)
                if not bike:
                    messages.error(request, "Bu zaman aralığı için uygun bisiklet bulunamadı.")
                    return render(request, "core/booking_create.html", {"form": form})

                booking = Booking.objects.create(
                    user=request.user,
                    station=station,
                    bike=bike,
                    pricing=pricing,
                    start_at=start_at,
                    end_at=end_at,
                    planned_price=compute_planned_price(pricing, start_at, end_at),
                    total_price=Decimal("0.00"),
                    status=Booking.Status.CONFIRMED,
                )

                # (Opsiyonel) Ön ödeme oluşturma – burada sadece başlatıyoruz.
                Payment.objects.create(
                    booking=booking,
                    amount=booking.planned_price,
                    currency=pricing.currency
                )

                # SMS (mock)
                phone = getattr(request.user, "phone", None) or "5550000000"
                send_sms(
                    phone,
                    f"Rezervasyon onaylandı. Bisiklet: {bike.tag}. {start_at:%d.%m %H:%M} - {end_at:%d.%m %H:%M}",
                    booking=booking
                )

                messages.success(request, "Rezervasyon onaylandı! SMS ile bilgi gönderildi.")
                return JsonResponse({
                    "success": True,
                    "redirect_url": reverse("my_bookings")  # ✅ buraya yönlendirilecek
                })
    else:
        form = BookingForm()
        html = render_to_string("core/partials/booking_form.html", {"form": form}, request=request)
        return JsonResponse({"html": html})

    return render(request, "core/booking_create.html", {"form": form})


@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, "core/booking_detail.html", {"booking": booking})


@login_required
def booking_mark_returned_by_user(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status not in [Booking.Status.CONFIRMED, Booking.Status.ACTIVE]:
        messages.error(request, "Bu rezervasyon teslim edilmeye uygun değil.")
        return redirect("booking_detail", booking_id=booking.id)

    booking.actual_return_at_user = timezone.now()
    booking.status = Booking.Status.ACTIVE  # sürüş bitti ama görevli onayı bekleniyor
    booking.save(update_fields=["actual_return_at_user", "status"])

    messages.success(request, "Teslim talebiniz alındı. Görevli onayı bekleniyor.")
    return redirect("my_bookings")


def is_staff(user):
    return user.is_staff


@user_passes_test(is_staff)
def staff_confirm_return(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == "POST":
        form = ReturnConfirmForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                booking.actual_return_at = timezone.now()
                penalty = compute_penalty(booking.pricing, booking.end_at, booking.actual_return_at)
                booking.penalty_amount = penalty
                booking.total_price = (booking.planned_price or Decimal("0.00")) + penalty
                booking.status = Booking.Status.RETURNED
                booking.save()

                # Ödeme kaydını güncelle (mock)
                if hasattr(booking, "payment"):
                    booking.payment.amount = booking.total_price
                    booking.payment.status = Payment.Status.PAID
                    booking.payment.save()

            messages.success(request, f"Teslim onaylandı. Toplam ücret: {booking.total_price} {booking.pricing.currency}")
            return redirect("staff_booking_view", booking_id=booking.id)
    else:
        form = ReturnConfirmForm()

    return render(request, "core/staff_confirm_return.html", {"booking": booking, "form": form})


@user_passes_test(is_staff)
def staff_booking_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, "core/staff_booking_view.html", {"booking": booking})

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # kayıt olur olmaz giriş yap
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, "core/signup.html", {"form": form})

@login_required
def my_bookings_view(request):
    active_bookings = Booking.objects.filter(user=request.user, status=Booking.Status.CONFIRMED)
    past_bookings = Booking.objects.filter(
        user=request.user,
        status__in=[Booking.Status.RETURNED, Booking.Status.CANCELED]
    )

    return render(request, 'core/includes/my_bookings.html', {
        'active_bookings': active_bookings,
        'past_bookings': past_bookings
    })

