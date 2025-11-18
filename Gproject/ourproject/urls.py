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
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('api/place-order/', views.place_order, name='place_order'),
    path('api/mark-received/<int:order_id>/', views.mark_received, name='mark_received'),
    path('api/cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
]
