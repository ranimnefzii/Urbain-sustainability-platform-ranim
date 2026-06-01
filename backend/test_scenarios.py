import asyncio, httpx

async def test():
    async with httpx.AsyncClient() as client:
        r = await client.post('http://127.0.0.1:8001/api/v1/auth/login', json={'email':'admin@urbain.com','password':'Admin123!'})
        token = r.json()['data']['access_token']
        h = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        
        tests = [
            ('EMAIL custom_email', {'title':'Test E','message':'Testing email from frontend','notification_type':'system_alert','channel':'email','priority':'normal','recipient_type':'custom_email','recipient_email':'seifabdaoui5@gmail.com'}),
            ('WHATSAPP custom_phone', {'title':'Test WA','message':'Testing WhatsApp from frontend','notification_type':'system_alert','channel':'whatsapp','priority':'normal','recipient_type':'custom_phone','recipient_phone':'+21654309348'}),
            ('WHATSAPP single_user',  {'title':'Test WU','message':'Testing WhatsApp to user','notification_type':'system_alert','channel':'whatsapp','priority':'normal','user_id':1}),
            ('EMAIL single_user', {'title':'Test EU','message':'Testing email to user','notification_type':'system_alert','channel':'email','priority':'normal','user_id':1}),
            ('MEDIUM priority alias', {'title':'Test M','message':'Testing MEDIUM alias','notification_type':'system_alert','channel':'in_app','priority':'medium','user_id':1}),
        ]
        for name, payload in tests:
            r = await client.post('http://127.0.0.1:8001/api/v1/notifications/send', json=payload, headers=h)
            ok = r.status_code == 200
            status = 'OK' if ok else 'FAIL'
            print(f'  [{status}] {name}: {r.status_code}', end='')
            print(' (no 500!)' if ok else f' {r.json()}')
        
        # Run full test suite
        print()
        print('=== Full test suite ===')
        import subprocess
        result = subprocess.run(['python', 'test_notification_full.py'], capture_output=True, text=True)
        for line in result.stdout.split(chr(10)):
            if 'PASS' in line or 'FAIL' in line:
                print(line)

asyncio.run(test())
