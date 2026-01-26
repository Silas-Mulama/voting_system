# System Access Lock - Admin Dashboard Guide

## Overview for System Administrators

The System Access Lock is a feature that allows you to instantly control who can use the eVoting system. When activated, students cannot access voting, elections, or results—but admins can always access the admin panel for troubleshooting.

---

## 🎯 Use Cases

✅ **Server Maintenance** - Temporarily disable access while performing updates  
✅ **Emergency Shutdown** - Instantly block access during a crisis  
✅ **Scheduled Downtime** - Pre-plan maintenance windows  
✅ **Testing** - Suspend system while making changes  
✅ **Billing Issues** - Restrict access if needed (system doesn't enforce this, but you control it)  

---

## 🎛️ Control Panel Location

Navigate to: **`/admin/core/systemstatus/`**

Or from the Django Admin Home:
1. Login to `/admin/`
2. Look for **"System Status"** in the left sidebar
3. Click it to open the control panel

---

## ⚙️ Control Panel Interface

The System Status panel shows:

```
┌──────────────────────────────────────┐
│ System Status                        │
├──────────────────────────────────────┤
│ Is Active:    ☑ (Checkbox)          │
│               [Enable/Disable access]│
│                                      │
│ Suspension Reason:                   │
│ ┌──────────────────────────────────┐ │
│ │ (Text area - optional)           │ │
│ │ What to tell users when blocked  │ │
│ └──────────────────────────────────┘ │
│                                      │
│ Updated At:   2024-01-26 10:30:45   │
│               [Read-only timestamp]  │
│                                      │
│ [ Cancel ]  [ Save ]                │
└──────────────────────────────────────┘
```

---

## 📝 Step-by-Step: Suspend the System

### If System is Currently ACTIVE (☑ checked):

1. **Uncheck** the "Is Active" checkbox
   - This blocks all student access
   - Admins remain unaffected

2. **(Optional) Add a reason** in the text area:
   - "Server maintenance in progress"
   - "Emergency hardware replacement"
   - "System upgrade - back online at 3 PM"
   - Be clear and professional

3. Click **"Save"** button
   - ✅ Changes take effect instantly
   - Students will see suspension page on next action

### What Students See:

Students trying to vote will see:
- **"System Temporarily Unavailable"** (large header)
- Your reason (if provided)
- **"Return to Login"** button
- Assurance that their data is safe

---

## 📝 Step-by-Step: Resume the System

### If System is Currently INACTIVE (☐ unchecked):

1. **Check** the "Is Active" checkbox
   - This allows all student access
   - Students can immediately vote again

2. **(Optional) Clear the reason**
   - You can leave it or clear it
   - Not displayed when system is active

3. Click **"Save"** button
   - ✅ System is live again instantly
   - Students can resume voting immediately

---

## ⏰ Scheduling Maintenance

### Example: Friday 10 PM - Saturday 6 AM Maintenance

**Friday 9:00 PM** (1 hour before):
1. Open `/admin/core/systemstatus/`
2. Uncheck "Is Active"
3. Add reason: "Scheduled database maintenance. Expected duration: 8 hours. System will be back online at 6 AM Saturday."
4. Save
5. ✅ Students see suspension page

**Saturday 6:15 AM** (maintenance complete):
1. Open `/admin/core/systemstatus/`
2. Check "Is Active"
3. Clear the reason (optional)
4. Save
5. ✅ System is live

---

## 🚨 Emergency Shutdown

### If Something Goes Wrong:

1. Go to `/admin/core/systemstatus/` (takes ~10 seconds)
2. Uncheck "Is Active"
3. Add reason: "System is temporarily offline for emergency maintenance"
4. Click Save
5. ✅ **System is locked within seconds**

Students cannot access anything. You remain in control via `/admin/`.

---

## 🔍 What Admins Can Always Do

Even when the system is suspended:

✅ Access `/admin/` - full admin interface  
✅ Manage elections, positions, candidates  
✅ View audit logs  
✅ Review voting results  
✅ Export data  
✅ Re-enable the system  

**Only students are blocked.**

---

## 💡 Pro Tips

### Tip 1: Use Clear Reasons
❌ Bad: "System down"  
✅ Good: "Server migration - expected to be online by 2 PM EDT"

### Tip 2: Plan Ahead
- Announce maintenance time to students beforehand
- Disable access 15 minutes before planned window
- Re-enable 5 minutes after done

### Tip 3: Test First
1. Suspend the system briefly
2. Verify students see the page
3. Resume
4. Plan full maintenance knowing it works

### Tip 4: Keep Reasons Short
- Suspensions are stressful
- Be empathetic and concise
- No need to explain technical details

### Tip 5: Monitor Active Sessions
Before suspending, know that:
- Students mid-vote can resume when system is back
- Their progress is saved
- No votes are lost

---

## 🆘 Troubleshooting

### Q: I suspended the system but students can still vote

**A:** 
1. Clear your browser cache (Ctrl+Shift+Delete)
2. Try a different browser or incognito window
3. Check that "Is Active" is unchecked in admin panel
4. Refresh the admin page to verify

### Q: I want to edit the message but it keeps showing the old one

**A:**
1. Click "Edit" on the System Status again
2. Change the reason text
3. Click "Save" (not just navigate away)
4. Verify change took effect

### Q: Can I let some students through while others are blocked?

**A:** 
No, the lock is all-or-nothing. However, you could:
- Suspend for students while leaving `/admin/` open for staff
- Admins (is_staff=True) can see everything

### Q: How do I check if the system is active?

**A:** 
Go to `/admin/core/systemstatus/` and look at the "Is Active" checkbox:
- ☑ Checked = System active, students can vote
- ☐ Unchecked = System suspended, students blocked

---

## 📊 Status Reference

| Status | Is Active | Students Can Vote | Admins Access /admin/ | Suspension Reason Visible |
|--------|-----------|-------------------|----------------------|--------------------------|
| 🟢 Normal | ☑ Yes | ✅ Yes | ✅ Yes | ✖️ No |
| 🔴 Suspended | ☐ No | ❌ No | ✅ Yes | ✅ Yes (if provided) |

---

## 🔐 Security Notes

✅ **Only admins can change system status** - requires `/admin/` access  
✅ **Changes are instant** - no server restart needed  
✅ **Data is never deleted** - suspension is reversible  
✅ **Audit trail exists** - all changes logged with timestamps  
✅ **Sessions are preserved** - users mid-action aren't kicked  

---

## 📱 Mobile Admin Access

You can manage the system from anywhere:

1. Open `/admin/` on your phone/tablet
2. Login with admin credentials
3. Click "System Status"
4. Toggle "Is Active" on/off
5. Save

✅ **The system responds within seconds worldwide**

---

## 🎓 Training Checklist

If training other admins, ensure they know:

- [ ] How to access the System Status page (`/admin/core/systemstatus/`)
- [ ] How to uncheck "Is Active" to suspend
- [ ] How to check "Is Active" to resume
- [ ] How to write a clear suspension reason
- [ ] That changes take effect instantly (no redeploy)
- [ ] That admins can always access `/admin/`
- [ ] That student votes are never lost
- [ ] That this is not a replacement for proper testing

---

## 📞 Support

If you have questions:

1. **Check the implementation**: `SYSTEM_ACCESS_LOCK.md` (technical docs)
2. **Quick reference**: `QUICK_START_SYSTEM_LOCK.md` (user guide)
3. **Review the code**: 
   - Model: `core/models.py` → `SystemStatus`
   - Middleware: `core/middleware.py`
   - Admin: `core/admin.py` → `SystemStatusAdmin`

---

**Remember**: You control when students can vote. Use it wisely.

**Butere Technical Training Institute — Fair. Secure. Transparent Elections.**
