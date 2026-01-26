# System Access Lock - Quick Reference Guide

## 🚀 Quick Start

The system access lock allows you to instantly suspend access to the eVoting system for students without affecting admins or requiring a code redeploy.

---

## 📋 Three Ways to Control System Access

### 1️⃣ **Django Admin Panel** (Easiest - Recommended)

1. Go to: `http://yoursite/admin/`
2. Login with admin credentials
3. Click **"System Status"** in the left menu
4. Check or uncheck **"Is Active"** checkbox
5. (Optional) Add a suspension reason in the text field
6. Click **"Save"**

✅ **Changes take effect immediately!**

---

### 2️⃣ **Command Line** (Best for Automation)

```bash
# Suspend the system with a message
python manage.py system_status suspend --reason "Server maintenance until 3 PM"

# Resume the system
python manage.py system_status enable
```

✅ **Perfect for scheduled maintenance scripts!**

---

### 3️⃣ **Django Shell** (Advanced/Debug)

```bash
python manage.py shell
```

Then in the Python shell:

```python
from core.models import SystemStatus

# Get the system status
status = SystemStatus.get_status()

# Suspend
status.is_active = False
status.suspension_reason = "Custom reason here"
status.save()

# Resume
status.is_active = True
status.save()
```

---

## 🔒 What Happens When System is Suspended

### Students See:
- ✗ Cannot access voting, elections, results, or any student features
- ✓ See professional "System Temporarily Unavailable" page (HTTP 403)
- ✓ See the suspension reason (if you provided one)
- ✓ Can return to login page
- ✓ All their votes/data are safe (nothing is deleted)

### Admins Always Can:
- ✓ Access `/admin/` for management
- ✓ Access `/admin/elections/`, `/admin/results/`, etc.
- ✓ Re-enable the system immediately

### Login/Logout:
- ✓ Login and logout pages always work
- ✓ Students can still login, but access is blocked after login

---

## 📊 Practical Examples

### Example 1: Quick Maintenance

```bash
# 9:50 AM - Emergency issue detected
python manage.py system_status suspend --reason "Emergency server maintenance in progress"

# Fix the issue...

# 10:15 AM - Ready to resume
python manage.py system_status enable
```

### Example 2: Scheduled Downtime

Use Django Admin at a specific time:
1. Open admin panel 1 hour before maintenance
2. Disable system: uncheck "Is Active"
3. Add reason: "Scheduled database upgrade 2-4 PM"
4. Save
5. After maintenance, check the box again and save

### Example 3: Graceful Shutdown

Use command with detailed message:

```bash
python manage.py system_status suspend --reason "System will be temporarily unavailable for upgrades. Expected duration: 2 hours. Thank you for your patience."
```

---

## ❓ Frequently Asked Questions

### Q: Does suspending the system delete any votes?
**A:** No! Suspension only blocks access. All votes and data are preserved. When you re-enable, everything is exactly as it was.

### Q: Can admins bypass the suspension?
**A:** Yes, by design. Admins need access to `/admin/` to re-enable the system if something goes wrong.

### Q: What if a student is mid-vote when I suspend?
**A:** Their session is preserved. When you re-enable, they can resume voting from where they left off.

### Q: How long does it take for the suspension to take effect?
**A:** Immediately! The middleware checks status on every request.

### Q: Can students see payment-related messages?
**A:** No! The suspension page is generic and doesn't mention payment or the developer.

### Q: Do I need to redeploy code to change the status?
**A:** No! Status is stored in the database and checked at runtime.

---

## 🛠️ Troubleshooting

### Issue: Admin can't access `/admin/` when suspended

**Solution**: This shouldn't happen. The middleware explicitly allows `/admin/` paths. Check that:
1. User has `is_staff=True` or `is_superuser=True`
2. Middleware is correctly registered in `settings.py`
3. Clear browser cache and try again

### Issue: Student got stuck on suspension page

**Solution**: This is normal. They'll see the suspension page until you:
1. Re-enable the system: `python manage.py system_status enable`
2. They refresh their browser

### Issue: Suspension page looks broken/unstyled

**Solution**: 
1. Make sure `templates/core/system_suspended.html` exists
2. Run `python manage.py collectstatic` (for production)
3. Clear browser cache

---

## 📱 What the Suspension Page Shows

```
┌─────────────────────────────────────┐
│  🔒 System Temporarily Unavailable  │
│  (Professional header with gradient)│
├─────────────────────────────────────┤
│                                     │
│  Scheduled Maintenance              │
│  We apologize for the inconvenience.│
│  The eVoting system is currently    │
│  unavailable.                       │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ Additional Information:        │ │
│  │ [Your suspension reason here] │ │
│  └───────────────────────────────┘ │
│                                     │
│  [ Return to Login ]                │
│                                     │
├─────────────────────────────────────┤
│  Your voting progress is safe...    │
│  Butere TTI — Fair. Secure. Secure. │
└─────────────────────────────────────┘
```

---

## 🔐 Security Features

✅ **Centralized Control**: Enforced by middleware, not scattered in views  
✅ **Admin Always Can Access**: Emergency override built-in  
✅ **Instant Changes**: No code redeploy needed  
✅ **Data Safe**: Suspension doesn't touch votes/data  
✅ **No Hardcoding**: Django best practices throughout  
✅ **Responsive**: Works on phone, tablet, desktop  

---

## 📚 Related Files

- **Model**: `core/models.py` → `SystemStatus` class
- **Middleware**: `core/middleware.py` → `SystemAccessLockMiddleware`
- **Admin**: `core/admin.py` → `SystemStatusAdmin`
- **Command**: `core/management/commands/system_status.py`
- **Template**: `templates/core/system_suspended.html`
- **Settings**: `evoting_system/settings.py` → `MIDDLEWARE` list

---

## 🎯 Summary

| Task | Method | Time to Take Effect |
|------|--------|-------------------|
| Quick toggle | Admin panel | Instant |
| Scheduled downtime | Django Admin 1 hour early | Instant |
| Emergency shutdown | `system_status suspend` command | Instant |
| Automated shutdown | Scheduled task with command | Instant |
| Resume service | Any of 3 methods | Instant |

---

**Need more help?** See `SYSTEM_ACCESS_LOCK.md` for complete technical documentation.

---

**Butere Technical Training Institute — Fair. Secure. Transparent Elections.**
