# Django imports
from django.shortcuts import render, redirect  
from django.contrib.auth import login, logout  
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm  
from django.contrib.auth.decorators import login_required, user_passes_test  
from django.contrib import messages  
from django import forms 
from django.contrib.auth.models import User  
from django.http import JsonResponse, HttpResponseBadRequest  
from django.conf import settings  
from django.views.decorators.http import require_POST  
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Order, Profile, MenuItem


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'email')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'avatar', 'location', 'website', 'phone')


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


def public_profile(request, username):
    try:
        profile_user = User.objects.get(username=username)
        profile = profile_user.profile
        return render(request, 'public_profile.html', {'profile_user': profile_user, 'profile': profile})
    except User.DoesNotExist:
        return redirect('index')


# Custom signup form to include role selection
class SignupForm(UserCreationForm):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('super_admin', 'Super Admin'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect, initial='customer')
    admin_code = forms.CharField(required=False, widget=forms.PasswordInput, help_text='Provide the super admin code.')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1', 'password2')

    def clean(self):
        data = super().clean()
        role = data.get('role', 'customer')
        code = data.get('admin_code', '').strip()
        if role == 'super_admin':
            # enforce single super admin and correct code
            if User.objects.filter(is_superuser=True).exists():
                self.add_error('role', 'A super admin already exists.')
            expected = getattr(settings, 'ADMIN_SIGNUP_CODE', '')
            if not code or code != expected:
                self.add_error('admin_code', 'Invalid admin code.')
        return data


# Page views
def index(request):
    return render(request, 'index.html')


def menu(request):
    menu_items = MenuItem.objects.filter(available=True)
    # Map item names to image files
    image_map = {
        'Ema Datshi': 'emadatsi.jpg',
        'Fried Momo': 'fried momo.avif',
        'Sikam Datshi': 'sikam datsi.jpg',
        'Kewa Datshi': 'kewa datsi.png',
        'Vegetable Curry': 'vegetablecurry.jpg',
        'Chicken Fried Rice': 'chicken.jpg',
        'Spicy Noodles': 'spicy.jpg',
        'Seasonal Salad': 'salad.jpg',
    }
    for item in menu_items:
        item.image_url = image_map.get(item.name, 'default.jpg')
    return render(request, 'menu.html', {'menu_items': menu_items})


@login_required
def order(request):
    return render(request, 'order.html')


def reception(request):
    orders = Order.objects.order_by('-created_at')[:50]
    user_orders = []
    if request.user.is_authenticated:
        user_orders = Order.objects.filter(user=request.user, payment_status='unpaid').order_by('-created_at')
        if request.method == 'POST' and 'payment_method' in request.POST:
            order_id = request.POST.get('order_id')
            payment_method = request.POST.get('payment_method')
            if order_id and payment_method in ['qr_payment', 'cash']:
                try:
                    order = Order.objects.get(pk=order_id, user=request.user, payment_status='unpaid')
                    order.payment_method = payment_method
                    if payment_method == 'qr_payment':
                        order.payment_status = 'pending_verification'
                    order.save()
                    messages.success(request, f'Payment method set to {order.get_payment_method_display()}.')
                    return redirect('reception')
                except Order.DoesNotExist:
                    messages.error(request, 'Order not found.')
    return render(request, 'reception.html', {'orders': orders, 'user_orders': user_orders})


def aboutus(request):
    return render(request, 'aboutus.html')


# Authentication: combined login / signup page
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role', 'customer')
            user = form.save(commit=False)
            if role == 'super_admin':
                user.is_staff = True
                user.is_superuser = True
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
            return redirect('dashboard')
        else:
            pass  
    return render(request, 'login.html', {'login_form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('index')


def _is_admin(user):
    return user.is_superuser


@login_required
def dashboard(request):
    if _is_admin(request.user):
        return redirect('admin_dashboard')
    return redirect('customer_dashboard')


@login_required
@user_passes_test(_is_admin)
def admin_dashboard(request):
    users = User.objects.all().order_by('username')
    orders = Order.objects.order_by('-created_at')[:50]  # recent orders
    for order in orders:
        try:
            items = json.loads(order.items)
            item_names = [item['title'] for item in items]
            order.item_names = ', '.join(item_names)
        except (json.JSONDecodeError, KeyError):
            order.item_names = order.items
    return render(request, 'admin_dashboard.html', {'users': users, 'orders': orders})


@require_POST
@login_required
@user_passes_test(_is_admin)
def update_order_status(request, order_id, status):
    try:
        order = Order.objects.get(pk=order_id)
        if status in ['received', 'cancelled']:
            order.status = status
            order.save()
            messages.success(request, f'Order {order.id} marked as {status}.')
        else:
            messages.error(request, 'Invalid status.')
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
    return redirect('admin_dashboard')


@require_POST
@login_required
@user_passes_test(_is_admin)
def delete_order(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
        order.delete()
        messages.success(request, f'Order {order_id} deleted successfully.')
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
    return redirect('reception')


@require_POST
@login_required
@user_passes_test(_is_admin)
def toggle_staff(request, user_id):
    # Role promotion/demotion disabled to enforce single super admin model.
    messages.info(request, 'Role changes are disabled; single super admin is enforced.')
    return redirect('admin_dashboard')


@login_required
def customer_dashboard(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:10]
    return render(request, 'customer_dashboard.html', {'orders': orders})


@csrf_exempt
@require_POST
def place_order(request):
    # Require authenticated customer with a display name
    if not request.user.is_authenticated:
        return JsonResponse({'ok': False, 'error': 'Please log in or create an account before ordering.'}, status=403)
    display_name = (request.user.first_name or '').strip()
    if not display_name:
        return JsonResponse({'ok': False, 'error': 'Please set your display name in your profile before ordering.'}, status=400)
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')
    items = payload.get('items', [])
    total = payload.get('total', 0)
    user = request.user
    order = Order.objects.create(user=user, items=json.dumps(items), total=total, status='on_the_way', payment_status='unpaid')
    return JsonResponse({'ok': True, 'order_id': order.id, 'redirect': f'/qr-payment/{order.id}/', 'message': 'Order placed. Proceed to payment.'})


def qr_payment(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return redirect('index')
    if request.method == 'POST':
        transaction_ref = request.POST.get('transaction_ref', '').strip()
        order.payment_method = 'qr_payment'
        order.payment_status = 'pending_verification'
        order.transaction_ref = transaction_ref if transaction_ref else None
        order.save()
        messages.success(request, 'Payment submitted for verification. Please wait in reception.')
        return redirect('reception')
    return render(request, 'qr_payment.html', {'order': order})


@require_POST
@login_required
def mark_received(request, order_id):
    if not _is_admin(request.user):
        return JsonResponse({'ok': False, 'error': 'Unauthorized'}, status=403)
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
def mark_paid(request, order_id):
    if not _is_admin(request.user):
        return JsonResponse({'ok': False, 'error': 'Unauthorized'}, status=403)
    try:
        order = Order.objects.get(pk=order_id)
        order.payment_status = 'paid'
        order.save()
        return JsonResponse({'ok': True, 'order_id': order.id, 'message': 'Order marked as paid.'})
    except Order.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Order not found'}, status=404)


@require_POST
@login_required
def cancel_order(request, order_id):
    if not _is_admin(request.user):
        return JsonResponse({'ok': False, 'error': 'Unauthorized'}, status=403)
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


