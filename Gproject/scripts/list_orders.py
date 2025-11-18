import os
import django
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Gproject.settings')
django.setup()

from ourproject.models import Order

orders = Order.objects.order_by('-created_at')[:20]
print(f'Found {orders.count()} orders:')
for o in orders:
    print(f'ID={o.id} status={o.status} total={o.total} user={o.user} created={o.created_at}')
    try:
        items = o.items
        # items may be JSON string; try to load
        import json
        try:
            items = json.loads(items)
        except Exception:
            pass
    except Exception:
        items = o.items
    print(' items:', items)
