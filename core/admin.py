from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Election, Position, Candidate, Vote, AuditLog, SystemStatus, BotQuestion


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'admission_number', 'programme', 'year_of_study')}),
        ('Permissions', {'fields': ('is_student', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Password', {'fields': ('password_changed',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'admission_number', 'password1', 'password2', 'is_student'),
        }),
    )
    list_display = ('email', 'full_name', 'admission_number', 'is_student', 'is_staff', 'date_joined')
    list_filter = ('is_student', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'full_name', 'admission_number')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions')


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'start_datetime', 'end_datetime', 'created_at')
    list_filter = ('status', 'created_at', 'start_datetime')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Election Info', {'fields': ('title', 'description', 'status')}),
        ('Timing', {'fields': ('start_datetime', 'end_datetime')}),
        ('Metadata', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'election', 'order', 'candidate_count')
    list_filter = ('election', 'order')
    search_fields = ('title', 'election__title')
    readonly_fields = ('created_at',)
    
    def candidate_count(self, obj):
        return obj.candidates.count()
    candidate_count.short_description = 'Candidates'


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'position', 'user', 'approved', 'vote_count')
    list_filter = ('approved', 'position__election', 'position')
    search_fields = ('full_name', 'user__email', 'user__admission_number')
    readonly_fields = ('photo_preview', 'vote_count')
    fieldsets = (
        ('Candidate Info', {'fields': ('user', 'full_name', 'position', 'manifesto')}),
        ('Media', {'fields': ('photo', 'photo_preview')}),
        ('Status', {'fields': ('approved',)}),
        ('Stats', {'fields': ('vote_count',), 'classes': ('collapse',)}),
    )
    
    def photo_preview(self, obj):
        if obj.photo:
            from django.utils.html import format_html
            return format_html('<img src="{}" width="100" height="100" />', obj.photo.url)
        return 'No photo'
    photo_preview.short_description = 'Photo Preview'
    
    def vote_count(self, obj):
        return obj.votes.count()
    vote_count.short_description = 'Total Votes'


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'position', 'voter_id', 'timestamp')
    list_filter = ('timestamp', 'candidate__position__election')
    search_fields = ('candidate__full_name', 'position__title')
    readonly_fields = ('voter_id', 'timestamp', 'position')
    
    def has_add_permission(self, request):
        """Prevent manual vote creation from admin"""
        return False
    
    # def has_delete_permission(self, request, obj=None):
    #     """Prevent vote deletion from admin"""
    #     return False


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'ip_address', 'description_short')
    list_filter = ('action', 'timestamp', 'user__is_student')
    search_fields = ('user__email', 'user__full_name', 'description', 'ip_address')
    readonly_fields = ('timestamp', 'user', 'action', 'description', 'ip_address', 'user_agent')
    
    
    def description_short(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'
    
    def has_add_permission(self, request):
        """Prevent manual audit log creation"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent audit log deletion"""
        return False


@admin.register(SystemStatus)
class SystemStatusAdmin(admin.ModelAdmin):
    list_display = ('get_status_display', 'updated_at')
    fieldsets = (
        ('System Status', {
            'fields': ('is_active',),
            'description': 'Enable or disable access to the system for non-admin users. Admins can always access the system.'
        }),
        ('Suspension Details', {
            'fields': ('suspension_reason',),
            'description': 'Optional message displayed to users when the system is suspended.'
        }),
        ('Metadata', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('updated_at',)
    
    def get_status_display(self, obj):
        if obj.is_active:
            return '✅ Active - System Operational'
        else:
            return '🔒 Suspended - Access Restricted'
    get_status_display.short_description = 'System Status'
    
    def has_add_permission(self, request):
        """Allow adding system status (though only one should exist)"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of system status"""
        return False


@admin.register(BotQuestion)
class BotQuestionAdmin(admin.ModelAdmin):
    list_display = ('status_icon', 'question_short', 'is_answered', 'created_at')
    list_filter = ('is_answered', 'created_at')
    search_fields = ('question', 'answer')
    readonly_fields = ('question', 'created_at', 'updated_at')
    fieldsets = (
        ('Question', {
            'fields': ('question',),
            'description': 'User question that the bot could not answer with high confidence.'
        }),
        ('Answer', {
            'fields': ('answer', 'is_answered'),
            'description': 'Provide the answer you want the bot to learn. Mark as answered when complete.'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_icon(self, obj):
        if obj.is_answered:
            return '✅ Answered'
        else:
            return '⏳ Pending'
    status_icon.short_description = 'Status'
    
    def question_short(self, obj):
        return obj.question[:60] + '...' if len(obj.question) > 60 else obj.question
    question_short.short_description = 'Question'
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion of questions if needed"""
        return True
    
    actions = ['mark_as_answered']
    
    def mark_as_answered(self, request, queryset):
        """Quick action to mark selected questions as answered"""
        updated = queryset.filter(is_answered=False).update(is_answered=True)
        self.message_user(request, f'{updated} questions marked as pending answer.')
    mark_as_answered.short_description = "Mark selected as answered (after filling answers)"

