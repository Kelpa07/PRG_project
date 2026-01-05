# Django imports
from django.shortcuts import render, redirect  # type: ignore
from django.contrib.auth import login, logout  # type: ignore
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm  # type: ignore
from django.contrib.auth.decorators import login_required, user_passes_test  # type: ignore
from django.contrib import messages  # type: ignore
from django import forms  # type: ignore
from django.contrib.auth.models import User  # type: ignore
from django.http import JsonResponse, HttpResponseBadRequest  # type: ignore
from django.conf import settings  # type: ignore
from django.views.decorators.http import require_POST  # type: ignore
import json
from .models import Order, Profile


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'email')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'avatar')


@login_required
def profile(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    if request.method == 'POST':
        uform = UserForm(request.POST, instance=user)
        pform = ProfileForm(request.POST, request.FILES, instance=profile)
        if uform.is_valid() and pform.is_valid():
            uform.save()
            pform.save()
            messages.success(request, 'Profile updated.')
            return redirect('profile')
    else:
        uform = UserForm(instance=user)
        pform = ProfileForm(instance=profile)
    return render(request, 'account_profile.html', {'user_form': uform, 'profile_form': pform})


# Custom signup form to include role selection
class SignupForm(UserCreationForm):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('admin', 'Admin (staff)'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect, initial='customer')
    admin_code = forms.CharField(required=False, widget=forms.PasswordInput, help_text='Secret code required to create admin accounts')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1', 'password2')


# Page views
def index(request):
    return render(request, 'index.html')


def menu(request):
    return render(request, 'menu.html')


def order(request):
    return render(request, 'order.html')


def reception(request):
    orders = Order.objects.order_by('-created_at')[:50]
    return render(request, 'reception.html', {'orders': orders})


def aboutus(request):
    return render(request, 'aboutus.html')


# Authentication: combined login / signup page
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.pop('role', 'customer')
            admin_code = form.cleaned_data.pop('admin_code', '')
            # If admin role requested, require correct admin code
            if role == 'admin':
                expected = getattr(settings, 'ADMIN_SIGNUP_CODE', None)
                if not expected or admin_code != expected:
                    form.add_error('admin_code', 'Invalid admin code')
                    messages.error(request, 'Sign up failed. Invalid admin code.')
                    return render(request, 'signup.html', {'signup_form': form})
            user = form.save()
            # set staff for admin role
            if role == 'admin':
                user.is_staff = True
                user.save()
            login(request, user)
            messages.success(request, f'Account created. Welcome, {user.username}!')
            # Redirect new users to their profile page where they can add info
            return redirect('profile')
        else:
            messages.error(request, 'Sign up failed. Please correct the errors below.')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'signup_form': form})


def login_view(request):
    form = AuthenticationForm(request)
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Login failed. Check your username and password.')
    return render(request, 'login.html', {'login_form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('index')


def _is_admin(user):
    return user.is_staff


@login_required
def dashboard(request):
    # redirect to role-specific dashboard
    if request.user.is_staff:
        return redirect('admin_dashboard')
    return redirect('customer_dashboard')


@login_required
@user_passes_test(_is_admin)
def admin_dashboard(request):
    users = User.objects.all().order_by('username')
    return render(request, 'admin_dashboard.html', {'users': users})


@require_POST
@login_required
@user_passes_test(_is_admin)
def toggle_staff(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        user.is_staff = not user.is_staff
        user.save()
        messages.success(request, f'User {user.username} role updated.')
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
    return redirect('admin_dashboard')


@login_required
def customer_dashboard(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:10]
    return render(request, 'customer_dashboard.html', {'orders': orders})


@require_POST
def place_order(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')
    items = payload.get('items', [])
    total = payload.get('total', 0)
    user = request.user if request.user.is_authenticated else None
    order = Order.objects.create(user=user, items=json.dumps(items), total=total, status='on_the_way')
    return JsonResponse({'ok': True, 'order_id': order.id, 'message': 'Order placed. Order is on the way — please wait in reception.'})


@require_POST
def mark_received(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Order not found'}, status=404)
    order.status = 'received'
    order.save()
    # If this was submitted from a normal form POST, redirect back to reception
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'order_id': order.id, 'message': 'Order marked as received.'})
    return redirect('reception')


@require_POST
def cancel_order(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Order not found'}, status=404)
    # Only allow cancelling orders that are on the way
    if order.status == 'on_the_way':
        order.status = 'cancelled'
        order.save()
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({'ok': True, 'order_id': order.id, 'message': 'Order cancelled.'})
        return redirect('reception')
    else:
        return JsonResponse({'ok': False, 'error': 'Order cannot be cancelled.'}, status=400)


