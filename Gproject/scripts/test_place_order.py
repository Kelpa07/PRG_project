import os
import django
import json
import sys
from pathlib import Path

# Ensure project root is on sys.path so the 'Gproject' package is importable
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Gproject.settings')
django.setup()

from django.test import Client

client = Client()

payload = {
    'items': [
        {'title': 'Test Item', 'price': 10, 'qty': 2}
    ],
    'total': 20
}

resp = client.post('/api/place-order/', json.dumps(payload), content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_HOST='127.0.0.1')
print('Status:', resp.status_code)
try:
    print('JSON:', resp.json())
except Exception:
    print('Content:', resp.content)
