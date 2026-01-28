from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Root
    path('', views.index, name='index'),
    
    # Authentication
    path('login/admin/', views.admin_login, name='admin_login'),
    path('login/student/', views.student_login, name='student_login'),
    path('change-password/', views.change_password_first, name='change_password_first'),
    path('student/change-password/', views.change_password, name='change_password'),
    path('logout/', auth_views.LogoutView.as_view(next_page='student_login'), name='logout'),
    
    # Dashboards
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    
    # Student Upload
    path('admin/students/upload/', views.upload_students, name='upload_students'),
    path('admin/students/upload/progress/', views.get_upload_progress, name='get_upload_progress'),
    path('admin/students/credentials/', views.student_credentials, name='student_credentials'),
    path('admin/students/credentials/download/', views.download_student_credentials, name='download_student_credentials'),
    
    # Elections
    path('admin/elections/', views.election_list, name='election_list'),
    path('admin/elections/create/', views.election_create, name='election_create'),
    path('admin/elections/<int:pk>/', views.election_detail, name='election_detail'),
    path('admin/elections/<int:pk>/edit/', views.election_update, name='election_update'),
    path('admin/elections/<int:pk>/delete/', views.election_delete, name='election_delete'),
    
    # Positions
    path('admin/elections/<int:election_pk>/positions/create/', views.position_create, name='position_create'),
    path('admin/positions/<int:pk>/edit/', views.position_update, name='position_update'),
    path('admin/positions/<int:pk>/delete/', views.position_delete, name='position_delete'),
    
    # Candidates
    path('admin/positions/<int:position_pk>/candidates/create/', views.candidate_create, name='candidate_create'),
    path('admin/candidates/<int:pk>/edit/', views.candidate_update, name='candidate_update'),
    path('admin/candidates/<int:pk>/delete/', views.candidate_delete, name='candidate_delete'),
    
    # Student Voting
    path('student/elections/', views.elections_list, name='elections_list'),
    path('student/elections/<int:election_pk>/vote/', views.vote, name='vote'),
    path('student/elections/<int:election_pk>/results/', views.election_results, name='election_results'),
    
    # About
    path('about/', views.about, name='about'),
    
    # Student Profile
    path('student/profile/', views.student_profile, name='student_profile'),
    path('student/profile/edit/', views.student_profile_edit, name='student_profile_edit'),
    path('student/profile/change-password/', views.student_change_password, name='student_change_password'),
    
    # Admin Profile
    path('admin/profile/', views.admin_profile, name='admin_profile'),
    path('admin/profile/edit/', views.admin_profile_edit, name='admin_profile_edit'),
    path('admin/profile/change-password/', views.admin_change_password, name='admin_change_password'),
    path('admin/activity-log/', views.activity_log, name='activity_log'),
    
    # Audit Logs
    path('admin/audit-logs/', views.audit_logs, name='audit_logs'),
    path('admin/audit-logs/export/', views.audit_logs_export, name='audit_logs_export'),
    
    # Results
    path('admin/results/', views.election_results_admin, name='election_results_admin'),
    path('admin/results/<int:election_pk>/export-csv/', views.election_results_export_csv, name='election_results_export_csv'),
]