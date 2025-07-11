from django import forms
from .models import CustomUser
from .models import ParkingSpace
from .models import ParkingLot
from .models import Slot
from .models import PeakPricingRule, DiscountCoupon
from .models import Notification

class OwnerCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    space_name = forms.CharField(label="Parking Space Name")
    space_location = forms.CharField(label="Location")
    space_capacity = forms.IntegerField(label="Capacity")

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'space_name', 'space_location', 'space_capacity']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_staff = True
        user.is_superuser = False
        if commit:
            user.save()
            # Create linked ParkingSpace
            ParkingSpace.objects.create(
                owner=user,
                name=self.cleaned_data["space_name"],
                location=self.cleaned_data["space_location"],
                capacity=self.cleaned_data["space_capacity"]
            )
        return user


class OwnerEditForm(forms.ModelForm):
    space_name = forms.CharField(label="Parking Space Name")
    space_location = forms.CharField(label="Location")
    space_capacity = forms.IntegerField(label="Capacity")

    class Meta:
        model = CustomUser
        fields = ['email']

    def __init__(self, *args, **kwargs):
        self.instance_user = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        if self.instance_user and hasattr(self.instance_user, 'parkingspace'):
            self.fields['space_name'].initial = self.instance_user.parkingspace.name
            self.fields['space_location'].initial = self.instance_user.parkingspace.location
            self.fields['space_capacity'].initial = self.instance_user.parkingspace.capacity

    def save(self, commit=True):
        user = super().save(commit=commit)
        ParkingSpace.objects.update_or_create(
            owner=user,
            defaults={
                'name': self.cleaned_data['space_name'],
                'location': self.cleaned_data['space_location'],
                'capacity': self.cleaned_data['space_capacity']
            }
        )
        return user

class ParkingLotForm(forms.ModelForm):
    class Meta:
        model = ParkingLot
        fields = ['name', 'description', 'type', 'rate_type', 'rate_amount']
        
class SlotForm(forms.ModelForm):
    class Meta:
        model = Slot
        fields = ['slot_number', 'is_occupied']
        
class PeakPricingForm(forms.ModelForm):
    class Meta:
        model = PeakPricingRule
        fields = ['day_of_week', 'start_hour', 'end_hour', 'multiplier']

class DiscountForm(forms.ModelForm):
    class Meta:
        model = DiscountCoupon
        fields = ['code', 'discount_percent', 'is_active']
        
class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['title', 'message', 'is_public']