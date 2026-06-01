import json, urllib.request, urllib.error

try:
    r = urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8001/api/v1/auth/login',
        data=json.dumps({'email':'admin@urbain.com','password':'Admin123!'}).encode(),
        headers={'Content-Type':'application/json'}), timeout=5)
    token = json.loads(r.read())['data']['access_token']
    print('Server OK, logged in')

    # Exact payload the frontend sends for SINGLE_USER with valid fields
    payload = {'title':'Test','message':'This is a test message body','notification_type':'system_alert','channel':'in_app','priority':'normal','user_id':1}
    r2 = urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8001/api/v1/notifications/send',
        data=json.dumps(payload).encode(),
        headers={'Content-Type':'application/json','Authorization':f'Bearer {token}'}), timeout=5)
    d = json.loads(r2.read())
    status = r2.status
    msg = d.get('message', '')
    print(f'Send single_user: {status} - {msg}')

    # Frontend payload for ALL_CITIZENS
    payload2 = {'title':'Test Bulk','message':'This is a test message body','notification_type':'system_alert','channel':'in_app','priority':'normal','recipient_type':'all_citizens'}
    r3 = urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8001/api/v1/notifications/send',
        data=json.dumps(payload2).encode(),
        headers={'Content-Type':'application/json','Authorization':f'Bearer {token}'}), timeout=5)
    d2 = json.loads(r3.read())
    print(f'Send all_citizens: {r3.status} - {d2.get("message")}')

except urllib.error.HTTPError as e:
    print(f'HTTP Error {e.code}: {e.read().decode()[:500]}')
except Exception as e:
    print(f'Connection error: {e}')

print('Done')
