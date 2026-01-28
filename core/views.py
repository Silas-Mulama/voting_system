from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Count, Q, Prefetch
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
import uuid
import csv
<<<<<<< HEAD
import json
=======
>>>>>>> fda6d5ef726056f0c8eabf2946f19a342a16bf18
from .decorators import student_required, admin_required, voting_page_required
from .models import Election, Position, Candidate, Vote
from .forms import StudentBulkUploadForm, ElectionForm, PositionForm, CandidateForm
from .utils import StudentBulkUploadValidator, bulk_create_students, log_audit_event

User = get_user_model()


def index(request):
	"""Root URL - redirect to appropriate dashboard."""
	if not request.user.is_authenticated:
		return redirect('student_login')
	if request.user.is_student:
		if not request.user.password_changed:
			return redirect('change_password_first')
		return redirect('student_dashboard')
	return redirect('admin_dashboard')


@require_http_methods(["GET", "POST"])
def admin_login(request):
    if request.user.is_authenticated:
        if request.user.is_student:
            return redirect('student_dashboard')
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            if user.is_student:
                messages.error(request, 'Students must use the student login page.')
                return redirect('admin_login')
            login(request, user)
            # ✅ LOG: Admin login successful
            log_audit_event(request, 'login', f'Admin login: {email}', user)
            return redirect('admin_dashboard')
        else:
            # ✅ LOG: Failed admin login attempt
            log_audit_event(request, 'login_failed', f'Failed admin login attempt: {email}')
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'core/admin_login.html')


@require_http_methods(["GET", "POST"])
def student_login(request):
    if request.user.is_authenticated:
        if not request.user.is_student:
            return redirect('admin_dashboard')
        if not request.user.password_changed:
            return redirect('change_password_first')
        return redirect('student_dashboard')
    
    if request.method == 'POST':
        admission_number = request.POST.get('admission_number')
        password = request.POST.get('password')
        
        user = authenticate(request, username=admission_number, password=password)
        if user is not None:
            if not user.is_student:
                messages.error(request, 'Admins must use the admin login page.')
                return redirect('student_login')
            login(request, user)
            # ✅ LOG: Student login successful
            log_audit_event(request, 'login', f'Student login: {admission_number}', user)
            if not user.password_changed:
                return redirect('change_password_first')
            return redirect('student_dashboard')
        else:
            # ✅ LOG: Failed student login attempt
            log_audit_event(request, 'login_failed', f'Failed student login attempt: {admission_number}')
            messages.error(request, 'Invalid admission number or password.')
    
    return render(request, 'core/student_login.html')


@login_required(login_url='student_login')
@student_required
@require_http_methods(["GET", "POST"])
@login_required(login_url='student_login')
@student_required
def change_password_first(request):
    """Force password change for students on first login."""
    if request.user.password_changed:
        return redirect('student_dashboard')
    
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not request.user.check_password(old_password):
            messages.error(request, 'Current password is incorrect.')
            return render(request, 'core/change_password_first.html')
        
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return render(request, 'core/change_password_first.html')
        
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'core/change_password_first.html')
        
        request.user.set_password(new_password)
        request.user.password_changed = True
        request.user.save()
        # ✅ LOG: Password change (first login)
        log_audit_event(request, 'password_change', 'First login password change', request.user)
        messages.success(request, 'Password changed successfully. Please login again.')
        logout(request)
        return redirect('student_login')
    
    return render(request, 'core/change_password_first.html')


@login_required(login_url='student_login')
@student_required
def change_password(request):
    """Allow students to change their password anytime."""
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not request.user.check_password(old_password):
            messages.error(request, 'Current password is incorrect.')
            return render(request, 'core/change_password.html')
        
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return render(request, 'core/change_password.html')
        
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'core/change_password.html')
        
        request.user.set_password(new_password)
        request.user.save()
        # ✅ LOG: Password change
        log_audit_event(request, 'password_change', 'Student password changed', request.user)
        messages.success(request, 'Password changed successfully.')
        return redirect('student_dashboard')
    
    return render(request, 'core/change_password.html')


@login_required(login_url='admin_login')
@admin_required
def admin_dashboard(request):
    """Admin dashboard view."""
    elections_count = Election.objects.count()
    active_elections = Election.objects.filter(status='active').count()
    total_students = User.objects.filter(is_student=True).count()
    
    context = {
        'elections_count': elections_count,
        'active_elections': active_elections,
        'total_students': total_students,
    }
    return render(request, 'core/admin_dashboard.html', context)


