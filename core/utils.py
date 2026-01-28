import csv
import re
from io import StringIO, BytesIO
import openpyxl
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
import secrets
import string

User = get_user_model()
ADMISSION_REGEX = r'^[A-Z]+/\d{5}/\d{2}[A-Z]$'


class StudentBulkUploadValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.valid_rows = []
    
    def validate_file(self, file_obj):
        """Validate file type and read content."""
        filename = file_obj.name.lower()
        
        if filename.endswith('.csv'):
            return self._parse_csv(file_obj)
        elif filename.endswith('.xlsx'):
            return self._parse_excel(file_obj)
        else:
            raise ValidationError("File must be CSV or Excel (.xlsx) format")
    
    def _parse_csv(self, file_obj):
        """Parse CSV file."""
        try:
            # Reset file pointer to beginning if needed
            file_obj.seek(0)
            
            try:
                file_content = file_obj.read().decode('utf-8')
            except UnicodeDecodeError:
                # Try with latin-1 encoding if UTF-8 fails
                file_obj.seek(0)
                file_content = file_obj.read().decode('latin-1')
            
            if not file_content.strip():
                raise ValidationError("File is empty. Please provide a CSV file with student data.")
            
            reader = csv.DictReader(StringIO(file_content))
            rows = list(reader)
            
            # Check if rows were actually read
            if not rows:
                raise ValidationError("File has no data rows. Please ensure the CSV contains student records with headers in the first row. Got headers but no data rows.")
            
            # Filter out completely empty rows
            rows = [row for row in rows if any(str(v).strip() for v in row.values())]
            
            if not rows:
                raise ValidationError("File has no valid data rows. All rows appear to be empty. Please ensure the CSV contains student records.")
            
            return self._validate_rows(rows)
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error reading CSV file: {str(e)}")
    
    def _parse_excel(self, file_obj):
        """Parse Excel file."""
        try:
            workbook = openpyxl.load_workbook(BytesIO(file_obj.read()))
            worksheet = workbook.active
            
            if not worksheet or worksheet.max_row <= 1:
                raise ValidationError("Excel file is empty or contains only headers. Please add student records.")
            
            # Get headers from first row
            headers = [cell.value for cell in worksheet[1]]
            if not any(headers):
                raise ValidationError("Excel file has no headers in the first row.")
            
            rows = []
            
            for row_idx, row in enumerate(worksheet.iter_rows(min_row=2, values_only=True), start=2):
                # Skip completely empty rows
                if not any(row):
                    continue
                row_dict = dict(zip(headers, row))
                rows.append((row_idx, row_dict))
            
            if not rows:
                raise ValidationError("Excel file has no data rows. Please ensure student records start from row 2.")
            
            return self._validate_rows(rows, is_excel=True)
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error reading Excel file: {str(e)}")
    
    def _validate_rows(self, rows, is_excel=False):
        """Validate each row and collect errors."""
        if not rows:
            raise ValidationError("File is empty or has no data rows. Please ensure your file contains student records with the following columns: admission_number, full_name, email, programme, year_of_study")
        
        required_fields = {'admission_number', 'full_name', 'email', 'programme', 'year_of_study'}
        
        # Check headers - for CSV, first row IS data (headers handled by DictReader), for Excel get from first tuple element
        if is_excel:
            first_row = rows[0][1]  # Excel: tuple of (row_num, row_data)
        else:
            first_row = rows[0]  # CSV: dict from DictReader
        
        headers = set(first_row.keys()) if isinstance(first_row, dict) else set(k for k in first_row.keys() if k)
        
        missing_fields = required_fields - headers
        if missing_fields:
            raise ValidationError(f"Missing required columns: {', '.join(sorted(missing_fields))}. Your file must include: {', '.join(sorted(required_fields))}")
        
        # Validate data rows
        admission_numbers = set()
        existing_students = set(User.objects.filter(is_student=True).values_list('admission_number', flat=True))
        
        # For CSV, enumerate from 2 (since DictReader already consumed headers)
        # For Excel, use the row_num provided in tuple
        start_idx = 1 if is_excel else 2
        for idx, row in enumerate(rows, start=start_idx):
            row_num = row[0] if is_excel else idx
            row_data = row[1] if is_excel else row
            
            errors = self._validate_row(row_data, row_num, admission_numbers, existing_students)
            if errors:
                self.errors.extend(errors)
            else:
                self.valid_rows.append(row_data)
            
            admission_numbers.add(row_data.get('admission_number', ''))
        
        if self.errors:
            error_message = "Validation errors found:\n" + "\n".join(self.errors[:10])  # Show first 10 errors
            if len(self.errors) > 10:
                error_message += f"\n... and {len(self.errors) - 10} more errors"
            raise ValidationError(error_message)
        
        if not self.valid_rows:
            raise ValidationError("No valid rows found in the file")
        
        return True
    
    def _validate_row(self, row, row_num, admission_numbers, existing_students):
        """Validate a single row."""
        errors = []
        
        admission = str(row.get('admission_number', '')).strip()
        full_name = str(row.get('full_name', '')).strip()
        email = str(row.get('email', '')).strip()
        programme = str(row.get('programme', '')).strip()
        year_of_study_str = str(row.get('year_of_study', '')).strip()
        
        # Check missing values
        if not admission:
            errors.append(f"Row {row_num}: Missing admission number")
        if not full_name:
            errors.append(f"Row {row_num}: Missing full name")
        if not email:
            errors.append(f"Row {row_num}: Missing email address")
        if not programme:
            errors.append(f"Row {row_num}: Missing programme")
        if not year_of_study_str:
            errors.append(f"Row {row_num}: Missing year of study")
        
        if errors:
            return errors
        
        # Validate admission format
        if not re.match(ADMISSION_REGEX, admission):
            errors.append(f"Row {row_num}: Invalid admission number format '{admission}' (expected PROGRAM/01542/24S)")
        
        # Validate email format
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append(f"Row {row_num}: Invalid email format '{email}'")
        
        # Validate year of study is a positive integer
        try:
            year_of_study = int(year_of_study_str)
            if year_of_study < 1:
                errors.append(f"Row {row_num}: Year of study must be a positive number, got '{year_of_study_str}'")
        except ValueError:
            errors.append(f"Row {row_num}: Year of study must be a valid number, got '{year_of_study_str}'")
        
        # Check for duplicates within file
        if admission in admission_numbers and admission != '':
            errors.append(f"Row {row_num}: Duplicate admission number '{admission}'")
        
        # Check if already exists in database
        if admission in existing_students:
            errors.append(f"Row {row_num}: Admission number '{admission}' already registered")
        
        return errors
    
    def get_errors(self):
        """Return all validation errors."""
        return self.errors
    
    def get_warnings(self):
        """Return all warnings."""
        return self.warnings


