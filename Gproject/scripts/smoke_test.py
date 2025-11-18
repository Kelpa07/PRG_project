import os
import django
import sys
import json
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Gproject.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

client = Client()
HOST = {'HTTP_HOST': '127.0.0.1'}
passed = 0
failed = 0

def test(name, fn):
    global passed, failed
    try:
        fn()
        print(f"✓ {name}")
        passed += 1
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        failed += 1
    except Exception as e:
        print(f"✗ {name}: {type(e).__name__}: {e}")
        failed += 1

# Test pages
def test_index():
    resp = client.get('/', **HOST)
    assert resp.status_code == 200, f"Got {resp.status_code}"
test('GET /', test_index)

def test_menu():
    resp = client.get('/menu/', **HOST)
    assert resp.status_code == 200, f"Got {resp.status_code}"
test('GET /menu/', test_menu)

def test_order():
    resp = client.get('/order/', **HOST)
    assert resp.status_code == 200, f"Got {resp.status_code}"
test('GET /order/', test_order)

def test_reception():
    resp = client.get('/reception/', **HOST)
    assert resp.status_code == 200, f"Got {resp.status_code}"
test('GET /reception/', test_reception)

def test_aboutus():
    resp = client.get('/aboutus/', **HOST)
    assert resp.status_code == 200, f"Got {resp.status_code}"
test('GET /aboutus/', test_aboutus)

# Test signup
def test_signup_customer():
    resp = client.post('/accounts/', {
        'username': 'testuser', 'password1': 'pass@12345', 'password2': 'pass@12345', 'role': 'customer'
    }, **HOST)
    assert resp.status_code in (200, 302), f"Got {resp.status_code}"
test('POST /accounts/ (customer)', test_signup_customer)

def test_signup_admin_wrong_code():
    resp = client.post('/accounts/', {
        'username': 'testadmin1', 'password1': 'pass@12345', 'password2': 'pass@12345', 'role': 'admin', 'admin_code': 'wrong'
    }, **HOST)
    # Should not redirect (error on same page)
    assert resp.status_code == 200, f"Got {resp.status_code}"
test('POST /accounts/ (admin, wrong code)', test_signup_admin_wrong_code)

def test_signup_admin_correct_code():
    resp = client.post('/accounts/', {
        'username': 'testadmin2', 'password1': 'pass@12345', 'password2': 'pass@12345', 'role': 'admin', 'admin_code': 'please-change-this'
    }, **HOST)
    # Should redirect after success
    assert resp.status_code in (200, 302), f"Got {resp.status_code}"
test('POST /accounts/ (admin, correct code)', test_signup_admin_correct_code)

# Test login
def test_login():
    resp = client.post('/login/', {'username': 'testuser', 'password': 'pass@12345'}, **HOST)
    assert resp.status_code in (200, 302), f"Got {resp.status_code}"
test('POST /login/', test_login)

# Test order API
def test_place_order():
    payload = {'items': [{'title': 'Test', 'price': 10, 'qty': 1}], 'total': 10}
    resp = client.post('/api/place-order/', json.dumps(payload), 
                       content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest', **HOST)
    assert resp.status_code == 200, f"Got {resp.status_code}"
    data = resp.json()
    assert data.get('ok') == True, f"Got {data}"
test('POST /api/place-order/', test_place_order)

# Test mark received
def test_mark_received():
    resp = client.post('/api/mark-received/1/', '', content_type='application/json', 
                       HTTP_X_REQUESTED_WITH='XMLHttpRequest', **HOST)
    assert resp.status_code == 200, f"Got {resp.status_code}"
    data = resp.json()
    assert data.get('ok') == True, f"Got {data}"
test('POST /api/mark-received/1/', test_mark_received)

print(f"\n{passed} passed, {failed} failed")
sys.exit(0 if failed == 0 else 1)
