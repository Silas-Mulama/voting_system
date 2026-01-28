import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evoting_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Election, Position, Candidate

User = get_user_model()

# Create test students
students_data = [
    ('DICT/00001/24S', 'Alice Johnson', 'DICT', 1),
    ('DICT/00002/24S', 'Bob Smith', 'DICT', 1),
    ('BIT/00003/24S', 'Carol White', 'BIT', 2),
    ('BIT/00004/24S', 'David Brown', 'BIT', 2),
    ('DATA/00005/24S', 'Eve Davis', 'DATA ANALYTICS', 1),
]

for admission, name, programme, year in students_data:
    if not User.objects.filter(admission_number=admission).exists():
        email_part = admission.lower().replace('/', '_')
        user = User.objects.create_user(
            email=email_part + '@buteretti.ac.ke',
            admission_number=admission,
            full_name=name,
            programme=programme,
            year_of_study=year,
            password='Temp@12345',
            password_changed=True,
            is_student=True
        )
        print(f'Created student: {name} ({admission}) - {programme}, Year {year}')

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
