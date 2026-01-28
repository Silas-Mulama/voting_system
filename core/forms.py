from django import forms
from django.core.exceptions import ValidationError
from .models import Election, Position, Candidate
from .utils import StudentBulkUploadValidator


class StudentBulkUploadForm(forms.Form):
    file = forms.FileField(
        label='Upload CSV or Excel file',
<<<<<<< HEAD
        help_text='Accepted formats: CSV, Excel (.xlsx). Required columns: admission_number, full_name, email, programme, year_of_study'
=======
        help_text='Accepted formats: CSV, Excel (.xlsx). Required columns: admission_number, full_name, class_form'
>>>>>>> fda6d5ef726056f0c8eabf2946f19a342a16bf18
    )
    
    def clean_file(self):
        file_obj = self.cleaned_data.get('file')
        if not file_obj:
            raise ValidationError("File is required")
        
        # Validate file type
        filename = file_obj.name.lower()
        if not (filename.endswith('.csv') or filename.endswith('.xlsx')):
            raise ValidationError("File must be CSV or Excel (.xlsx) format")
        
        # Parse and validate
        validator = StudentBulkUploadValidator()
        try:
            validator.validate_file(file_obj)
        except ValidationError as e:
            raise ValidationError(f"File validation failed: {e.message}")
        
        errors = validator.get_errors()
        if errors:
            error_msg = "File contains errors:\n" + "\n".join(errors[:10])
            if len(errors) > 10:
                error_msg += f"\n... and {len(errors) - 10} more errors"
            raise ValidationError(error_msg)
        
        return file_obj


class ElectionForm(forms.ModelForm):
    class Meta:
        model = Election
        fields = ['title', 'description', 'start_datetime', 'end_datetime', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Election title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Election description'}),
            'start_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_datetime')
        end = cleaned_data.get('end_datetime')
        status = cleaned_data.get('status')
        
        if start and end and start >= end:
            raise ValidationError("Start time must be before end time")
        
        # Only allow one active election
        if status == 'active':
            existing_active = Election.objects.filter(status='active').exclude(pk=self.instance.pk)
            if existing_active.exists():
                raise ValidationError("Only one active election is allowed at a time")
        
        return cleaned_data


class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['title', 'description', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Position title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['full_name', 'photo', 'manifesto', 'approved']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'manifesto': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'approved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class VoteForm(forms.Form):
    """Dynamic form for voting - created programmatically per election."""
    pass
