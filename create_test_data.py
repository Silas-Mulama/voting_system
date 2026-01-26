import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evoting_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Election, Position, Candidate

User = get_user_model()

# Create test students
students_data = [
    ('CS/00001/24A', 'Alice Johnson', 'Form 4A'),
    ('CS/00002/24A', 'Bob Smith', 'Form 4A'),
    ('CS/00003/24B', 'Carol White', 'Form 4B'),
    ('CS/00004/24B', 'David Brown', 'Form 4B'),
    ('CS/00005/24C', 'Eve Davis', 'Form 4C'),
]

for admission, name, form in students_data:
    if not User.objects.filter(admission_number=admission).exists():
        email_part = admission.lower().replace('/', '_')
        user = User.objects.create_user(
            email=email_part + '@student.local',
            admission_number=admission,
            full_name=name,
            class_form=form,
            password='Temp@12345',
            password_changed=True,
            is_student=True
        )
        print(f'Created student: {name} ({admission})')

print('\nStudent accounts created!')

# Create candidates for the existing election
election = Election.objects.first()
if election:
    positions = election.positions.all()
    
    candidates_data = {
        'President': [
            ('Alice Johnson', 'CS/00001/24A', 'Strong leader with great vision'),
            ('David Brown', 'CS/00004/24B', 'Experienced and dedicated'),
        ],
        'Vice President': [
            ('Bob Smith', 'CS/00002/24A', 'Great team player'),
            ('Carol White', 'CS/00003/24B', 'Supportive and organized'),
        ],
        'Secretary': [
            ('Eve Davis', 'CS/00005/24C', 'Excellent communicator'),
        ],
    }
    
    for position in positions:
        candidates = candidates_data.get(position.title, [])
        for name, admission, manifesto in candidates:
            try:
                student = User.objects.get(admission_number=admission)
                if not Candidate.objects.filter(position=position, user=student).exists():
                    candidate = Candidate.objects.create(
                        position=position,
                        user=student,
                        full_name=name,
                        manifesto=manifesto,
                        approved=True
                    )
                    print(f'Created candidate: {name} for {position.title}')
            except User.DoesNotExist:
                print(f'Student {admission} not found')

print('\nCandidate accounts created!')
