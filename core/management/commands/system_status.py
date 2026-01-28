from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import SystemStatus


class Command(BaseCommand):
    help = 'Manage system access status. Enable or suspend access instantly.'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            type=str,
            choices=['enable', 'suspend'],
            help='Action to perform: "enable" to activate system, "suspend" to deactivate'
        )
        parser.add_argument(
            '--reason',
            type=str,
            default='',
            help='Optional suspension reason (only used with suspend action)'
        )

    def handle(self, *args, **options):
        action = options['action']
        reason = options.get('reason', '')

        system_status = SystemStatus.get_status()

        if action == 'enable':
            system_status.is_active = True
            system_status.suspension_reason = ''
            system_status.save()
            self.stdout.write(
                self.style.SUCCESS('✅ System ENABLED - All users can access the system')
            )
        
        elif action == 'suspend':
            system_status.is_active = False
            system_status.suspension_reason = reason or 'The system is temporarily unavailable.'
            system_status.save()
            self.stdout.write(
                self.style.WARNING('🔒 System SUSPENDED - Non-admin users cannot access the system')
            )
            if reason:
                self.stdout.write(f'   Reason: {reason}')

        self.stdout.write(f'   Updated at: {system_status.updated_at}')
        self.stdout.write(f'   Admins can still access /admin/ at all times')
