from .models import Order

def reception_flag(request):
    try:
        has_received = Order.objects.filter(status='received').exists()
    except Exception:
        has_received = False
    return {'reception_has_received': has_received}
