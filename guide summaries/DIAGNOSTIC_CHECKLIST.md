# 🔍 VOTING SYSTEM - COMPREHENSIVE DIAGNOSTIC CHECKLIST

**Date**: January 26, 2026
**Purpose**: Verify all critical bugs are fixed

---

## ✅ HIERARCHY MODEL VERIFICATION

### Position → Election Relationship
```python
# VERIFY IN DJANGO SHELL:
from core.models import Position, Election

# Should return positions for each election
for election in Election.objects.all():
    positions = election.positions.all()
    print(f"{election.title}: {positions.count()} positions")

# ✅ Expected: Each election has its positions
```

### Candidate → Position Relationship
```python
# VERIFY IN DJANGO SHELL:
from core.models import Candidate, Position

# Should return candidates for each position
for position in Position.objects.all():
    candidates = position.candidates.all()
    print(f"{position.title}: {candidates.count()} candidates")

# ✅ Expected: Each position has its candidates
```

### Candidate Approval Status
```python
# VERIFY IN DJANGO SHELL:
from core.models import Candidate

# Should show approved vs unapproved
approved = Candidate.objects.filter(approved=True).count()
unapproved = Candidate.objects.filter(approved=False).count()
print(f"Approved: {approved}, Unapproved: {unapproved}")

# ✅ Expected: At least some approved candidates
```

### Vote → (Position, Voter) Relationship
```python
# VERIFY IN DJANGO SHELL:
from core.models import Vote

# Should show votes recorded
for vote in Vote.objects.all()[:5]:
    print(f"Vote: {vote.candidate.full_name} by {vote.voter_id}")

# ✅ Expected: Votes exist with correct candidate & voter_id
```

---

## ✅ VIEW LOGIC VERIFICATION

### vote() Function - Hierarchy Enforcement

**Check 1: Election Scope**
```python
# In core/views.py, line ~415
positions = election.positions.prefetch_related(...).all()

# ✅ VERIFY: Using election.positions (scoped to election)
```

**Check 2: Approved Candidate Filter**
```python
# In core/views.py, line ~414-420
approved_candidates = Candidate.objects.filter(approved=True)
positions = election.positions.prefetch_related(
    Prefetch('candidates', queryset=approved_candidates)
)

# ✅ VERIFY: Only approved candidates loaded
```

**Check 3: Double-Vote Prevention**
```python
# In core/views.py, line ~445
existing_vote = Vote.objects.filter(
    position=position,
    voter_id=voter_id
).exists()

# ✅ VERIFY: Checking (position, voter_id) unique pair
```

**Check 4: Three-Level Validation**
```python
# In core/views.py, line ~437-442
candidate = Candidate.objects.get(
    id=candidate_id,
    position=position,              # Level 1: Position
    position__election=election,    # Level 2: Election
    approved=True                   # Level 3: Approval
)

# ✅ VERIFY: All three checks present
```

---

## ✅ MODEL VALIDATION VERIFICATION

### Vote.save() Enforcement
```python
# In core/models.py, line ~192-204
def save(self, *args, **kwargs):
    # Check 1: Position match
    if self.candidate.position != self.position:
        raise ValueError("...Hierarchy must be strictly maintained...")
    
    # Check 2: Approval status
    if not self.candidate.approved:
        raise ValueError(f"Cannot vote for unapproved candidate...")
    
    super().save(*args, **kwargs)

# ✅ VERIFY: Both checks raise ValueError (not silent)
```

---

## ✅ TEMPLATE RENDERING VERIFICATION

### Candidate Display CSS
```html
<!-- In core/templates/core/vote.html, line ~76 -->
.candidate-option {
    display: block;  /* ✅ MUST BE 'block' not 'none' */
}

<!-- ✅ VERIFY: Candidates are VISIBLE, not hidden -->
```

### Candidate Loop Structure
```html
<!-- In core/templates/core/vote.html, line ~20-42 -->
{% for position in positions %}
    <div class="position-section">
        <h3>{{ position.title }}</h3>
        {% for candidate in position.candidates.all %}
            <div class="candidate-option">
                <!-- Candidate content -->
            </div>
        {% endfor %}
    </div>
{% endfor %}

<!-- ✅ VERIFY: Inner loop over position.candidates exists -->
```

---

## 🧪 FUNCTIONAL TESTS

### Test 1: UI Rendering
```
STEPS:
1. python manage.py runserver
2. Login as student
3. Go to active election
4. Click "Vote Now"

EXPECTED RESULTS:
✅ Page shows position headings
✅ Under each position, see candidate cards
✅ Each card shows:
   - Candidate photo or 📸 placeholder
   - Candidate name
   - Manifesto preview
   - Radio button to select
✅ Candidate list is NOT empty
```

### Test 2: Unapproved Candidate Filtering
```
STEPS:
1. In Django admin: core/Candidate
2. Find an approved candidate
3. Uncheck the "Approved" checkbox
4. Save
5. Refresh voting page

EXPECTED RESULTS:
✅ That candidate is NO LONGER visible
✅ Page shows "No candidates for this position yet" OR
✅ Other approved candidates still visible
```

