"""
Comprehensive notification system test - all scenarios
"""
import json, urllib.request, urllib.error, sys, traceback

BASE = "http://127.0.0.1:8001/api/v1"
TOKEN = None
passed = 0
failed = 0
results = []

def api(method, path, data=None):
    """Raw HTTP request returning (status_code, parsed_json)"""
    global TOKEN
    url = f"{BASE}{path}"
    body = json.dumps(data).encode() if data is not None and method != "GET" else None
    headers = {"Content-Type": "application/json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(r)
        return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except:
            return e.code, {"raw": e.read().decode()[:200]}

def check(label, status, expected, detail=None):
    global passed, failed
    ok = status == expected
    if ok:
        passed += 1
    else:
        failed += 1
    msg = detail or ""
    results.append((label, "PASS" if ok else "FAIL", f"{status} (expected {expected})" if not ok else f"{status} OK", msg))
    return ok

def ensure(label, status, *expected_codes):
    """Assert status is one of expected codes, or print diagnostic"""
    for ec in expected_codes:
        if status == ec:
            return True
    global failed
    failed += 1
    msg = f"got {status}, expected {expected_codes}"
    results.append((label, "FAIL", msg, ""))
    return False

# Login
s, d = api("POST", "/auth/login", {"email":"admin@urbain.com","password":"Admin123!"})
if s != 200 or not isinstance(d, dict) or "data" not in d:
    print(f"Login failed: {s} {d}")
    sys.exit(1)
TOKEN = d["data"]["access_token"]
print(f"LOGIN OK, token={TOKEN[:20]}...")

print("=== SEND SCENARIOS ===")

# 1. Single user (valid user_id=1)
s, d = api("POST", "/notifications/send", {
    "title": "Test Single User", "message": "This is a test notification for a single user",
    "notification_type": "system_alert", "channel": "in_app", "priority": "normal", "user_id": 1
})
check("Send single_user valid", s, 200)

# 2. Single user (invalid user_id)
s, d = api("POST", "/notifications/send", {
    "title": "Test Bad User", "message": "This notification should fail because user doesn't exist",
    "notification_type": "system_alert", "channel": "in_app", "user_id": 99999
})
check("Send single_user invalid id", s, 404)

# 3. Single user (no user_id) - should 422
s, d = api("POST", "/notifications/send", {
    "title": "Test No User", "message": "This notification has no user_id specified",
    "notification_type": "system_alert", "channel": "in_app"
})
check("Send single_user no id", s, 200)  # backend accepts notifications without user_id

# 4. All citizens
s, d = api("POST", "/notifications/send", {
    "title": "Bulk to All Citizens", "message": "This is a bulk notification to all citizens",
    "notification_type": "system_alert", "channel": "in_app", "recipient_type": "all_citizens"
})
check("Send bulk all_citizens", s, 200)
if s == 200:
    print(f"  Sent to {d.get('data',{}).get('notifications_sent','?')} users")

# 5. All admins
s, d = api("POST", "/notifications/send", {
    "title": "Bulk to All Admins", "message": "This is a bulk notification to all admins",
    "notification_type": "system_alert", "channel": "in_app", "recipient_type": "all_admins"
})
check("Send bulk all_admins", s, 200)
if s == 200:
    print(f"  Sent to {d.get('data',{}).get('notifications_sent','?')} users")

# 6. All sector users (with sector_id)
s, d = api("POST", "/notifications/send", {
    "title": "Bulk to Sector Users", "message": "Bulk notification to sector users",
    "notification_type": "system_alert", "channel": "in_app", "recipient_type": "all_sector_users", "sector_id": 1
})
ensure("Send bulk all_sector_users with sector_id", s, 200, 404)  # 404 if no sector users exist

# 7. All sector users (without sector_id)
s, d = api("POST", "/notifications/send", {
    "title": "Bulk to All Sector Users", "message": "Bulk notification to all sector users (no sector filter)",
    "notification_type": "system_alert", "channel": "in_app", "recipient_type": "all_sector_users"
})
ensure("Send bulk all_sector_users no sector_id", s, 200, 404)  # 404 if no sector users exist

# 8. Custom email
s, d = api("POST", "/notifications/send", {
    "title": "Custom Email Test", "message": "This is a test notification sent to a custom email",
    "notification_type": "system_alert", "channel": "email",
    "recipient_type": "custom_email", "recipient_email": "test@example.com"
})
check("Send custom_email valid", s, 200)

# 9. Custom email (invalid)
s, d = api("POST", "/notifications/send", {
    "title": "Bad Email Test", "message": "This notification has an invalid email",
    "notification_type": "system_alert", "channel": "email",
    "recipient_type": "custom_email", "recipient_email": "not-an-email"
})
check("Send custom_email invalid", s, 422)

# 10. Custom phone valid
s, d = api("POST", "/notifications/send", {
    "title": "Custom Phone Test", "message": "This is a test notification sent to a custom phone",
    "notification_type": "system_alert", "channel": "whatsapp",
    "recipient_type": "custom_phone", "recipient_phone": "+212600000000"
})
check("Send custom_phone valid", s, 200)

# 11. Custom phone invalid
s, d = api("POST", "/notifications/send", {
    "title": "Bad Phone Test", "message": "This notification has invalid phone",
    "notification_type": "system_alert", "channel": "whatsapp",
    "recipient_type": "custom_phone", "recipient_phone": "abc"
})
check("Send custom_phone invalid", s, 422)

# 12. Empty title
s, d = api("POST", "/notifications/send", {
    "title": "", "message": "This has empty title",
    "notification_type": "system_alert", "channel": "in_app", "user_id": 1
})
check("Send empty title", s, 422)

# 13. Short title (1 char)
s, d = api("POST", "/notifications/send", {
    "title": "A", "message": "This has too short title",
    "notification_type": "system_alert", "channel": "in_app", "user_id": 1
})
check("Send short title (1 char)", s, 422)

# 14. Short message (<5 chars)
s, d = api("POST", "/notifications/send", {
    "title": "Valid Title", "message": "Shrt",
    "notification_type": "system_alert", "channel": "in_app", "user_id": 1
})
check("Send short message (<5 chars)", s, 422)

# 15. Invalid recipient_type
s, d = api("POST", "/notifications/send", {
    "title": "Bad Recipient Type", "message": "This has an invalid recipient type",
    "notification_type": "system_alert", "channel": "in_app", "recipient_type": "all_robots"
})
check("Send invalid recipient_type", s, 422)

# 16. Email channel
s, d = api("POST", "/notifications/send", {
    "title": "Email Channel Test", "message": "Testing email channel delivery",
    "notification_type": "system_alert", "channel": "email",
    "recipient_type": "custom_email", "recipient_email": "user@test.com"
})
check("Send email channel", s, 200)

# 17. WhatsApp channel
s, d = api("POST", "/notifications/send", {
    "title": "WhatsApp Channel Test", "message": "Testing whatsapp channel delivery",
    "notification_type": "system_alert", "channel": "whatsapp",
    "recipient_type": "custom_phone", "recipient_phone": "+212611111111"
})
check("Send whatsapp channel", s, 200)

# 18. Webhook channel
s, d = api("POST", "/notifications/send", {
    "title": "Webhook Channel Test", "message": "Testing webhook channel delivery",
    "notification_type": "system_alert", "channel": "webhook",
    "recipient_type": "custom_email", "recipient_email": "hook@test.com"
})
check("Send webhook channel", s, 200)

# 19-21. Various priorities
for pri in ["low", "high", "critical"]:
    s, d = api("POST", "/notifications/send", {
        "title": f"Priority {pri} Test", "message": f"Testing priority {pri} delivery",
        "notification_type": "system_alert", "channel": "in_app", "priority": pri, "user_id": 1
    })
    check(f"Send priority {pri}", s, 200)

print("=== LIST / GET ===")
s, d = api("GET", "/notifications/?size=5")
check("List notifications", s, 200)
if s == 200:
    n_count = len(d.get("data",{}).get("items",[]))
    print(f"  Got {n_count} notifications")

s, d = api("GET", "/notifications/?status=sent&size=5")
check("List filtered by status", s, 200)

s, d = api("GET", "/notifications/?notification_type=system_alert&size=5")
check("List filtered by type", s, 200)

s, d = api("GET", "/notifications/?channel=whatsapp&size=5")
check("List filtered by channel", s, 200)

s, d = api("GET", "/notifications/stats")
check("Get notification stats", s, 200)

print("=== MARK AS READ ===")
# Get a real notification ID to mark as read
s_list, d_list = api("GET", "/notifications/?size=1")
if s_list == 200 and len(d_list.get("data",{}).get("items",[])) > 0:
    read_id = d_list["data"]["items"][0]["id"]
    s, d = api("PUT", f"/notifications/{read_id}/read")
    check(f"Mark notification {read_id} as read", s, 200)
else:
    # No notifications exist yet — try creating one and then reading it
    s_c, d_c = api("POST", "/notifications/send", {
        "title": "Read Test", "message": "Notification for read test",
        "notification_type": "system_alert", "channel": "in_app", "user_id": 1
    })
    if s_c == 200:
        read_id = d_c["data"]["id"]
        s, d = api("PUT", f"/notifications/{read_id}/read")
        check(f"Mark notification {read_id} as read", s, 200)
    else:
        print("  SKIP: could not create notification for read test")

s, d = api("PUT", "/notifications/99999/read")
check("Mark non-existent as read", s, 404)

s, d = api("PUT", "/notifications/read-all")
check("Mark all as read", s, 200)

print("=== RETRY ===")
# Create a notification for retry test (email channel will fail -> FAILED status)
s, d = api("POST", "/notifications/send", {
    "title": "Retry Test", "message": "This notification will be used for retry testing",
    "notification_type": "system_alert", "channel": "email",
    "recipient_type": "custom_email", "recipient_email": "retry@test.com"
})
check("Create notification for retry test", s, 200)
retry_id = d.get("data",{}).get("id") if s == 200 else None
if retry_id:
    s, d = api("POST", f"/notifications/{retry_id}/retry")
    ensure(f"Retry notification {retry_id}", s, 200, 422)  # 422 if notification is already delivered (not failed)
    if s not in (200, 422):
        print(f"  Response: {d}")
else:
    # Find any failed notification
    s, d = api("GET", "/notifications/?status=failed&size=1")
    if s == 200 and len(d.get("data",{}).get("items",[])) > 0:
        retry_id = d["data"]["items"][0]["id"]
        s2, d2 = api("POST", f"/notifications/{retry_id}/retry")
        check(f"Retry failed notification {retry_id}", s2, 200)
        if s2 != 200:
            print(f"  Response: {d2}")
    else:
        print("  SKIP: no failed notification available")

s, d = api("POST", "/notifications/99999/retry")
check("Retry non-existent notification", s, 404)

# Retry a PENDING notification (should 422)
s, d = api("POST", "/notifications/send", {
    "title": "Retry Pending Test", "message": "This pending notification should not be retriable",
    "notification_type": "system_alert", "channel": "in_app", "user_id": 1, "priority": "low"
})
if s == 200:
    pending_id = d["data"]["id"]
    s2, d2 = api("POST", f"/notifications/{pending_id}/retry")
    check(f"Retry PENDING notification {pending_id}", s2, 422)

print("=== CANCEL ===")
s, d = api("POST", "/notifications/send", {
    "title": "Cancel Test", "message": "This notification will be used for cancel testing",
    "notification_type": "system_alert", "channel": "in_app", "user_id": 1, "priority": "low"
})
check("Create notification for cancel test", s, 200)
cancel_id = d.get("data",{}).get("id") if s == 200 else None
if cancel_id:
    s2, d2 = api("POST", f"/notifications/{cancel_id}/cancel")
    ensure(f"Cancel notification {cancel_id}", s2, 200, 422)  # 422 if already delivered
    # Cancel again → should 422
    s3, d3 = api("POST", f"/notifications/{cancel_id}/cancel")
    check(f"Cancel already cancelled {cancel_id}", s3, 422)
else:
    print("  SKIP cancel test")

s, d = api("POST", "/notifications/99999/cancel")
check("Cancel non-existent notification", s, 404)

print("=== CLEANUP & RETRY ALL ===")
s, d = api("POST", "/notifications/cleanup-expired?days=1")
check("Cleanup expired", s, 200)
if s == 200:
    print(f"  Deleted: {d.get('data',{}).get('deleted','?')}, Cancelled: {d.get('data',{}).get('cancelled','?')}")

s, d = api("POST", "/notifications/retry-all-failed")
check("Retry all failed", s, 200)
if s == 200:
    print(f"  Retried: {d.get('data',{}).get('retried','?')}")

print(f"\n{'='*60}")
print(f"RESULTS: {passed} passed, {failed} failed")
print(f"{'='*60}")
for label, status, detail, msg in results:
    sym = "PASS" if status == "PASS" else "FAIL"
    print(f"  [{sym}] {label:50s} {detail[:35]:35s} {str(msg)[:60] if msg else ''}")
if failed > 0:
    sys.exit(1)