@login_required(login_url='student_login')
@student_required
def student_dashboard(request):
    """Student dashboard view."""
    active_elections = Election.objects.filter(status='active')
    user_votes = Vote.objects.filter(voter_id=str(request.user.id))
    
    # Calculate participation rate
    all_elections = Election.objects.filter(status__in=['active', 'closed'])
    participation_rate = 0
    if all_elections.exists():
        voted_elections = all_elections.filter(positions__votes__voter_id=str(request.user.id)).distinct().count()
        participation_rate = int((voted_elections / all_elections.count()) * 100) if all_elections.count() > 0 else 0
    
    context = {
        'active_elections': active_elections,
        'total_votes': user_votes.count(),
        'participation_rate': participation_rate,
    }
    return render(request, 'core/student_dashboard.html', context)


<<<<<<< HEAD
=======
@login_required
def logout_view(request):
    """Logout view."""
    user = request.user
    # ✅ LOG: User logout
    log_audit_event(request, 'logout', f'User logout: {user.full_name if user.is_authenticated else "Unknown"}', user if user.is_authenticated else None)
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('admin_login')


>>>>>>> fda6d5ef726056f0c8eabf2946f19a342a16bf18
# ==================== STUDENT BULK UPLOAD ====================

@login_required(login_url='admin_login')
@admin_required
@require_http_methods(["GET", "POST"])
@login_required(login_url='admin_login')
@admin_required
<<<<<<< HEAD
@login_required(login_url='admin_login')
@admin_required
@require_http_methods(["GET", "POST"])
=======
>>>>>>> fda6d5ef726056f0c8eabf2946f19a342a16bf18
def upload_students(request):
    """Handle bulk student upload."""
    if request.method == 'POST':
        form = StudentBulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_obj = request.FILES['file']
            validator = StudentBulkUploadValidator()
            
            try:
                validator.validate_file(file_obj)
<<<<<<< HEAD
                
                # Store progress tracking info in session
                request.session['upload_progress'] = {
                    'status': 'processing',
                    'percentage': 0,
                    'current': 0,
                    'total': len(validator.valid_rows)
                }
                request.session.save()
                
                # Define progress callback
                def update_progress(percentage, current, total):
                    request.session['upload_progress'] = {
                        'status': 'processing',
                        'percentage': percentage,
                        'current': current,
                        'total': total
                    }
                    request.session.save()
                
                created, errors = bulk_create_students(validator.valid_rows, progress_callback=update_progress)
                
                # Mark progress as complete
                request.session['upload_progress'] = {
                    'status': 'complete',
                    'percentage': 100,
                    'current': len(created),
                    'total': len(validator.valid_rows)
                }
                request.session.save()
=======
                created, errors = bulk_create_students(validator.valid_rows)
>>>>>>> fda6d5ef726056f0c8eabf2946f19a342a16bf18
                
                if errors:
                    for error in errors:
                        messages.error(request, error)
                
                if created:
                    # ✅ LOG: Bulk student upload
                    log_audit_event(request, 'student_upload', f'Imported {len(created)} students from {file_obj.name}', request.user)
                    
                    # Store credentials in session for display
                    request.session['import_credentials'] = [
                        {
                            'admission_number': c['admission_number'],
                            'full_name': c['full_name'],
                            'email': c['email'],
                            'temp_password': c['temp_password']
                        }
                        for c in created
                    ]
                    request.session['import_count'] = len(created)
                    
<<<<<<< HEAD
                    # Clear upload progress from session
                    request.session.pop('upload_progress', None)
                    request.session.save()
                    
                    return redirect('student_credentials')
            except Exception as e:
                request.session.pop('upload_progress', None)
                request.session.save()
=======
                    return redirect('student_credentials')
            except Exception as e:
>>>>>>> fda6d5ef726056f0c8eabf2946f19a342a16bf18
                messages.error(request, f"Import failed: {str(e)}")
    else:
        form = StudentBulkUploadForm()
    
    context = {'form': form}
    return render(request, 'core/upload_students.html', context)