### Test 3: Vote Submission
```
STEPS:
1. Select one candidate per position
2. Click "Submit Votes"

EXPECTED RESULTS:
✅ Success message appears
✅ Redirect to dashboard
✅ In database: Vote objects created
```

### Test 4: Double-Vote Prevention
```
STEPS:
1. Submit votes for all positions
2. Try to open voting page again
3. Try to vote again

EXPECTED RESULTS:
✅ Cannot open voting page (already voted)
  OR
✅ Try to submit → "You have already voted for [position]"
```

### Test 5: Cross-Election Prevention
```
STEPS:
1. Create two elections (E1, E2)
2. Try to manually craft vote for candidate from E2 while voting in E1

EXPECTED RESULTS:
✅ Cannot select candidate from E2 (not in dropdown)
✅ If attempted via URL manipulation:
   "Invalid or unapproved candidate" error
```

---

## 📊 DATABASE VERIFICATION

### Check Relationship Integrity
```sql
-- In Django shell or SQL:
SELECT COUNT(*) FROM core_position WHERE election_id IS NULL;
-- ✅ Expected: 0 (all positions have election)

SELECT COUNT(*) FROM core_candidate WHERE position_id IS NULL;
-- ✅ Expected: 0 (all candidates have position)

SELECT COUNT(*) FROM core_vote WHERE position_id IS NULL;
-- ✅ Expected: 0 (all votes have position)
```

### Check Approval Status
```sql
SELECT COUNT(*) FROM core_candidate WHERE approved=1;
-- ✅ Expected: > 0 (some candidates approved)

SELECT COUNT(*) FROM core_candidate WHERE approved=0;
-- ✅ Expected: >= 0 (may have unapproved)
```

### Check Votes Recorded Correctly
```sql
SELECT 
    v.id, 
    c.full_name, 
    p.title as position, 
    e.title as election
FROM core_vote v
JOIN core_candidate c ON v.candidate_id = c.id
JOIN core_position p ON v.position_id = p.id
JOIN core_election e ON p.election_id = e.id
LIMIT 10;

-- ✅ Expected: 
--   - Each vote has a candidate
--   - Each candidate in correct position
--   - Each position in correct election
--   - No cross-election data
```

---

## 🔐 SECURITY VERIFICATION

### Can Cross-Election Vote Injection Occur?
```
TEST: Try to vote for candidate from different election

RESULT MUST BE: ❌ BLOCKED
Error message: "Invalid or unapproved candidate"
Vote not recorded: ✅
```

### Can Unapproved Candidate Receive Votes?
```
TEST: 
1. Set candidate.approved = False
2. Try to vote for it

RESULT MUST BE: ❌ BLOCKED
In view: approved=True filter
In model: if not self.candidate.approved: raise ValueError()
Vote not recorded: ✅
```

### Can Position Mismatches Occur?
```
TEST:
1. Manually create Vote with:
   candidate from position A
   vote.position = position B (different)

RESULT MUST BE: ❌ BLOCKED
In model: ValueError raised
Vote not created: ✅
```

### Can Voter Double-Vote Same Position?
```
TEST:
1. Vote for position X with candidate A
2. Try to vote for position X with candidate B

RESULT MUST BE: ❌ BLOCKED
Error message: "You have already voted for [position]"
Second vote not recorded: ✅
```

---

## 📝 REQUIRED FILES - VERIFICATION

### File: core/templates/core/vote.html
```
✅ Line 76: .candidate-option { display: block; }
✅ Line 20-42: {% for candidate in position.candidates.all %}
✅ Line 27: <input type="radio" name="position_{{ position.id }}" ...>
✅ Line 32: <img src="{{ candidate.photo.url }}" ...>
✅ Line 35: <h4>{{ candidate.full_name }}</h4>
```

### File: core/views.py
```
✅ Line 7: from django.db.models import ..., Prefetch
✅ Line 414-420: Prefetch query optimization
✅ Line 437-442: Three-level candidate validation
✅ Line 445: Double-vote check
✅ Line 460: Vote creation with explicit position
```

### File: core/models.py
```
✅ Line 192-204: Vote.save() validation
✅ Line 194: if self.candidate.position != self.position: raise ValueError(...)
✅ Line 197: if not self.candidate.approved: raise ValueError(...)
```

---

## ✅ FINAL SIGN-OFF

When ALL of the above verify as ✅:

- [ ] Models correctly linked (Election → Position → Candidate → Vote)
- [ ] Views enforce three-level hierarchy
- [ ] Models validate on save()
- [ ] Template renders candidates correctly
- [ ] CSS displays candidates
- [ ] Candidates are filterable by approval
- [ ] Double-vote prevented
- [ ] Cross-election votes blocked
- [ ] UI fully functional
- [ ] All tests pass

**System Status**: 🟢 PRODUCTION READY

---

**Verification Date**: _______________
**Verified By**: _______________
**Status**: 🔵 READY FOR DEPLOYMENT

