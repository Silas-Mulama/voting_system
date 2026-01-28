from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin
from .models import SystemStatus


class SystemAccessLockMiddleware(MiddlewareMixin):
	"""
	Middleware that enforces system access locks.
	When SystemStatus.is_active=False, blocks access to all non-admin pages.
	Always allows access to /admin/ paths.
	"""
	
	# URLs that should always be accessible
	ALWAYS_ALLOWED_PATHS = [
		'/admin/',
		'/login/',
		'/logout/',
	]
	
	def process_request(self, request):
		"""Check system status before processing request."""
		# Always allow admin paths
		if any(request.path.startswith(path) for path in self.ALWAYS_ALLOWED_PATHS):
			return None
		
		# Check system status
		system_status = SystemStatus.get_status()
		
		# If system is active, allow access
		if system_status.is_active:
			return None
		
		# If user is not authenticated, allow them to proceed to login
		if not request.user.is_authenticated:
			return None
		
		# If user is admin, always allow access
		if request.user.is_staff or request.user.is_superuser:
			return None
		
		# System is suspended and user is not admin - block access
		return render(
			request,
			'core/system_suspended.html',
			{
				'suspension_reason': system_status.suspension_reason,
			},
			status=403
		)
