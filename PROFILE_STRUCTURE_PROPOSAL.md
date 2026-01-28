# User Profile & Navigation Structure Proposal

## 1. USER PROFILE PAGE (New)

### Path & Access
- **Student Profile**: `/student/profile/`
- **Admin Profile**: `/admin/profile/`
- Access: Login required

---

## 2. STUDENT PROFILE PAGE STRUCTURE

### Layout
```
┌─────────────────────────────────────────────┐
│ Student Navigation Bar (Updated)            │
│  [Logo] [Elections] [Results] [Notifications]  │
│                           [Profile ▼] [Theme] [Logout]
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  STUDENT PROFILE PAGE                       │
├─────────────────────────────────────────────┤
│                                             │
│  ┌───────────────────────────────────────┐  │
│  │  Profile Header                       │  │
│  │  ┌─────────────┐                      │  │
│  │  │   Avatar    │  Full Name           │  │
│  │  │  (Initials) │  Admission: STU001   │  │
│  │  └─────────────┘  Class: Form 4A      │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  ┌───────────────────────────────────────┐  │
│  │  Account Information                  │  │
│  ├───────────────────────────────────────┤  │
│  │  Email: john.doe@school.com           │  │
│  │  Admission Number: STU001             │  │
│  │  Class: Form 4A                       │  │
│  │  Account Created: Jan 15, 2026        │  │
│  │  Last Updated: Jan 26, 2026           │  │
│  │  Status: ✓ Active                     │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  ┌───────────────────────────────────────┐  │
│  │  Voting Statistics                    │  │
│  ├───────────────────────────────────────┤  │
│  │  Total Elections Participated: 3      │  │
│  │  Total Votes Cast: 12                 │  │
│  │  Elections Pending: 1                 │  │
│  │  Last Vote: Jan 24, 2026              │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  ┌───────────────────────────────────────┐  │
│  │  Actions                              │  │
│  │  [Edit Profile] [Change Password]     │  │
│  │  [View Voting History] [Download QR]  │  │
│  └───────────────────────────────────────┘  │
│                                             │
└─────────────────────────────────────────────┘
```

### Sections
1. **Profile Header**
   - Avatar with initials (generated from name)
   - Full Name
   - Admission Number
   - Class/Form

2. **Account Information**
   - Email
   - Admission Number
   - Class
   - Account Created Date
   - Last Updated Date
   - Status Badge

3. **Voting Statistics**
   - Total Elections Participated
   - Total Votes Cast
   - Elections Pending
   - Last Vote Date

4. **Quick Actions**
   - Edit Profile Button
   - Change Password Button
   - View Voting History Link
   - Download Voter ID QR Code (future)

---

## 3. ADMIN PROFILE PAGE STRUCTURE

