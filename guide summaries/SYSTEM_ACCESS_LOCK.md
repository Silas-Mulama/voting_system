# System Access Lock - Implementation Guide

## Overview

The System Access Lock is a global control mechanism that allows administrators to instantly suspend access to the eVoting system for non-admin users. This is useful for:

- Maintenance windows
- Emergency shutdowns
- Service interruptions
- Custom operational scenarios

**Key Feature**: System status can be changed instantly by updating the database—no code redeploy required.

---

## Architecture

### 1. **SystemStatus Model** (`core/models.py`)

Singleton model that stores the global system status:

```python
class SystemStatus(models.Model):
    is_active = models.BooleanField(default=True)
    suspension_reason = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @classmethod
    def get_status(cls):
        """Get or create the system status singleton."""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
```

- **is_active**: When `False`, non-admin users see a suspension page
- **suspension_reason**: Optional message displayed to suspended users
- **updated_at**: Auto-updated timestamp tracking last change

### 2. **SystemAccessLockMiddleware** (`core/middleware.py`)

Django middleware that enforces access control:

```python
class SystemAccessLockMiddleware(MiddlewareMixin):
    ALWAYS_ALLOWED_PATHS = [
        '/admin/',
        '/login/',
        '/logout/',
    ]
```

**Access Control Logic**:
- ✅ **Always allow**: Admin paths, login, logout
- ✅ **Always allow**: Unauthenticated users (redirect to login)
- ✅ **Always allow**: Admin users (staff/superuser)
- ❌ **Block**: Non-admin authenticated users when `is_active=False`

**Response**: Returns HTTP 403 with `system_suspended.html` template

### 3. **Suspension Page** (`templates/core/system_suspended.html`)

Professional, user-friendly suspension page that:

- Displays a clear message about unavailability
- Shows optional suspension reason (if provided)
- Includes reassurance about data safety
- Provides a logout button
- Does NOT mention payment or developers
- Responsive design for mobile and desktop

### 4. **Admin Interface** (`core/admin.py`)

SystemStatus is registered in Django Admin with:

- Easy toggle for `is_active` field
- Rich text area for `suspension_reason`
- Read-only `updated_at` timestamp
- Helpful description text
- Status display showing ✅ Active or 🔒 Suspended

### 5. **Management Command** (`core/management/commands/system_status.py`)

CLI tool for quick system status changes:

```bash
# Enable the system
python manage.py system_status enable

# Suspend the system with a reason
python manage.py system_status suspend --reason "Scheduled maintenance until 3 PM"
```

---

## How to Use

### Method 1: Django Admin Panel (Recommended for Quick Changes)

1. Go to `http://yoursite/admin/`
2. Click on **System Status** in the sidebar
3. Check/uncheck the **Is Active** field
4. Optionally add a **Suspension Reason**
5. Click **Save**

✅ Changes take effect **immediately**

### Method 2: Management Command (Best for Automation)

```bash
# Suspend with reason
python manage.py system_status suspend --reason "Scheduled maintenance 2-4 PM"

# Enable immediately
python manage.py system_status enable
```

### Method 3: Direct Database Query (Advanced)

```bash
# Using Django shell
python manage.py shell

from core.models import SystemStatus

# Suspend
status = SystemStatus.get_status()
status.is_active = False
status.suspension_reason = "Your reason here"
status.save()

# Enable
status.is_active = True
status.save()
```

---

## What Users See

### When System is Active ✅
- Normal access to all student features
- Elections list, voting, results, etc.

### When System is Suspended 🔒
- Non-admin users see: **"System Temporarily Unavailable"** page
- HTTP 403 status code
- Optional suspension reason is displayed
- Button to return to login
- No data is lost

### Admin Always Can Access
- Admins can access `/admin/` at all times
- Useful for troubleshooting during suspension

---

## Technical Details

### Middleware Execution Flow

```
Request arrives
    ↓
Is it an admin path (/admin/, /login/, /logout/)?
    → YES: Allow
    → NO: Continue
    ↓
Is system active (is_active=True)?
    → YES: Allow
    → NO: Continue
    ↓
Is user authenticated?
    → NO: Allow (redirect to login handled elsewhere)
    → YES: Continue
    ↓
Is user an admin (is_staff or is_superuser)?
    → YES: Allow
    → NO: Render system_suspended.html (HTTP 403)
```

