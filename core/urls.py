from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('revenue/', views.revenue_dashboard, name='revenue_dashboard'),
    
    
    path('owners/create/', views.create_owner, name='create_owner'),
    path('owners/', views.list_owners, name='list_owners'),
    path('owners/edit/<int:owner_id>/', views.edit_owner, name='edit_owner'),
    path('owners/toggle/<int:owner_id>/', views.toggle_owner_status, name='toggle_owner_status'),
    
    path('lots/', views.list_lots, name='list_lots'),
    path('lots/add/', views.add_lot, name='add_lot'),
    path('lots/edit/<int:lot_id>/', views.edit_lot, name='edit_lot'),
    path('lots/delete/<int:lot_id>/', views.delete_lot, name='delete_lot'),
    
    path('lots/<int:lot_id>/slots/', views.list_slots, name='list_slots'),
    path('lots/<int:lot_id>/slots/add/', views.add_slot, name='add_slot'),
    path('slots/<int:slot_id>/toggle/', views.toggle_slot_status, name='toggle_slot_status'),
    
    path('lots/<int:lot_id>/peak/', views.peak_pricing_rules, name='peak_pricing_rules'),
    path('peak/edit/<int:rule_id>/', views.edit_peak_pricing, name='edit_peak_pricing'),
    path('peak/delete/<int:rule_id>/', views.delete_peak_pricing, name='delete_peak_pricing'),

    path('lots/<int:lot_id>/discounts/', views.discount_coupons, name='discount_coupons'),
    path('discounts/toggle/<int:coupon_id>/', views.toggle_coupon_status, name='toggle_coupon_status'),
    path('discounts/edit/<int:coupon_id>/', views.edit_coupon, name='edit_coupon'),
    path('discounts/delete/<int:coupon_id>/', views.delete_coupon, name='delete_coupon'),
    
    path('lots/<int:lot_id>/notifications/', views.lot_notifications, name='lot_notifications'),
    path('notifications/', views.my_notifications, name='my_notifications'),
    path('notifications/delete/<int:notif_id>/', views.delete_notification, name='delete_notification'),
    path('notifications/hide/<int:notif_id>/', views.hide_notification_from_my_view, name='hide_notification'),

]
