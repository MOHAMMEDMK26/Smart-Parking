from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import DiscountForm, NotificationForm, OwnerCreateForm, PeakPricingForm, SlotForm
from .models import CustomUser, DiscountCoupon, Notification, PeakPricingRule, Transaction
from django.shortcuts import get_object_or_404
from .forms import OwnerEditForm
from django.contrib.auth import logout
from .models import ParkingLot
from .forms import ParkingLotForm
from .models import Slot
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_dashboard')
            elif user.is_staff:
                return redirect('revenue_dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'core/login.html')

def is_super_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    owners = CustomUser.objects.filter(is_staff=True, is_superuser=False)
    return render(request, 'core/admin_dashboard.html', {'owners': owners})

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
@user_passes_test(is_super_admin)
def create_owner(request):
    if request.method == 'POST':
        form = OwnerCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_owners')
    else:
        form = OwnerCreateForm()
    return render(request, 'core/create_owner.html', {'form': form})

@login_required
@user_passes_test(is_super_admin)
def list_owners(request):
    owners = CustomUser.objects.filter(is_staff=True, is_superuser=False)
    return render(request, 'core/list_owners.html', {'owners': owners})


@login_required
@user_passes_test(is_super_admin)
def edit_owner(request, owner_id):
    user = get_object_or_404(CustomUser, id=owner_id)
    if request.method == 'POST':
        form = OwnerEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('list_owners')
    else:
        form = OwnerEditForm(instance=user)
    return render(request, 'core/edit_owner.html', {'form': form, 'owner': user})


@login_required
@user_passes_test(is_super_admin)
def toggle_owner_status(request, owner_id):
    user = get_object_or_404(CustomUser, id=owner_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('list_owners')

@login_required
@user_passes_test(lambda u: u.is_staff and not u.is_superuser)
def list_lots(request):
    lots = ParkingLot.objects.filter(owner=request.user)
    return render(request, 'core/list_lots.html', {'lots': lots})


@login_required
@user_passes_test(lambda u: u.is_staff and not u.is_superuser)
def add_lot(request):
    if request.method == 'POST':
        form = ParkingLotForm(request.POST)
        if form.is_valid():
            lot = form.save(commit=False)
            lot.owner = request.user
            lot.save()
            return redirect('list_lots')
    else:
        form = ParkingLotForm()
    return render(request, 'core/add_lot.html', {'form': form})


@login_required
@user_passes_test(lambda u: u.is_staff and not u.is_superuser)
def edit_lot(request, lot_id):
    lot = get_object_or_404(ParkingLot, id=lot_id, owner=request.user)
    if request.method == 'POST':
        form = ParkingLotForm(request.POST, instance=lot)
        if form.is_valid():
            form.save()
            return redirect('list_lots')
    else:
        form = ParkingLotForm(instance=lot)
    return render(request, 'core/edit_lot.html', {'form': form})


@login_required
@user_passes_test(lambda u: u.is_staff and not u.is_superuser)
def delete_lot(request, lot_id):
    lot = get_object_or_404(ParkingLot, id=lot_id, owner=request.user)
    lot.delete()
    return redirect('list_lots')

@login_required
@user_passes_test(lambda u: u.is_staff and not u.is_superuser)
def list_slots(request, lot_id):
    lot = get_object_or_404(ParkingLot, id=lot_id, owner=request.user)
    slots = Slot.objects.filter(lot=lot)
    return render(request, 'core/list_slots.html', {'lot': lot, 'slots': slots})


@login_required
@user_passes_test(lambda u: u.is_staff and not u.is_superuser)
def add_slot(request, lot_id):
    lot = get_object_or_404(ParkingLot, id=lot_id, owner=request.user)
    if request.method == 'POST':
        form = SlotForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.lot = lot
            slot.save()
            return redirect('list_slots', lot_id=lot.id)
    else:
        form = SlotForm()
    return render(request, 'core/add_slot.html', {'form': form, 'lot': lot})


@login_required
@user_passes_test(lambda u: u.is_staff and not u.is_superuser)
def toggle_slot_status(request, slot_id):
    slot = get_object_or_404(Slot, id=slot_id, lot__owner=request.user)
    slot.is_occupied = not slot.is_occupied
    slot.save()
    return redirect('list_slots', lot_id=slot.lot.id)

@login_required
@user_passes_test(lambda u: u.is_staff and not u.is_superuser)
def revenue_dashboard(request):
    lots = ParkingLot.objects.filter(owner=request.user)
    transactions = Transaction.objects.filter(lot__in=lots)

    today = timezone.now().date()
    this_week = today - timedelta(days=7)
    this_month = today - timedelta(days=30)

    daily_total = transactions.filter(timestamp__date=today).aggregate(Sum('amount'))['amount__sum'] or 0
    weekly_total = transactions.filter(timestamp__date__gte=this_week).aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_total = transactions.filter(timestamp__date__gte=this_month).aggregate(Sum('amount'))['amount__sum'] or 0

    return render(request, 'core/revenue_dashboard.html', {
        'daily': daily_total,
        'weekly': weekly_total,
        'monthly': monthly_total,
        'transactions': transactions.order_by('-timestamp')
    })


@login_required
@user_passes_test(lambda u: u.is_staff and not u.is_superuser)
def peak_pricing_rules(request, lot_id):
    lot = get_object_or_404(ParkingLot, id=lot_id, owner=request.user)
    rules = PeakPricingRule.objects.filter(lot=lot)
    if request.method == 'POST':
        form = PeakPricingForm(request.POST)
        if form.is_valid():
            rule = form.save(commit=False)
            rule.lot = lot
            rule.save()
            return redirect('peak_pricing_rules', lot_id=lot.id)
    else:
        form = PeakPricingForm()
    return render(request, 'core/peak_pricing.html', {'form': form, 'rules': rules, 'lot': lot})


@login_required
@user_passes_test(lambda u: u.is_staff and not u.is_superuser)
def discount_coupons(request, lot_id):
    lot = get_object_or_404(ParkingLot, id=lot_id, owner=request.user)
    coupons = DiscountCoupon.objects.filter(lot=lot)
    if request.method == 'POST':
        form = DiscountForm(request.POST)
        if form.is_valid():
            coupon = form.save(commit=False)
            coupon.lot = lot
            coupon.save()
            return redirect('discount_coupons', lot_id=lot.id)
    else:
        form = DiscountForm()
    return render(request, 'core/discounts.html', {'form': form, 'coupons': coupons, 'lot': lot})

@login_required
@user_passes_test(lambda u: u.is_staff and not u.is_superuser)
def toggle_coupon_status(request, coupon_id):
    coupon = get_object_or_404(DiscountCoupon, id=coupon_id, lot__owner=request.user)
    coupon.is_active = not coupon.is_active
    coupon.save()
    return redirect('discount_coupons', lot_id=coupon.lot.id)

@login_required
@user_passes_test(lambda u: u.is_staff and not u.is_superuser)
def edit_coupon(request, coupon_id):
    coupon = get_object_or_404(DiscountCoupon, id=coupon_id, lot__owner=request.user)
    if request.method == 'POST':
        form = DiscountForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            return redirect('discount_coupons', lot_id=coupon.lot.id)
    else:
        form = DiscountForm(instance=coupon)
    return render(request, 'core/edit_coupon.html', {'form': form, 'coupon': coupon})

@login_required
@user_passes_test(lambda u: u.is_staff and not u.is_superuser)
def delete_coupon(request, coupon_id):
    coupon = get_object_or_404(DiscountCoupon, id=coupon_id, lot__owner=request.user)
    lot_id = coupon.lot.id
    coupon.delete()
    return redirect('discount_coupons', lot_id=lot_id)

@login_required
@user_passes_test(lambda u: u.is_staff and not u.is_superuser)
def lot_notifications(request, lot_id):
    lot = get_object_or_404(ParkingLot, id=lot_id, owner=request.user)
    notifications = Notification.objects.filter(lot=lot).order_by('-created_at')
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.lot = lot
            note.save()
            return redirect('lot_notifications', lot_id=lot.id)
    else:
        form = NotificationForm()
    return render(request, 'core/notifications.html', {
        'form': form,
        'notifications': notifications,
        'lot': lot
    })

@login_required
@user_passes_test(lambda u: u.is_staff and not u.is_superuser)
def my_notifications(request):
    lots = ParkingLot.objects.filter(owner=request.user)
    notifications = Notification.objects.filter(lot__in=lots, hidden_for_owner=False).order_by('-created_at')
    return render(request, 'core/my_notifications.html', {'notifications': notifications})

@login_required
@user_passes_test(lambda u: u.is_staff and not u.is_superuser)
def edit_peak_pricing(request, rule_id):
    rule = get_object_or_404(PeakPricingRule, id=rule_id, lot__owner=request.user)
    if request.method == 'POST':
        form = PeakPricingForm(request.POST, instance=rule)
        if form.is_valid():
            form.save()
            return redirect('peak_pricing_rules', lot_id=rule.lot.id)
    else:
        form = PeakPricingForm(instance=rule)
    return render(request, 'core/edit_peak_pricing.html', {'form': form, 'rule': rule})

@login_required
@user_passes_test(lambda u: u.is_staff and not u.is_superuser)
def delete_peak_pricing(request, rule_id):
    rule = get_object_or_404(PeakPricingRule, id=rule_id, lot__owner=request.user)
    lot_id = rule.lot.id
    rule.delete()
    return redirect('peak_pricing_rules', lot_id=lot_id)

@login_required
@user_passes_test(lambda u: u.is_staff and not u.is_superuser)
def delete_notification(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, lot__owner=request.user)
    lot_id = notif.lot.id
    notif.delete()
    return redirect('lot_notifications', lot_id=lot_id)

@login_required
@user_passes_test(lambda u: u.is_staff and not u.is_superuser)
def hide_notification_from_my_view(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, lot__owner=request.user)
    notif.hidden_for_owner = True
    notif.save()
    return redirect('my_notifications')