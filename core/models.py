from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.utils import timezone
from django.db.models import Q
import uuid

ADMISSION_NUMBER_REGEX = r'^[A-Z]+/\d{5}/\d{2}[A-Z]$'  # e.g. DICT/01542/24S


class UserManager(BaseUserManager):
	use_in_migrations = True

	def _create_user(self, email, admission_number, full_name, programme, year_of_study, is_student, password=None, **extra_fields):
		if is_student:
			if not admission_number:
				raise ValueError('Students must have an admission number')
			if not full_name:
				raise ValueError('Students must have a full name')
		else:
			if not email:
				raise ValueError('Admins must have an email address')
			if not full_name:
				raise ValueError('Admins must have a full name')
		email = self.normalize_email(email) if email else None
		user = self.model(
			email=email,
			admission_number=admission_number,
			full_name=full_name,
			programme=programme,
			year_of_study=year_of_study,
			is_student=is_student,
			**extra_fields
		)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_user(self, email=None, admission_number=None, full_name=None, programme=None, year_of_study=None, password=None, **extra_fields):
		is_student = extra_fields.pop('is_student', False)
		extra_fields.setdefault('is_staff', False)
		extra_fields.setdefault('is_superuser', False)
		return self._create_user(email, admission_number, full_name, programme, year_of_study, is_student, password, **extra_fields)

	def create_superuser(self, email, full_name, password=None, **extra_fields):
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)
		if extra_fields.get('is_staff') is not True:
			raise ValueError('Superuser must have is_staff=True.')
		if extra_fields.get('is_superuser') is not True:
			raise ValueError('Superuser must have is_superuser=True.')
		return self._create_user(email, None, full_name, None, None, False, password, **extra_fields)


class User(AbstractUser):
	username = None  # Remove username field
	email = models.EmailField('email address', unique=True, null=True, blank=True)
	admission_number = models.CharField(
		max_length=20,
		unique=True,
		null=True,
		blank=True,
		validators=[
			RegexValidator(
				regex=ADMISSION_NUMBER_REGEX,
				message='Admission number must be in the format PROGRAM/01542/24S',
				code='invalid_admission_number'
			)
		]
	)
	full_name = models.CharField(max_length=255)
	programme = models.CharField(max_length=100, null=True, blank=True)
	year_of_study = models.PositiveIntegerField(null=True, blank=True)
	is_student = models.BooleanField(default=False)
	password_changed = models.BooleanField(default=False)  # Track first login password change
	profile_picture = models.ImageField(upload_to='profile_pictures/%Y/%m/%d/', null=True, blank=True)
	# is_staff is already present in AbstractUser for admin check

	objects = UserManager()

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['full_name']

	def __str__(self):
		return self.full_name or self.email or self.admission_number


# Election Model
class Election(models.Model):
	STATUS_CHOICES = [
		('draft', 'Draft'),
		('active', 'Active'),
		('closed', 'Closed'),
	]
	
	title = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	start_datetime = models.DateTimeField()
	end_datetime = models.DateTimeField()
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	class Meta:
		ordering = ['-created_at']
	
	def __str__(self):
		return self.title
	
	def is_active(self):
		now = timezone.now()
		return self.status == 'active' and self.start_datetime <= now < self.end_datetime
	
	def is_closed(self):
		now = timezone.now()
		if now >= self.end_datetime and self.status == 'active':
			self.status = 'closed'
			self.save()
			return True
		return self.status == 'closed'
	
	def save(self, *args, **kwargs):
		# Validate datetime
		if self.start_datetime >= self.end_datetime:
			raise ValueError('Start time must be before end time')
		
		# Only allow one active election
		if self.status == 'active':
			Election.objects.filter(status='active').exclude(pk=self.pk).update(status='closed')
		
		super().save(*args, **kwargs)


# Position Model
class Position(models.Model):
	election = models.ForeignKey(Election, on_delete=models.PROTECT, related_name='positions')
	title = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	order = models.PositiveIntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	
	class Meta:
		ordering = ['order', 'title']
		unique_together = ('election', 'title')
	
	def __str__(self):
		return f"{self.title} ({self.election.title})"
	
	def can_delete(self):
		# Cannot delete if there are votes for candidates in this position
		return not self.candidates.filter(votes__isnull=False).exists()