### Database Schema

```sql
CREATE TABLE core_systemstatus (
    id INTEGER PRIMARY KEY,
    is_active BOOLEAN DEFAULT 1,
    suspension_reason TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## Features & Guarantees

✅ **Instant Changes**: No redeploy required—update database and system responds immediately

✅ **Centralized Control**: Middleware enforces globally, not in individual views

✅ **Admin Exemption**: System admins can always access `/admin/` for troubleshooting

✅ **Data Safety**: When suspended, only access is blocked—no data is deleted or lost

✅ **User-Friendly**: Professional suspension page with optional explanatory text

✅ **No Hardcoding**: Django best practices—all logic in middleware and models

✅ **Performance**: Single database query per request (uses get_or_create with pk=1)

✅ **Responsive**: Works on mobile, tablet, and desktop

---

## Setup Checklist

- [x] Added `SystemStatus` model to `core/models.py`
- [x] Created `core/middleware.py` with `SystemAccessLockMiddleware`
- [x] Added middleware to `MIDDLEWARE` list in `evoting_system/settings.py`
- [x] Created `templates/core/system_suspended.html` template
- [x] Registered `SystemStatus` in `core/admin.py`
- [x] Created `system_status` management command
- [x] Created this documentation

---

## Example Scenarios

### Scenario 1: Emergency Maintenance

```bash
# Suspend immediately with reason
python manage.py system_status suspend --reason "Emergency server maintenance. Expected duration: 30 minutes."

# After fixing, enable
python manage.py system_status enable
```

**Result**: Students see suspension page. Admins can still troubleshoot in `/admin/`.

### Scenario 2: Scheduled Downtime

1. Go to Django Admin
2. Set `is_active = False`
3. Add reason: "System scheduled maintenance 11 PM - 1 AM"
4. Save at 10:55 PM
5. At 1:05 AM, go back and set `is_active = True`

**Result**: Students cannot vote during maintenance window but see clear message.

### Scenario 3: Graceful Degradation

Instead of hard shutdown, you could also extend middleware to:
- Log suspension attempts
- Track active sessions
- Notify admins via email
- Set auto-recovery time

---

## Security Considerations

- ✅ Middleware runs after authentication—unauthenticated users can still log in
- ✅ Status is checked on every request (minimal performance impact)
- ✅ Admins need valid credentials to bypass suspension
- ✅ Suspension reason is simple text—no HTML injection risks
- ✅ HTTP 403 status code is semantically correct for access denied

---

## Troubleshooting

### Question: Why can an admin still access the system?

**Answer**: This is intentional. Admins need to troubleshoot and re-enable the system. This is managed in the middleware with the check:

```python
if request.user.is_staff or request.user.is_superuser:
    return None
```

### Question: How do I test if it's working?

**Answer**: 
1. Suspend the system: `python manage.py system_status suspend --reason "Test"`
2. Log in as a student
3. You should see the suspension page
4. Log out and log in as an admin—you can access `/admin/`
5. Enable: `python manage.py system_status enable`

### Question: What if a user was in the middle of voting when suspended?

**Answer**: Their session persists, but they cannot navigate to new pages. When the system is re-enabled, they can resume. No votes are lost.

---

## Database Migration

Run migrations to create the `SystemStatus` table:

```bash
python manage.py makemigrations
python manage.py migrate
```

The system automatically creates the singleton record on first access via `get_or_create(pk=1)`.

---

## Future Enhancements

Possible extensions to this feature:

- **Scheduled Suspension**: Set auto-suspension at specific times
- **Notification System**: Notify users by email before suspension
- **Granular Permissions**: Different suspension rules for different user groups
- **Audit Trail**: Log all system status changes
- **API Endpoint**: Allow integration with external monitoring systems
- **Customizable Messages**: Admin-configurable suspension message templates

---

## Related Files

- `core/models.py` - SystemStatus model
- `core/middleware.py` - Access lock middleware
- `core/admin.py` - Admin interface
- `core/management/commands/system_status.py` - Management command
- `templates/core/system_suspended.html` - Suspension page
- `evoting_system/settings.py` - Middleware registration

---

**Last Updated**: January 26, 2026  
**System**: Butere Technical Training Institute eVoting System