@login_required(login_url='admin_login')
@admin_required
<<<<<<< HEAD
@require_http_methods(["GET"])
def get_upload_progress(request):
    """Get the current upload progress."""
    progress = request.session.get('upload_progress', {
        'status': 'idle',
        'percentage': 0,
        'current': 0,
        'total': 0
    })
    return JsonResponse(progress)



@login_required(login_url='admin_login')
@admin_required
=======
>>>>>>> fda6d5ef726056f0c8eabf2946f19a342a16bf18
def student_credentials(request):
    """Display student credentials after import."""
    credentials = request.session.get('import_credentials', [])
    import_count = request.session.get('import_count', 0)
    
    if not credentials:
        messages.warning(request, 'No credentials available.')
        return redirect('upload_students')
    
    context = {
        'credentials': credentials,
        'import_count': import_count,
    }
    return render(request, 'core/student_credentials.html', context)


@login_required(login_url='admin_login')
@admin_required
def download_student_credentials(request):
    """Download student credentials as CSV."""
    credentials = request.session.get('import_credentials', [])
    
    if not credentials:
        messages.warning(request, 'No credentials available for download.')
        return redirect('student_credentials')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="student_credentials.csv"'
    
    writer = csv.writer(response)
    # Write headers
    writer.writerow(['Admission Number', 'Full Name', 'Email', 'Temporary Password'])
    
    # Write data
    for cred in credentials:
        writer.writerow([
            cred['admission_number'],
            cred['full_name'],
            cred['email'],
            cred['temp_password']
        ])
    
    # Clear session data after download
    del request.session['import_credentials']
    del request.session['import_count']
    
    return response


# ==================== ELECTION MANAGEMENT ====================

@login_required(login_url='admin_login')
@admin_required
def election_list(request):
    """List all elections."""
    elections = Election.objects.all()
    context = {'elections': elections}
    return render(request, 'core/election_list.html', context)


@login_required(login_url='admin_login')
@admin_required
@require_http_methods(["GET", "POST"])
def election_create(request):
    """Create a new election."""
    if request.method == 'POST':
        form = ElectionForm(request.POST)
        if form.is_valid():
            election = form.save()
            # ✅ LOG: Election created
            log_audit_event(request, 'election_created', f'Election created: {election.title}', request.user)
            messages.success(request, 'Election created successfully')
            return redirect('election_list')
    else:
        form = ElectionForm()
    
    context = {'form': form, 'title': 'Create Election'}
    return render(request, 'core/election_form.html', context)


@login_required(login_url='admin_login')
@admin_required
@require_http_methods(["GET", "POST"])
def election_update(request, pk):
    """Update an election."""
    election = get_object_or_404(Election, pk=pk)
    
    if request.method == 'POST':
        form = ElectionForm(request.POST, instance=election)
        if form.is_valid():
            election = form.save()
            # ✅ LOG: Election updated
            log_audit_event(request, 'election_updated', f'Election updated: {election.title}', request.user)
            messages.success(request, 'Election updated successfully')
            return redirect('election_list')
    else:
        form = ElectionForm(instance=election)
    
    context = {'form': form, 'title': 'Update Election', 'election': election}
    return render(request, 'core/election_form.html', context)


@login_required(login_url='admin_login')
@admin_required
def election_detail(request, pk):
    """View election details."""
    election = get_object_or_404(Election, pk=pk)
    positions = election.positions.all()
    
    context = {
        'election': election,
        'positions': positions,
    }
    return render(request, 'core/election_detail.html', context)


@login_required(login_url='admin_login')
@admin_required
@require_http_methods(["POST"])
def election_delete(request, pk):
    """Delete an election."""
    election = get_object_or_404(Election, pk=pk)
    election_title = election.title
    # ✅ LOG: Election deleted (before deletion)
    log_audit_event(request, 'election_updated', f'Election deleted: {election_title}', request.user)
    election.delete()
    messages.success(request, 'Election deleted successfully')
    return redirect('election_list')


# ==================== POSITION MANAGEMENT ====================

@login_required(login_url='admin_login')
@admin_required
@require_http_methods(["GET", "POST"])
def position_create(request, election_pk):
    """Create a position."""
    election = get_object_or_404(Election, pk=election_pk)
    
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            position = form.save(commit=False)
            position.election = election
            position.save()
            messages.success(request, 'Position created successfully')
            return redirect('election_detail', pk=election_pk)
    else:
        form = PositionForm()
    
    context = {'form': form, 'election': election, 'title': 'Create Position'}
    return render(request, 'core/position_form.html', context)


