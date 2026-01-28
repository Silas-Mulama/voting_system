"""
Django management command to export approved chatbot training data to YAML format.

This command exports all answered BotQuestion objects into a YAML training file
that can be used to retrain the chatbot with admin-approved Q&A pairs.

Usage:
    python manage.py export_bot_training
"""

import os
import yaml
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from core.models import BotQuestion


class Command(BaseCommand):
    help = 'Export approved chatbot Q&A pairs into YAML training file'

    def handle(self, *args, **options):
        """Export approved BotQuestion objects to YAML file."""
        
        # Get all answered questions
        answered_questions = BotQuestion.objects.filter(is_answered=True).order_by('-updated_at')
        
        if not answered_questions.exists():
            self.stdout.write(
                self.style.WARNING('⚠️  No answered questions found. Nothing to export.')
            )
            return
        
        # Create training data structure
        conversations = []
        for q_obj in answered_questions:
            if q_obj.answer:  # Only include if answer is not empty
                conversations.append([
                    q_obj.question,
                    q_obj.answer
                ])
        
        if not conversations:
            self.stdout.write(
                self.style.WARNING('⚠️  No valid Q&A pairs (answers are empty). Nothing to export.')
            )
            return
        
        # Build YAML structure
        training_data = {
            'categories': ['dynamic_training'],
            'conversations': conversations
        }
        
        # Determine output path
        output_dir = os.path.join(settings.BASE_DIR, 'core', 'training_data')
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, 'dynamic_training.yml')
        
        try:
            # Write YAML file
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(training_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Successfully exported {len(conversations)} Q&A pairs!')
            )
            self.stdout.write(f'📁 File saved to: {output_file}')
            self.stdout.write(
                self.style.WARNING(
                    '\n⚠️  IMPORTANT: Restart your Django server for the chatbot to use the new training data.\n'
                    '   The chatbot loads training data at startup.'
                )
            )
            
        except Exception as e:
            raise CommandError(f'❌ Error writing training file: {str(e)}')
