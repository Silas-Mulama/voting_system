"""
Tests for System Access Lock feature.
Tests the SystemStatus model, middleware, and access control.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import SystemStatus

User = get_user_model()


class SystemStatusModelTests(TestCase):
    """Test SystemStatus model functionality."""

    def test_system_status_singleton(self):
        """Test that SystemStatus uses get_or_create singleton pattern."""
        status1 = SystemStatus.get_status()
        status2 = SystemStatus.get_status()
        self.assertEqual(status1.pk, status2.pk)
        self.assertEqual(SystemStatus.objects.count(), 1)

    def test_default_status_is_active(self):
        """Test that default status is active."""
        status = SystemStatus.get_status()
        self.assertTrue(status.is_active)

    def test_suspend_and_resume(self):
        """Test suspending and resuming system."""
        status = SystemStatus.get_status()
        
        # Suspend
        status.is_active = False
        status.suspension_reason = "Test suspension"
        status.save()
        
        # Verify suspension
        status = SystemStatus.get_status()
        self.assertFalse(status.is_active)
        self.assertEqual(status.suspension_reason, "Test suspension")
        
        # Resume
        status.is_active = True
        status.suspension_reason = ""
        status.save()
        
        # Verify active
        status = SystemStatus.get_status()
        self.assertTrue(status.is_active)


class SystemAccessLockMiddlewareTests(TestCase):
    """Test SystemAccessLockMiddleware access control."""

    def setUp(self):
        """Set up test users and client."""
        self.client = Client()
        
        # Create a student user
        self.student = User.objects.create_user(
            email='student@test.com',
            admission_number='TEST/00001/24S',
            full_name='Test Student',
            programme='DICT',
            year_of_study=1,
            is_student=True,
            password='testpass123'
        )
        self.student.password_changed = True
        self.student.save()
        
        # Create an admin user
        self.admin = User.objects.create_user(
            email='admin@test.com',
            full_name='Test Admin',
            password='adminpass123',
            is_staff=True,
            is_superuser=True
        )

    def test_system_active_student_can_access(self):
        """Test that students can access system when active."""
        # Ensure system is active
        status = SystemStatus.get_status()
        status.is_active = True
        status.save()
        
        self.client.login(email='student@test.com', password='testpass123')
        
        # Student should access student dashboard
        response = self.client.get(reverse('student_dashboard'))
        self.assertNotEqual(response.status_code, 403)

    def test_system_suspended_student_cannot_access(self):
        """Test that students cannot access system when suspended."""
        # Suspend system
        status = SystemStatus.get_status()
        status.is_active = False
        status.suspension_reason = "Test suspension"
        status.save()
        
        self.client.login(email='student@test.com', password='testpass123')
        
        # Student should get 403 on any non-admin page
        response = self.client.get(reverse('student_dashboard'))
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'System Temporarily Unavailable', response.content)

    def test_system_suspended_admin_can_access(self):
        """Test that admins can always access system."""
        # Suspend system
        status = SystemStatus.get_status()
        status.is_active = False
        status.suspension_reason = "Test suspension"
        status.save()
        
        self.client.login(email='admin@test.com', password='adminpass123')
        
        # Admin should access admin dashboard
        response = self.client.get(reverse('admin_dashboard'))
        self.assertNotEqual(response.status_code, 403)

    def test_system_suspended_admin_can_access_admin_panel(self):
        """Test that admins can access /admin/ when suspended."""
        # Suspend system
        status = SystemStatus.get_status()
        status.is_active = False
        status.save()
        
        self.client.login(email='admin@test.com', password='adminpass123')
        
        # Admin should access /admin/
        response = self.client.get('/admin/')
        self.assertNotEqual(response.status_code, 403)

    def test_login_always_accessible(self):
        """Test that login page is always accessible."""
        # Suspend system
        status = SystemStatus.get_status()
        status.is_active = False
        status.save()
        
        # Should be able to access student login
        response = self.client.get(reverse('student_login'))
        self.assertNotEqual(response.status_code, 403)

    def test_suspension_reason_displayed(self):
        """Test that suspension reason is displayed to user."""
        reason = "Scheduled maintenance until 3 PM EDT"
        
        # Suspend system with reason
        status = SystemStatus.get_status()
        status.is_active = False
        status.suspension_reason = reason
        status.save()
        
        self.client.login(email='student@test.com', password='testpass123')
        response = self.client.get(reverse('student_dashboard'))
        
        self.assertEqual(response.status_code, 403)
        self.assertIn(reason.encode(), response.content)


class SystemStatusAdminTests(TestCase):
    """Test SystemStatus admin interface."""

    def setUp(self):
        """Set up admin user."""
        self.admin = User.objects.create_superuser(
            email='admin@test.com',
            full_name='Admin User',
            password='adminpass123'
        )
        self.client = Client()

    def test_admin_can_toggle_system_status(self):
        """Test that admin can toggle system status from admin panel."""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        # Get admin change page
        status = SystemStatus.get_status()
        response = self.client.get(f'/admin/core/systemstatus/{status.pk}/change/')
        
        # Should be accessible
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'is_active', response.content)


class ElectionsListVotingTests(TestCase):
    """Ensure per-election voting availability is shown correctly."""

    def setUp(self):
        from django.utils import timezone
        from datetime import timedelta
        from core.models import Election, Position, Candidate, Vote

        self.client = Client()
        User = get_user_model()
        # Create student user
        self.student = User.objects.create_user(
            email='voter@test.com',
            admission_number='VOTE/00001/24S',
            full_name='Voter One',
            programme='DICT',
            year_of_study=2,
            is_student=True,
            password='votepass123'
        )
        self.student.password_changed = True
        self.student.save()

        # Create two elections each with one position and candidate
        now = timezone.now()
        self.election1 = Election.objects.create(title='Election One', description='First', start_datetime=now, end_datetime=now + timedelta(hours=1), status='active')
        self.election2 = Election.objects.create(title='Election Two', description='Second', start_datetime=now, end_datetime=now + timedelta(hours=1), status='active')

        self.pos1 = Position.objects.create(title='President', election=self.election1, order=1)
        self.pos2 = Position.objects.create(title='President', election=self.election2, order=1)

        # Create candidate user accounts and candidate records
        self.candidate_user1 = User.objects.create_user(
            email='alice@test.com',
            admission_number='CAND/00001/24S',
            full_name='Alice',
            is_student=True,
            password='candidate1'
        )
        self.candidate_user2 = User.objects.create_user(
            email='bob@test.com',
            admission_number='CAND/00002/24S',
            full_name='Bob',
            is_student=True,
            password='candidate2'
        )

        self.cand1 = Candidate.objects.create(full_name='Alice', position=self.pos1, user=self.candidate_user1, approved=True)
        self.cand2 = Candidate.objects.create(full_name='Bob', position=self.pos2, user=self.candidate_user2, approved=True)

        # Cast vote for election1
        Vote.objects.create(candidate=self.cand1, position=self.pos1, voter_id=str(self.student.id))

    def test_elections_list_shows_correct_buttons(self):
        # Login as student
        self.client.login(email='voter@test.com', password='votepass123')

        response = self.client.get(reverse('elections_list'))
        content = response.content.decode()

        # Election One: Already Voted
        self.assertIn('Election One', content)
        self.assertIn('Already Voted', content)

        # Election Two: Vote Now
        self.assertIn('Election Two', content)
        self.assertIn('Vote Now', content)