@login_required(login_url='admin_login')
@admin_required
@require_http_methods(["GET", "POST"])
def position_update(request, pk):
    """Update a position."""
    position = get_object_or_404(Position, pk=pk)
    
    if request.method == 'POST':
        form = PositionForm(request.POST, instance=position)
        if form.is_valid():
            form.save()
            messages.success(request, 'Position updated successfully')
            return redirect('election_detail', pk=position.election.pk)
    else:
        form = PositionForm(instance=position)
    
    context = {'form': form, 'position': position, 'title': 'Update Position'}
    return render(request, 'core/position_form.html', context)


@login_required(login_url='admin_login')
@admin_required
@require_http_methods(["POST"])
def position_delete(request, pk):
    """Delete a position."""
    position = get_object_or_404(Position, pk=pk)
    election_pk = position.election.pk
    
    if not position.can_delete():
        messages.error(request, 'Cannot delete position with existing votes')
        return redirect('election_detail', pk=election_pk)
    
    position.delete()
    messages.success(request, 'Position deleted successfully')
    return redirect('election_detail', pk=election_pk)


# ==================== CANDIDATE MANAGEMENT ====================

@login_required(login_url='admin_login')
@admin_required
@require_http_methods(["GET", "POST"])
def candidate_create(request, position_pk):
    """Create a candidate."""
    position = get_object_or_404(Position, pk=position_pk)
    
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES)
        student_id = request.POST.get('student_id')
        
        # Validate that a student is selected
        if not student_id:
            messages.error(request, 'Please select a student to make a candidate')
            students = User.objects.filter(is_student=True)
            context = {
                'form': form,
                'position': position,
                'students': students,
                'title': 'Create Candidate'
            }
            return render(request, 'core/candidate_form.html', context)
        
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.position = position
            # Link to student
            try:
                candidate.user = User.objects.get(id=student_id, is_student=True)
            except User.DoesNotExist:
                messages.error(request, 'Selected student not found')
                students = User.objects.filter(is_student=True)
                context = {
                    'form': form,
                    'position': position,
                    'students': students,
                    'title': 'Create Candidate'
                }
                return render(request, 'core/candidate_form.html', context)
            candidate.save()
            messages.success(request, 'Candidate created successfully')
            return redirect('election_detail', pk=position.election.pk)
    else:
        form = CandidateForm()
    
    students = User.objects.filter(is_student=True)
    context = {
        'form': form,
        'position': position,
        'students': students,
        'title': 'Create Candidate'
    }
    return render(request, 'core/candidate_form.html', context)


@login_required(login_url='admin_login')
@admin_required
@require_http_methods(["GET", "POST"])
def candidate_update(request, pk):
    """Update a candidate."""
    candidate = get_object_or_404(Candidate, pk=pk)
    
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, 'Candidate updated successfully')
            return redirect('election_detail', pk=candidate.position.election.pk)
    else:
        form = CandidateForm(instance=candidate)
    
    context = {
        'form': form,
        'candidate': candidate,
        'position': candidate.position,
        'title': 'Update Candidate'
    }
    return render(request, 'core/candidate_form.html', context)


@login_required(login_url='admin_login')
@admin_required
@require_http_methods(["POST"])
def candidate_delete(request, pk):
    """Delete a candidate."""
    candidate = get_object_or_404(Candidate, pk=pk)
    election_pk = candidate.position.election.pk
    candidate.delete()
    messages.success(request, 'Candidate deleted successfully')
    return redirect('election_detail', pk=election_pk)


# ==================== STUDENT VOTING ====================

@login_required(login_url='student_login')
@student_required
<<<<<<< HEAD
@require_http_methods(["GET"])
=======
>>>>>>> fda6d5ef726056f0c8eabf2946f19a342a16bf18
def elections_list(request):
    """List elections for students."""
    elections = Election.objects.all()
    voter_id = str(request.user.id)
    
    # Add vote count to each election
    for election in elections:
        # Count distinct positions where user has voted
        voted_positions = Vote.objects.filter(
            voter_id=voter_id,
            position__election=election
        ).values('position_id').distinct().count()
        # Store explicit attributes to avoid template ambiguity
        election.user_vote_count = voted_positions
        election.total_positions = election.positions.count()
        election.is_currently_active = election.is_active()
    
    context = {
        'elections': elections,
    }
    return render(request, 'core/student_elections_list.html', context)