# Candidate Model
class Candidate(models.Model):
	position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='candidates',null=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='candidacies')
	full_name = models.CharField(max_length=255)
	photo = models.ImageField(upload_to='candidates/%Y/%m/%d/', null=True, blank=True)
	manifesto = models.TextField(blank=True)
	approved = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	
	class Meta:
		unique_together = ('position', 'user')
		ordering = ['full_name']
	
	def __str__(self):
		return f"{self.full_name} - {self.position.title}"
	
	def save(self, *args, **kwargs):
		# Ensure student can only be candidate once per election
		election = self.position.election
		existing = Candidate.objects.filter(
			user=self.user,
			position__election=election
		).exclude(pk=self.pk)
		if existing.exists():
			raise ValueError(f"Student {self.user} is already a candidate in this election")
		super().save(*args, **kwargs)


# Vote Model
class Vote(models.Model):
	candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='votes')
	position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='votes',null=True)
	voter_id = models.CharField(max_length=255)  # Anonymous voter ID
	timestamp = models.DateTimeField(auto_now_add=True)
	
	class Meta:
		unique_together = ('position', 'voter_id')
		indexes = [
			models.Index(fields=['voter_id', 'timestamp']),
		]
	
	def save(self, *args, **kwargs):
		# ✅ STRICT HIERARCHY ENFORCEMENT
		# Ensure position matches candidate's position (cascade from Candidate)
		if not self.position:
			self.position = self.candidate.position
		elif self.candidate.position != self.position:
			# Never allow mismatched positions - enforce hierarchy strictly
			raise ValueError(
				f'Vote position {self.position.id} does not match '
				f'candidate position {self.candidate.position.id}. '
				f'Hierarchy: Election -> Position -> Candidate -> Vote must be strictly maintained.'
			)
		
		# Verify candidate is approved for voting
		if not self.candidate.approved:
			raise ValueError(f'Cannot vote for unapproved candidate: {self.candidate.full_name}')
		
		super().save(*args, **kwargs)
	
	def __str__(self):
		return f"Vote for {self.candidate} by {self.voter_id}"


# Audit Log Model
class AuditLog(models.Model):
	ACTION_CHOICES = [
		('login', 'User Login'),
		('logout', 'User Logout'),
		('login_failed', 'Failed Login Attempt'),
		('password_change', 'Password Changed'),
		('student_upload', 'Bulk Student Upload'),
		('vote_cast', 'Vote Cast'),
		('election_created', 'Election Created'),
		('election_updated', 'Election Updated'),
		('election_closed', 'Election Closed'),
	]
	
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
	action = models.CharField(max_length=50, choices=ACTION_CHOICES)
	description = models.TextField(blank=True)
	ip_address = models.GenericIPAddressField(null=True, blank=True)
	user_agent = models.TextField(blank=True)
	timestamp = models.DateTimeField(auto_now_add=True)
	
	class Meta:
		ordering = ['-timestamp']
		indexes = [
			models.Index(fields=['-timestamp']),
			models.Index(fields=['user', '-timestamp']),
			models.Index(fields=['action', '-timestamp']),
		]
	
	def __str__(self):
		return f"{self.action} - {self.user} at {self.timestamp}"


class SystemStatus(models.Model):
	"""
	Manages the global system access status.
	When is_active=False, all non-admin access is blocked.
	"""
	is_active = models.BooleanField(default=True)
	suspension_reason = models.TextField(blank=True, null=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	class Meta:
		verbose_name = "System Status"
		verbose_name_plural = "System Status"
	
	def __str__(self):
		status = "Active" if self.is_active else "Suspended"
		return f"System Status: {status}"
	
	@classmethod
	def get_status(cls):
		"""Get or create the system status singleton."""
		obj, created = cls.objects.get_or_create(pk=1)
		return obj



