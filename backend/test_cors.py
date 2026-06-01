import json, urllib.request, urllib.error

# Login
r = urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8001/api/v1/auth/login',
    data=json.dumps({'email':'admin@urbain.com','password':'Admin123!'}).encode(),
    headers={'Content-Type':'application/json'}))
token = json.loads(r.read())['data']['access_token']

# Send with Origin header (simulating browser)
payload = {'title':'Test','message':'This is a test message body','notification_type':'system_alert','channel':'in_app','priority':'normal','user_id':1}
req = urllib.request.Request('http://127.0.0.1:8001/api/v1/notifications/send',
    data=json.dumps(payload).encode(),
    headers={
        'Content-Type':'application/json',
        'Authorization':f'Bearer {token}',
        'Origin':'http://localhost:5173'
    })
try:
    r = urllib.request.urlopen(req)
    d = json.loads(r.read())
    print(f'200 OK: {d.get("message")}')
    print(f'CORS headers: Access-Control-Allow-Origin={r.headers.get("Access-Control-Allow-Origin")}')
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f'Error {e.code}: {body[:500]}')
    print(f'Response headers: {dict(e.headers)}')
except Exception as e:
    print(f'Exception: {e}')