@login_required(login_url='student_login')
@voting_page_required
@require_http_methods(["GET", "POST"])
def vote(request, election_pk):
    """Vote in an election with strict hierarchy enforcement."""
    # ✅ STRICT: Get election first and verify it's active
    election = get_object_or_404(Election, pk=election_pk)
    
    if not election.is_active():
        messages.error(request, 'This election is not active')
        return redirect('elections_list')
    
    # ✅ STRICT: Get ONLY positions from THIS election with APPROVED candidates
    # Using prefetch_related to optimize query and filter approved candidates
    approved_candidates = Candidate.objects.filter(approved=True)
    positions = election.positions.prefetch_related(
        Prefetch('candidates', queryset=approved_candidates)
    ).all()
    
    if request.method == 'POST':
        voter_id = str(request.user.id)
        errors = []
        voted_positions = []
        
        # ✅ STRICT: Iterate ONLY through positions from this election
        for position in positions:
            candidate_id = request.POST.get(f'position_{position.id}')
            
            if not candidate_id:
                errors.append(f'Please select a candidate for {position.title}')
                continue
            
            # ✅ STRICT: Verify candidate belongs to THIS position AND is approved
            try:
                candidate = Candidate.objects.get(
                    id=candidate_id,
                    position=position,  # MUST belong to this position
                    position__election=election,  # MUST belong to this election
                    approved=True  # MUST be approved
                )
            except Candidate.DoesNotExist:
                errors.append(f'Invalid or unapproved candidate for {position.title}')
                continue
            
            # ✅ STRICT: Check for existing vote in THIS position only
            existing_vote = Vote.objects.filter(
                position=position,  # SCOPED to this position
                voter_id=voter_id
            ).exists()
            
            if existing_vote:
                errors.append(f'You have already voted for {position.title}')
                continue
            
            # ✅ STRICT: Create vote with explicit position assignment
            Vote.objects.create(
                candidate=candidate,
                position=position,  # Explicit assignment enforces hierarchy
                voter_id=voter_id
            )
            # ✅ LOG: Vote cast
            log_audit_event(request, 'vote_cast', f'Vote cast for {position.title}: {candidate.full_name}', request.user)
            voted_positions.append(position.title)
        
        if errors:
            for error in errors:
                messages.error(request, error)
        
        if voted_positions:
            messages.success(request, f'Votes recorded for: {", ".join(voted_positions)}')
            
            # Check if all positions voted
            remaining = positions.exclude(title__in=voted_positions)
            if remaining.exists():
                context = {
                    'election': election,
                    'positions': remaining,
                    'voted_positions': voted_positions,
                }
                return render(request, 'core/vote.html', context)
            else:
                messages.success(request, 'Thank you for voting!')
                return redirect('elections_list')
    
    context = {
        'election': election,
        'positions': positions,
    }
    return render(request, 'core/vote.html', context)


@login_required(login_url='student_login')
@student_required
def election_results(request, election_pk):
    """View election results."""
    election = get_object_or_404(Election, pk=election_pk)
    positions = election.positions.prefetch_related('candidates__votes').all()
    
    # Build results dictionary grouped by position
    results = {}
    for position in positions:
        candidates_data = []
        total_votes_in_position = 0
        
        for candidate in position.candidates.all():
            vote_count = candidate.votes.count()
            total_votes_in_position += vote_count
            candidates_data.append({
                'full_name': candidate.full_name,
                'vote_count': vote_count,
                'percentage': 0,  # Will be calculated
                'is_winner': False,
            })
        
        # Calculate percentages and find winner
        if total_votes_in_position > 0:
            max_votes = max([c['vote_count'] for c in candidates_data])
            for candidate in candidates_data:
                candidate['percentage'] = round((candidate['vote_count'] / total_votes_in_position) * 100, 1)
                if candidate['vote_count'] == max_votes:
                    candidate['is_winner'] = True
        
        # Sort by votes descending
        candidates_data.sort(key=lambda x: x['vote_count'], reverse=True)
        results[position.title] = candidates_data
    
    # Calculate turnout stats (admin only)
    turnout_stats = None
    if request.user.is_staff:
        total_students = User.objects.filter(is_student=True).count()
        total_votes_cast = Vote.objects.filter(candidate__position__election=election).values('voter_id').distinct().count()
        turnout_percentage = round((total_votes_cast / total_students * 100), 1) if total_students > 0 else 0
        
        turnout_stats = {
            'total_students': total_students,
            'total_votes': total_votes_cast,
            'turnout_percentage': turnout_percentage,
        }
    
    context = {
        'election': election,
        'positions': positions,
        'results': results,
        'turnout_stats': turnout_stats,
    }
    return render(request, 'core/election_results_student.html', context)