def generate_temporary_password():
    """Generate a temporary password."""
    chars = string.ascii_letters + string.digits + '!@#$%^&*'
    return ''.join(secrets.choice(chars) for _ in range(12))

def bulk_create_students(rows, progress_callback=None):
    """Create students from validated rows with optional progress callback."""
    created = []
    errors = []
    total = len(rows)
    
    for index, row in enumerate(rows):
        try:
            admission_number = str(row.get('admission_number')).strip()
            full_name = str(row.get('full_name')).strip()
            email = str(row.get('email')).strip()
            programme = str(row.get('programme')).strip()
            year_of_study = int(str(row.get('year_of_study')).strip())
            
            temp_password = generate_temporary_password()
            
            user = User.objects.create_user(
                admission_number=admission_number,
                full_name=full_name,
                email=email,
                programme=programme,
                year_of_study=year_of_study,
                is_student=True,
                password=temp_password
            )
            
            created.append({
                'user': user,
                'admission_number': admission_number,
                'email': email,
                'full_name': full_name,
                'programme': programme,
                'year_of_study': year_of_study,
                'temp_password': temp_password
            })
            
            # Call progress callback if provided
            if progress_callback and callable(progress_callback):
                progress = int((index + 1) / total * 100)
                progress_callback(progress, index + 1, total)
                
        except Exception as e:
            errors.append(f"Error creating student {row.get('admission_number')}: {str(e)}")
            # Still update progress on error
            if progress_callback and callable(progress_callback):
                progress = int((index + 1) / total * 100)
                progress_callback(progress, index + 1, total)
    
    return created, errors


# ==================== AUDIT LOGGING UTILITY ====================

def log_audit_event(request, action, description='', user=None):
    """
    Log an audit event to the AuditLog model.
    
    Args:
        request: Django request object (to capture IP and user agent)
        action: Action type from AuditLog.ACTION_CHOICES
        description: Optional description of the action
        user: User object (defaults to request.user if available)
    
    Returns:
        AuditLog instance created
    
    Examples:
        log_audit_event(request, 'login', 'Admin login successful')
        log_audit_event(request, 'vote_cast', f'Voted for {candidate.full_name}', request.user)
    """
    from .models import AuditLog
    
    # Get IP address from request
    ip_address = get_client_ip(request)
    
    # Get user agent
    user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]  # Truncate to reasonable size
    
    # Use provided user or request.user
    log_user = user or request.user if request.user.is_authenticated else None
    
    audit_log = AuditLog.objects.create(
        user=log_user,
        action=action,
        description=description[:500],  # Truncate description
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return audit_log


def get_client_ip(request):
    """
    Get client IP address from request, handling proxy headers.
    
    Args:
        request: Django request object
    
    Returns:
        Client IP address as string
    """
    # Check for IP behind proxy
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    return ip or 'Unknown'
