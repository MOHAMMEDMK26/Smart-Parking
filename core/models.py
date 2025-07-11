from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.conf import settings
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
class ParkingSpace(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} ({self.location})"
    
class ParkingLot(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    type = models.CharField(max_length=50, choices=[
        ('2-wheeler', '2-wheeler'),
        ('car', 'Car'),
        ('EV', 'EV'),
        ('VIP', 'VIP'),
    ])
    rate_type = models.CharField(max_length=20, choices=[
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('flat', 'Flat'),
    ])
    rate_amount = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.type})"

class Slot(models.Model):
    lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
    slot_number = models.CharField(max_length=20)
    is_occupied = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.lot.name} - Slot {self.slot_number}"

class Transaction(models.Model):
    lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)
    note = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.lot.name} - ₹{self.amount} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    
class PeakPricingRule(models.Model):
    lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10)  # e.g., "Monday"
    start_hour = models.IntegerField()  # 0–23
    end_hour = models.IntegerField()    # 0–23
    multiplier = models.FloatField(default=1.0)  # e.g., 1.5x

    def __str__(self):
        return f"{self.lot.name} - {self.day_of_week} {self.start_hour}:00 to {self.end_hour}:00"

class DiscountCoupon(models.Model):
    lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
    code = models.CharField(max_length=20, unique=True)
    discount_percent = models.IntegerField()  # e.g., 10 for 10%
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.discount_percent}%"

class Notification(models.Model):
    lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    hidden_for_owner = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - ({'Public' if self.is_public else 'Internal'})"