@login_required
@admin_required
@require_http_methods(["GET"])
def audit_logs(request):
    """View audit logs."""
    from .models import AuditLog
    
    logs = AuditLog.objects.all()
    
    # Filter by action
    action = request.GET.get('action')
    if action:
        logs = logs.filter(action=action)
    
    # Search by user
    search = request.GET.get('search')
    if search:
        logs = logs.filter(
            Q(user__email__icontains=search) |
            Q(user__admission_number__icontains=search) |
            Q(user__full_name__icontains=search)
        )
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    action_choices = AuditLog.ACTION_CHOICES
    
    context = {
        'audit_logs': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'action_choices': action_choices,
    }
    return render(request, 'core/audit_logs.html', context)


@login_required
@admin_required
@require_http_methods(["GET"])
def audit_logs_export(request):
    """Export audit logs as CSV."""
    import csv
    from .models import AuditLog
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="audit_logs.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'User', 'User Type', 'Action', 'Description', 'IP Address'])
    
    for log in AuditLog.objects.all().select_related('user'):
        user_type = 'Student' if log.user and log.user.is_student else 'Admin' if log.user else 'System'
        writer.writerow([
            log.timestamp,
            log.user.full_name if log.user else 'System',
            user_type,
            log.get_action_display(),
            log.description,
            log.ip_address or 'N/A',
        ])
    
    return response


@login_required
@admin_required
@require_http_methods(["GET"])
def election_results_admin(request):
    """Admin view for election results with comprehensive statistics."""
    elections = Election.objects.all().order_by('-created_at')
    selected_election = None
    results = {}
    turnout_stats = None
    total_votes_per_position = {}
    duration = 0
    
    election_id = request.GET.get('election_id')
    if election_id:
        selected_election = get_object_or_404(Election, pk=election_id)
        positions = selected_election.positions.prefetch_related('candidates__votes').all()
        
        # Calculate duration
        time_diff = selected_election.end_datetime - selected_election.start_datetime
        duration = round(time_diff.total_seconds() / 3600, 1)
        
        # Build results dictionary grouped by position
        for position in positions:
            candidates_data = []
            total_votes_in_position = 0
            
            for candidate in position.candidates.all():
                vote_count = candidate.votes.count()
                total_votes_in_position += vote_count
                candidates_data.append({
                    'full_name': candidate.full_name,
                    'vote_count': vote_count,
                    'percentage': 0,
                    'is_winner': False,
                })
            
            # Calculate percentages and find winner
            if total_votes_in_position > 0:
                max_votes = max([c['vote_count'] for c in candidates_data])
                for candidate in candidates_data:
                    candidate['percentage'] = round((candidate['vote_count'] / total_votes_in_position) * 100, 1)
                    if candidate['vote_count'] == max_votes:
                        candidate['is_winner'] = True
            
            # Sort by votes descending
            candidates_data.sort(key=lambda x: x['vote_count'], reverse=True)
            results[position.title] = candidates_data
            total_votes_per_position[position.title] = total_votes_in_position
        
        # Calculate turnout statistics
        total_students = User.objects.filter(is_student=True).count()
        total_votes_cast = Vote.objects.filter(candidate__position__election=selected_election).values('voter_id').distinct().count()
        turnout_percentage = round((total_votes_cast / total_students * 100), 1) if total_students > 0 else 0
        
        # Calculate average votes per position
        num_positions = selected_election.positions.count()
        avg_votes = round(total_votes_cast / num_positions, 1) if num_positions > 0 else 0
        
        turnout_stats = {
            'total_students': total_students,
            'total_votes': total_votes_cast,
            'turnout_percentage': turnout_percentage,
            'avg_votes_per_position': avg_votes,
        }
    
    context = {
        'elections': elections,
        'selected_election': selected_election,
        'results': results,
        'turnout_stats': turnout_stats,
        'total_votes_per_position': total_votes_per_position,
        'duration': duration,
    }
    return render(request, 'core/election_results_admin.html', context)