### Layout
```
┌──────────────────────────────────────────────────────┐
│ Admin Navigation Bar (Updated)                       │
│  [Logo] [Dashboard] [Elections] [Positions] [Users]  │
│                     [Admin ▼] [Theme] [Logout]       │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  ADMIN PROFILE PAGE                                  │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │  Profile Header                                │  │
│  │  ┌─────────────┐                               │  │
│  │  │   Avatar    │  Full Name                    │  │
│  │  │  (Initials) │  Role: Administrator          │  │
│  │  └─────────────┘  Email: admin@school.com     │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │  Account Information                           │  │
│  ├────────────────────────────────────────────────┤  │
│  │  Email: admin@school.com                       │  │
│  │  Full Name: Admin User                         │  │
│  │  Role: Administrator                           │  │
│  │  Account Created: Oct 1, 2024                  │  │
│  │  Last Login: Jan 26, 2026 at 3:45 PM          │  │
│  │  Status: ✓ Active                              │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │  Admin Statistics                              │  │
│  ├────────────────────────────────────────────────┤  │
│  │  Elections Created: 5                          │  │
│  │  Positions Managed: 18                         │  │
│  │  Candidates Approved: 45                       │  │
│  │  Total Votes Counted: 450                      │  │
│  │  Active Elections: 2                           │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │  System Access                                 │  │
│  ├────────────────────────────────────────────────┤  │
│  │  [✓] Create Elections                          │  │
│  │  [✓] Manage Positions                          │  │
│  │  [✓] Manage Candidates                         │  │
│  │  [✓] View Results                              │  │
│  │  [✓] Manage System Settings                    │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │  Quick Actions                                 │  │
│  │  [Edit Profile] [Change Password]              │  │
│  │  [View Activity Log] [System Settings]         │  │
│  │  [Manage Users] [Backup Data]                  │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### Sections
1. **Profile Header**
   - Avatar with initials
   - Full Name
   - Role Badge
   - Email

2. **Account Information**
   - Email
   - Full Name
   - Role
   - Account Created Date
   - Last Login Date/Time
   - Status Badge

3. **Admin Statistics**
   - Elections Created Count
   - Positions Managed Count
   - Candidates Approved Count
   - Total Votes Counted
   - Active Elections Count

4. **System Access**
   - Checklist of permissions (all checked for admin)
   - Visual indicators

5. **Quick Actions**
   - Edit Profile Button
   - Change Password Button
   - View Activity Log Link
   - System Settings Link
   - Manage Users Link
   - Backup Data Link

---

## 4. NAVIGATION BAR UPDATES

### Student Navigation Bar (base_student.html)

**Current Structure:**
```
[Logo] [Nav Links] ........... [User Name | Theme Toggle | Logout]
```

**Proposed Structure:**
```
[Logo] [Elections] [Results] [Notifications] ....... [Profile ▼] [Theme Toggle] [Logout]
```

**Changes:**
1. Move **Profile** to a dropdown menu (user icon with name)
2. Add **Notifications** link (icon based)
3. Keep existing nav links: Elections, Results
4. Keep Theme Toggle
5. Keep Logout

**Profile Dropdown Menu:**
- My Profile
- Edit Profile
- Change Password
- ─────────────
- Logout (duplicate for convenience)

---

### Admin Navigation Bar (base_admin.html)

**Current Structure:**
```
┌─────────────────────────────────┐
│ [Logo] [Nav Links]  [Theme] [Logout]
└─────────────────────────────────┘
```

**Proposed Structure:**
```
┌──────────────────────────────────────────────────┐
│ [Logo] [Dashboard] [Elections] [Candidates]      │
│                    [Positions] [Users] [Settings]│
│                    ............ [Admin ▼] [Theme] [Logout]
└──────────────────────────────────────────────────┘
```

**Changes:**
1. Add **Admin** dropdown menu (replaces plain user info)
2. Add **Users** link (if not present)
3. Add **Settings** link (if not present)
4. Reorganize nav items for better flow

**Admin Dropdown Menu:**
- My Profile
- Edit Profile
- Change Password
- ─────────────
- Activity Log
- System Settings
- ─────────────
- Logout (duplicate for convenience)

---

## 5. IMPLEMENTATION PLAN

### Views to Create:
1. `student_profile_view()` - GET/POST profile page
2. `student_profile_edit_view()` - Edit profile form
3. `student_change_password_view()` - Change password
4. `admin_profile_view()` - GET/POST profile page
5. `admin_profile_edit_view()` - Edit profile form
6. `admin_change_password_view()` - Change password

### Templates to Create:
1. `student_profile.html` - Student profile display
2. `student_profile_edit.html` - Student profile edit form
3. `student_change_password.html` - Change password form
4. `admin_profile.html` - Admin profile display
5. `admin_profile_edit.html` - Admin profile edit form
6. `admin_change_password.html` - Change password form

### Navigation Templates to Update:
1. `base_student.html` - Update nav with dropdown
2. `base_admin.html` - Update nav with dropdown

### URLs to Add:
```python
path('student/profile/', student_profile_view, name='student_profile')
path('student/profile/edit/', student_profile_edit_view, name='student_profile_edit')
path('student/profile/change-password/', student_change_password_view, name='student_change_password')
path('admin/profile/', admin_profile_view, name='admin_profile')
path('admin/profile/edit/', admin_profile_edit_view, name='admin_profile_edit')
path('admin/profile/change-password/', admin_change_password_view, name='admin_change_password')
```

---

## 6. DESIGN CONSISTENCY

### Colors (CSS Variables Already Available):
- Primary: `--primary` (#4f46e5)
- Text: `--text-main`, `--text-muted`
- Background: `--bg-body`, `--card-bg`
- Borders: `--border-color`
- Dark Theme Support: `[data-theme="dark"]`

### Icons Used:
- Profile: `<i class="fas fa-user-circle"></i>`
- Edit: `<i class="fas fa-edit"></i>`
- Password: `<i class="fas fa-lock"></i>`
- Logout: `<i class="fas fa-sign-out-alt"></i>`
- Notifications: `<i class="fas fa-bell"></i>`
- Settings: `<i class="fas fa-cog"></i>`

---

## 7. SECURITY CONSIDERATIONS

✅ Login required for profile pages
✅ Only admin/student can view own profile (no cross-viewing)
✅ Password changes require current password verification
✅ Profile edits logged in activity audit
✅ Sensitive data (email) cannot be changed by user (admin-only)

---

## APPROVAL CHECKLIST

- [ ] Student profile layout approved
- [ ] Admin profile layout approved
- [ ] Student nav dropdown approved
- [ ] Admin nav dropdown approved
- [ ] View structure approved
- [ ] Security measures approved
- [ ] Ready for implementation

**Please review and approve the structure above. Comment on any changes needed before I proceed with implementation.**
