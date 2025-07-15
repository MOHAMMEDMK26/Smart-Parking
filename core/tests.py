from django.test import TestCase
from django.test import TestCase, Client
from django.urls import reverse
from .models import CustomUser, ParkingSpace, ParkingLot, Slot, PeakPricingRule, DiscountCoupon, Notification
from .forms import OwnerCreateForm, ParkingLotForm, SlotForm, PeakPricingForm, DiscountForm, NotificationForm
from django.test import TestCase, Client
from django.urls import reverse
from django.core.management import CommandError, call_command
from django.contrib.auth import get_user_model
from io import StringIO
from core.forms import OwnerEditForm
from core.models import CustomUserManager, ParkingSpace, ParkingLot
from core.views import is_super_admin
from django.test import TestCase, Client
from django.urls import reverse
from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model
from core.models import ParkingLot, Slot, PeakPricingRule, DiscountCoupon, Notification, ParkingSpace
from core.forms import OwnerCreateForm, OwnerEditForm
from django.utils import timezone
from datetime import timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import ParkingLot, Slot, DiscountCoupon, Notification, Transaction
from datetime import datetime
import builtins

User = get_user_model()

class FinalViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser(email="admin@z.com", password="admin123")
        self.owner = User.objects.create_user(email="owner@z.com", password="owner123", is_staff=True)
        self.lot = ParkingLot.objects.create(owner=self.owner, name="LotZ", description="Test", type="car", rate_type="hourly", rate_amount=5)
        self.slot = Slot.objects.create(lot=self.lot, slot_number="Z1")
        self.coupon = DiscountCoupon.objects.create(lot=self.lot, code="END10", discount_percent=10)
        self.note = Notification.objects.create(lot=self.lot, title="End", message="Final", is_public=True)

    def test_list_owners_view(self):
        self.client.login(email="admin@z.com", password="admin123")
        response = self.client.get(reverse("list_owners"))
        self.assertEqual(response.status_code, 200)

    def test_edit_coupon_view(self):
        self.client.login(email="owner@z.com", password="owner123")
        response = self.client.get(reverse("edit_coupon", args=[self.coupon.id]))
        self.assertEqual(response.status_code, 200)

    def test_delete_coupon_view(self):
        self.client.login(email="owner@z.com", password="owner123")
        response = self.client.get(reverse("delete_coupon", args=[self.coupon.id]))
        self.assertEqual(response.status_code, 302)

    def test_delete_notification_view(self):
        self.client.login(email="owner@z.com", password="owner123")
        response = self.client.get(reverse("delete_notification", args=[self.note.id]))
        self.assertEqual(response.status_code, 302)

    def test_hide_notification_view(self):
        self.client.login(email="owner@z.com", password="owner123")
        response = self.client.get(reverse("hide_notification", args=[self.note.id]))
        self.assertEqual(response.status_code, 302)

    def test_toggle_slot_status_view(self):
        self.client.login(email="owner@z.com", password="owner123")
        response = self.client.get(reverse("toggle_slot_status", args=[self.slot.id]))
        self.assertEqual(response.status_code, 302)

class TransactionModelTest(TestCase):
    def test_transaction_str_method(self):
        user = User.objects.create_user(email="txnuser@test.com", password="123", is_staff=True)
        lot = ParkingLot.objects.create(owner=user, name="LotTxn", description="Desc", type="car", rate_type="flat", rate_amount=20)
        slot = Slot.objects.create(lot=lot, slot_number="TX1")
        txn = Transaction.objects.create(lot=lot, slot=slot, amount=123.45, timestamp=datetime(2025, 1, 1, 14, 0), note="Test")
        self.assertIn("₹123.45", str(txn))

class ManagePyCoverageTest(TestCase):
    def test_manage_py_main_import_error(self):
        original_import = builtins.__import__

        def mock_import(name, *args):
            if name == "django":
                raise ImportError("mock error")
            return original_import(name, *args)

        builtins.__import__ = mock_import
        try:
            from manage import main
            with self.assertRaises(ImportError):
                main()
        finally:
            builtins.__import__ = original_import


class ViewFullCoverageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser(email="admin@x.com", password="admin123")
        self.owner = User.objects.create_user(email="owner@x.com", password="owner123", is_staff=True)
        self.space = ParkingSpace.objects.create(owner=self.owner, name="Space1", location="City", capacity=10)
        self.lot = ParkingLot.objects.create(owner=self.owner, name="LotX", description="Desc", type="car", rate_type="flat", rate_amount=10.00)
        self.slot = Slot.objects.create(lot=self.lot, slot_number="S1", is_occupied=False)
        self.coupon = DiscountCoupon.objects.create(lot=self.lot, code="DISC10", discount_percent=10)
        self.rule = PeakPricingRule.objects.create(lot=self.lot, day_of_week="Monday", start_hour=8, end_hour=10, multiplier=1.5)
        self.note = Notification.objects.create(lot=self.lot, title="Note", message="msg", is_public=True)

    def test_create_owner_post(self):
        self.client.login(email="admin@x.com", password="admin123")
        data = {
            "email": "new@x.com",
            "password": "pass123",
            "space_name": "Lot A",
            "space_location": "Loc A",
            "space_capacity": 20
        }
        response = self.client.post(reverse("create_owner"), data)
        self.assertEqual(response.status_code, 302)

    def test_edit_owner(self):
        self.client.login(email="admin@x.com", password="admin123")
        response = self.client.get(reverse("edit_owner", args=[self.owner.id]))
        self.assertEqual(response.status_code, 200)

    def test_toggle_owner_status(self):
        self.client.login(email="admin@x.com", password="admin123")
        response = self.client.get(reverse("toggle_owner_status", args=[self.owner.id]))
        self.assertEqual(response.status_code, 302)

    def test_add_edit_delete_lot(self):
        self.client.login(email="owner@x.com", password="owner123")
        add_resp = self.client.post(reverse("add_lot"), {
            "name": "LotY", "description": "Desc", "type": "car", "rate_type": "daily", "rate_amount": 5.00
        })
        self.assertEqual(add_resp.status_code, 302)

        edit_resp = self.client.post(reverse("edit_lot", args=[self.lot.id]), {
            "name": "UpdatedLot", "description": "NewDesc", "type": "car", "rate_type": "daily", "rate_amount": 15.00
        })
        self.assertEqual(edit_resp.status_code, 302)

        del_resp = self.client.get(reverse("delete_lot", args=[self.lot.id]))
        self.assertEqual(del_resp.status_code, 302)

    def test_slot_views(self):
        self.client.login(email="owner@x.com", password="owner123")
        self.client.post(reverse("add_slot", args=[self.lot.id]), {
            "slot_number": "S2", "is_occupied": False
        })
        self.client.get(reverse("toggle_slot_status", args=[self.slot.id]))

    def test_coupon_views(self):
        self.client.login(email="owner@x.com", password="owner123")
        self.client.post(reverse("discount_coupons", args=[self.lot.id]), {
            "code": "SAVE5", "discount_percent": 5, "is_active": True
        })
        self.client.get(reverse("toggle_coupon_status", args=[self.coupon.id]))
        self.client.post(reverse("edit_coupon", args=[self.coupon.id]), {
            "code": "SAVE5", "discount_percent": 10, "is_active": False
        })
        self.client.get(reverse("delete_coupon", args=[self.coupon.id]))

    def test_peak_views(self):
        self.client.login(email="owner@x.com", password="owner123")
        self.client.post(reverse("peak_pricing_rules", args=[self.lot.id]), {
            "day_of_week": "Tuesday", "start_hour": 9, "end_hour": 18, "multiplier": 2.0
        })
        self.client.post(reverse("edit_peak_pricing", args=[self.rule.id]), {
            "day_of_week": "Wednesday", "start_hour": 7, "end_hour": 8, "multiplier": 1.2
        })
        self.client.get(reverse("delete_peak_pricing", args=[self.rule.id]))

    def test_notification_views(self):
        self.client.login(email="owner@x.com", password="owner123")
        self.client.post(reverse("lot_notifications", args=[self.lot.id]), {
            "title": "New Title", "message": "Test", "is_public": True
        })
        self.client.get(reverse("my_notifications"))
        self.client.get(reverse("delete_notification", args=[self.note.id]))
        self.client.get(reverse("hide_notification", args=[self.note.id]))


class OwnerCreateFormTests(TestCase):
    def test_save_logic(self):
        form_data = {
            'email': 'formtest@x.com',
            'password': 'test123',
            'space_name': 'Form Lot',
            'space_location': 'Test Loc',
            'space_capacity': 15
        }
        form = OwnerCreateForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.parkingspace.name, "Form Lot")


class OwnerEditFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="edituser@test.com", password="pass123", is_staff=True)
        ParkingSpace.objects.create(owner=self.user, name="Old Lot", location="Old Place", capacity=5)

    def test_owner_edit_form_init_and_save(self):
        form_data = {
            "email": "edituser@test.com",
            "space_name": "Updated Lot",
            "space_location": "New Place",
            "space_capacity": 20
        }
        form = OwnerEditForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())
        form.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.parkingspace.name, "Updated Lot")
        self.assertEqual(self.user.parkingspace.location, "New Place")
        self.assertEqual(self.user.parkingspace.capacity, 20)


class CustomUserManagerTests(TestCase):
    def test_create_user_and_superuser(self):
        user = User.objects.create_user(email="user@test.com", password="12345")
        self.assertTrue(user.check_password("12345"))
        self.assertFalse(user.is_superuser)
        superuser = User.objects.create_superuser(email="admin@test.com", password="adminpass")
        self.assertTrue(superuser.is_superuser)


class ViewsAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser(email="super@test.com", password="admin123")
        self.owner = User.objects.create_user(email="staff@test.com", password="owner123", is_staff=True)
        self.lot = ParkingLot.objects.create(owner=self.owner, name="Lot", description="Test", type="car", rate_type="flat", rate_amount=10)

    def test_is_super_admin(self):
        self.assertTrue(is_super_admin(self.superuser))
        self.assertFalse(is_super_admin(self.owner))

    def test_admin_dashboard_redirects_unauthenticated(self):
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_create_owner_page_superuser(self):
        self.client.login(email="super@test.com", password="admin123")
        response = self.client.get(reverse('create_owner'))
        self.assertEqual(response.status_code, 200)

    def test_list_lots_requires_login(self):
        response = self.client.get(reverse('list_lots'))
        self.assertEqual(response.status_code, 302)  # redirect to login


class ManagePyTests(TestCase):
    def test_manage_py_invalid_command(self):
        with self.assertRaises(CommandError):
            call_command("nonexistentcommand")

class BasicModelTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email='owner@test.com', password='pass123', is_staff=True)
        self.space = ParkingSpace.objects.create(owner=self.user, name='Main Lot', location='Downtown', capacity=30)
        self.lot = ParkingLot.objects.create(owner=self.user, name='Lot A', description='Open space', type='car', rate_type='hourly', rate_amount=10.0)
        self.slot = Slot.objects.create(lot=self.lot, slot_number='A1')
        self.coupon = DiscountCoupon.objects.create(lot=self.lot, code='SAVE10', discount_percent=10)
        self.peak = PeakPricingRule.objects.create(lot=self.lot, day_of_week='Monday', start_hour=9, end_hour=17, multiplier=1.5)
        self.note = Notification.objects.create(lot=self.lot, title='Alert', message='Maintenance scheduled')

    def test_user_str(self):
        self.assertEqual(str(self.user), 'owner@test.com')

    def test_space_str(self):
        self.assertIn('Main Lot', str(self.space))

    def test_lot_str(self):
        self.assertIn('Lot A', str(self.lot))

    def test_slot_str(self):
        self.assertIn('Slot A1', str(self.slot))

    def test_coupon_str(self):
        self.assertIn('SAVE10', str(self.coupon))

    def test_peak_str(self):
        self.assertIn('Monday', str(self.peak))

    def test_notification_str(self):
        self.assertIn('Alert', str(self.note))


class FormValidationTests(TestCase):
    def test_owner_create_form_valid(self):
        form_data = {
            'email': 'newowner@test.com',
            'password': 'newpass',
            'space_name': 'Test Lot',
            'space_location': 'City Center',
            'space_capacity': 25
        }
        form = OwnerCreateForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_lot_form(self):
        user = CustomUser.objects.create_user(email='owner2@test.com', password='pass123', is_staff=True)
        form = ParkingLotForm(data={'name': 'Lot X', 'description': 'Test Desc', 'type': 'car', 'rate_type': 'daily', 'rate_amount': 50})
        self.assertTrue(form.is_valid())

    def test_slot_form(self):
        form = SlotForm(data={'slot_number': 'S1', 'is_occupied': False})
        self.assertTrue(form.is_valid())

    def test_peak_pricing_form(self):
        form = PeakPricingForm(data={'day_of_week': 'Tuesday', 'start_hour': 8, 'end_hour': 18, 'multiplier': 2.0})
        self.assertTrue(form.is_valid())

    def test_discount_form(self):
        form = DiscountForm(data={'code': 'NEW10', 'discount_percent': 10, 'is_active': True})
        self.assertTrue(form.is_valid())

    def test_notification_form(self):
        form = NotificationForm(data={'title': 'Test Note', 'message': 'Important!', 'is_public': True})
        self.assertTrue(form.is_valid())


class AuthAndViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = CustomUser.objects.create_superuser(email='admin@test.com', password='admin123')
        self.owner = CustomUser.objects.create_user(email='staff@test.com', password='owner123', is_staff=True)
        ParkingSpace.objects.create(owner=self.owner, name='Space 1', location='Zone 1', capacity=10)

    def test_login_success(self):
        response = self.client.post(reverse('login'), {'email': 'admin@test.com', 'password': 'admin123'})
        self.assertEqual(response.status_code, 302)

    def test_login_fail(self):
        response = self.client.post(reverse('login'), {'email': 'wrong@test.com', 'password': 'nopass'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h2>Login</h2>')

    def test_admin_dashboard_access(self):
        self.client.login(email='admin@test.com', password='admin123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.client.login(email='admin@test.com', password='admin123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    def test_owner_dashboard_redirect(self):
        self.client.login(email='staff@test.com', password='owner123')
        response = self.client.get(reverse('revenue_dashboard'))
        self.assertEqual(response.status_code, 200)