@login_required
@admin_required
@require_http_methods(["GET"])
def election_results_export_csv(request, election_pk):
    """Export election results as CSV."""
    import csv
    election = get_object_or_404(Election, pk=election_pk)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="election_results_{election.id}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Election', election.title])
    writer.writerow(['Status', election.status])
    writer.writerow(['Generated', timezone.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow([])
    
    # Turnout stats
    total_students = User.objects.filter(is_student=True).count()
    total_votes = Vote.objects.filter(candidate__position__election=election).values('voter_id').distinct().count()
    turnout = round((total_votes / total_students * 100), 1) if total_students > 0 else 0
    
    writer.writerow(['Turnout Statistics'])
    writer.writerow(['Total Students', total_students])
    writer.writerow(['Total Votes', total_votes])
    writer.writerow(['Turnout Rate (%)', turnout])
    writer.writerow([])
    
    # Results by position
    positions = election.positions.prefetch_related('candidates__votes').all()
    for position in positions:
        writer.writerow([position.title])
        writer.writerow(['Candidate', 'Votes', 'Percentage'])
        
        candidates_data = []
        total_in_pos = 0
        for candidate in position.candidates.all():
            vote_count = candidate.votes.count()
            total_in_pos += vote_count
            candidates_data.append({
                'name': candidate.full_name,
                'votes': vote_count,
            })
        
        candidates_data.sort(key=lambda x: x['votes'], reverse=True)
        for cand in candidates_data:
            percentage = round((cand['votes'] / total_in_pos * 100), 1) if total_in_pos > 0 else 0
            writer.writerow([cand['name'], cand['votes'], f'{percentage}%'])
        
        writer.writerow([])
    
    return response


def about(request):
	"""Display information about the voting system."""
	return render(request, 'core/about.html')


# ============================================================
# STUDENT PROFILE VIEWS
# ============================================================

@login_required(login_url='student_login')
def student_profile(request):
	"""Display student profile with voting statistics."""
	user = request.user
	user_id = str(user.id)
	
	# Get all votes cast by this user
	vote_count = Vote.objects.filter(voter_id=user_id).count()
	
	# Get elections this user has participated in
	elections_participated = Election.objects.filter(
		positions__votes__voter_id=user_id
	).distinct().count()
	
	# Get elections with pending votes
	all_elections = Election.objects.filter(status='active')
	pending_elections = 0
	for election in all_elections:
		positions_count = election.positions.count()
		voted_positions = Vote.objects.filter(
			voter_id=user_id,
			position__election=election
		).values('position').distinct().count()
		if voted_positions < positions_count:
			pending_elections += 1
	
	# Get last vote date
	last_vote = Vote.objects.filter(voter_id=user_id).order_by('-timestamp').first()
	last_vote_date = last_vote.timestamp if last_vote else None
	
	context = {
		'profile_user': user,
		'vote_count': vote_count,
		'elections_participated': elections_participated,
		'pending_elections': pending_elections,
		'last_vote_date': last_vote_date,
		'account_created': user.date_joined,
	}
	return render(request, 'core/student_profile.html', context)


@login_required(login_url='student_login')
@require_http_methods(["GET", "POST"])
def student_profile_edit(request):
	"""Allow student to edit their profile."""
	user = request.user
	
	if request.method == 'POST':
		# Students can only edit certain fields (not email, admission_number)
		full_name = request.POST.get('full_name', '').strip()
		
		if not full_name:
			messages.error(request, 'Full name is required')
		else:
			user.full_name = full_name
			
			# Handle profile picture upload
			if 'profile_picture' in request.FILES:
				profile_picture = request.FILES['profile_picture']
				# Validate file size (5MB max)
				if profile_picture.size > 5 * 1024 * 1024:
					messages.error(request, 'Profile picture must be less than 5MB')
					context = {'profile_user': user}
					return render(request, 'core/student_profile_edit.html', context)
				user.profile_picture = profile_picture
			
			user.save()
			messages.success(request, 'Profile updated successfully')
			return redirect('student_profile')
	
	context = {
		'profile_user': user,
	}
	return render(request, 'core/student_profile_edit.html', context)


@login_required(login_url='student_login')
@require_http_methods(["GET", "POST"])
def student_change_password(request):
	"""Student change password view."""
	if request.method == 'POST':
		old_password = request.POST.get('old_password', '')
		new_password = request.POST.get('new_password', '')
		confirm_password = request.POST.get('confirm_password', '')
		
		user = request.user
		
		if not user.check_password(old_password):
			messages.error(request, 'Current password is incorrect')
		elif new_password != confirm_password:
			messages.error(request, 'New passwords do not match')
		elif len(new_password) < 6:
			messages.error(request, 'Password must be at least 6 characters')
		else:
			user.set_password(new_password)
			user.save()
			messages.success(request, 'Password changed successfully. Please log in again.')
			log_audit_event(request, 'password_changed', 'Student changed password', user)
			return redirect('student_login')
	
	return render(request, 'core/student_change_password.html')


# ============================================================
# ADMIN PROFILE VIEWS
# ============================================================

@login_required(login_url='admin_login')
@admin_required
def admin_profile(request):
	"""Display admin profile with system statistics."""
	user = request.user
	
	# Get admin statistics
	elections_created = Election.objects.count()
	positions_managed = Position.objects.count()
	candidates_approved = Candidate.objects.filter(approved=True).count()
	total_votes = Vote.objects.count()
	active_elections = Election.objects.filter(status='active').count()
	
	context = {
		'profile_user': user,
		'elections_created': elections_created,
		'positions_managed': positions_managed,
		'candidates_approved': candidates_approved,
		'total_votes': total_votes,
		'active_elections': active_elections,
		'account_created': user.date_joined,
		'last_login': user.last_login,
	}
	return render(request, 'core/admin_profile.html', context)


@login_required(login_url='admin_login')
@admin_required
@require_http_methods(["GET", "POST"])
def admin_profile_edit(request):
	"""Allow admin to edit their profile."""
	user = request.user
	
	if request.method == 'POST':
		full_name = request.POST.get('full_name', '').strip()
		
		if not full_name:
			messages.error(request, 'Full name is required')
		else:
			user.full_name = full_name
			
			# Handle profile picture upload
			if 'profile_picture' in request.FILES:
				profile_picture = request.FILES['profile_picture']
				# Validate file size (5MB max)
				if profile_picture.size > 5 * 1024 * 1024:
					messages.error(request, 'Profile picture must be less than 5MB')
					context = {'profile_user': user}
					return render(request, 'core/admin_profile_edit.html', context)
				user.profile_picture = profile_picture
			
			user.save()
			messages.success(request, 'Profile updated successfully')
			log_audit_event(request, 'profile_updated', 'Admin updated profile', user)
			return redirect('admin_profile')
	
	context = {
		'profile_user': user,
	}
	return render(request, 'core/admin_profile_edit.html', context)


@login_required(login_url='admin_login')
@admin_required
@require_http_methods(["GET", "POST"])
def admin_change_password(request):
	"""Admin change password view."""
	if request.method == 'POST':
		old_password = request.POST.get('old_password', '')
		new_password = request.POST.get('new_password', '')
		confirm_password = request.POST.get('confirm_password', '')
		
		user = request.user
		
		if not user.check_password(old_password):
			messages.error(request, 'Current password is incorrect')
		elif new_password != confirm_password:
			messages.error(request, 'New passwords do not match')
		elif len(new_password) < 6:
			messages.error(request, 'Password must be at least 6 characters')
		else:
			user.set_password(new_password)
			user.save()
			messages.success(request, 'Password changed successfully. Please log in again.')
			log_audit_event(request, 'password_changed', 'Admin changed password', user)
			return redirect('admin_login')
	
	return render(request, 'core/admin_change_password.html')


# Activity log view (stub for future implementation)
@login_required(login_url='admin_login')
@admin_required
def activity_log(request):
	"""Display activity log for admin."""
	# This is a stub - will implement full activity log later
	messages.info(request, 'Activity log feature coming soon')
	return redirect('admin_profile')
