from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('menu/', views.menu, name='menu'),
    path('order/', views.order, name='order'),
    path('reception/', views.reception, name='reception'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('accounts/', views.signup_view, name='accounts'),
    path('accounts/profile/', views.profile, name='profile'),
    path('profile/<str:username>/', views.public_profile, name='public_profile'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/admin/toggle-staff/<int:user_id>/', views.toggle_staff, name='toggle_staff'),
    path('dashboard/admin/update-order/<int:order_id>/<str:status>/', views.update_order_status, name='update_order_status'),
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('api/place-order/', views.place_order, name='place_order'),
    path('qr-payment/<int:order_id>/', views.qr_payment, name='qr_payment'),
    path('api/mark-received/<int:order_id>/', views.mark_received, name='mark_received'),
    path('api/mark-paid/<int:order_id>/', views.mark_paid, name='mark_paid'),
    path('api/cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('api/delete-order/<int:order_id>/', views.delete_order, name='delete_order'),
]
