"""
Simple Rule-Based Chatbot for the Voting System
This chatbot handles common questions about elections, voting, and the system.
It supports dynamic training through admin-approved Q&A pairs loaded from YAML.
"""

import os
import yaml
from django.conf import settings


def load_dynamic_training_data():
    """
    Load admin-approved training data from YAML file.
    Returns a dictionary of {question: answer} pairs.
    """
    training_file = os.path.join(settings.BASE_DIR, 'core', 'training_data', 'dynamic_training.yml')
    
    if not os.path.exists(training_file):
        return {}
    
    try:
        with open(training_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        if not data or 'conversations' not in data:
            return {}
        
        # Convert conversations list to dict
        # conversations = [['Q1', 'A1'], ['Q2', 'A2'], ...]
        training_dict = {}
        for conversation in data.get('conversations', []):
            if isinstance(conversation, list) and len(conversation) >= 2:
                question = conversation[0].lower().strip()
                answer = conversation[1]
                training_dict[question] = answer
        
        return training_dict
    except Exception as e:
        print(f"Warning: Could not load dynamic training data: {e}")
        return {}


class VotingChatbot:
    """Rule-based chatbot for answering voting system questions."""
    
    def __init__(self):
        """Initialize the chatbot with predefined responses."""
        self.name = "VotingAssistant"
        self.confidence_threshold = 0.60  # 60% confidence minimum
        
        # Base static responses (always available)
        self.base_responses = {
            # Voting questions
            'how to vote': 'To vote, log in to your student account, go to the Elections page, select an active election, and click "Vote" for each position. Your vote is confidential and secure.',
            'can i change my vote': 'No, once you submit a vote, it cannot be changed. Please review all candidates carefully before voting.',
            'voting deadline': 'Check the election detail page to see the voting deadline. Elections close at the specified end time.',
            'password reset': 'Contact your administrator to reset your password. For security, passwords cannot be reset via the chatbot.',
            'multiple votes': 'Each student can vote only once per election per position. Multiple votes are prevented by the system.',
            
            # Election questions
            'what is an election': 'An election is a voting process where students elect candidates for various positions. Elections are created and managed by administrators.',
            'election status': 'Elections can be in "Draft", "Active", or "Closed" status. Only Active elections accept votes.',
            'when does voting start': 'Check the election detail page for the start and end times. Your administrator determines these dates.',
            'candidates': 'Candidates are students approved by administrators to run for positions. You can see all approved candidates when voting.',
            
            # System questions
            'who can vote': 'All registered students can vote in active elections. You need a valid student account to access the voting system.',
            'is my vote private': 'Yes, all votes are completely confidential. The system records votes without associating them with student names.',
            'how are results calculated': 'Results are tallied automatically once an election closes. The candidate with the most votes wins each position.',
            'audit logs': 'Administrators can view audit logs to track all system activities for security and transparency.',
            
            # Help questions
            'help': 'I can answer questions about voting, elections, candidates, and system features. What would you like to know?',
            'hello': 'Hello! I\'m the VotingAssistant. I\'m here to help with questions about elections, voting, and the system. What would you like to know?',
            'hi': 'Hello! I\'m the VotingAssistant. I\'m here to help with questions about elections, voting, and the system. What would you like to know?',
            'contact admin': 'For account issues, system problems, or special requests, contact your election administrator.',
        }
        
        # Load dynamically trained responses (admin-approved Q&A)
        self.dynamic_responses = load_dynamic_training_data()
        
        # Combine both - dynamic responses take precedence for matching questions
        self.responses = {**self.base_responses, **self.dynamic_responses}
    
    def get_response(self, user_input):
        """
        Get a response based on user input with confidence score.
        
        Args:
            user_input (str): The user's question or message
            
        Returns:
            dict: {'response': str, 'confidence': float (0.0-1.0)}
        """
        if not user_input or not isinstance(user_input, str):
            return {
                'response': "I didn't understand that. Please ask a question about voting, elections, or the system.",
                'confidence': 0.0
            }
        
        # Normalize input - lowercase and strip whitespace
        normalized = user_input.lower().strip()
        
        # Try exact matches first (highest confidence)
        for keyword, response in self.responses.items():
            if normalized == keyword:
                return {'response': response, 'confidence': 1.0}
        
        # Try partial matches - check if any keyword is contained in the user input
        for keyword, response in self.responses.items():
            if keyword in normalized:
                return {'response': response, 'confidence': 0.85}
        
        # Default response if no match found (low confidence)
        default_response = (
            "I'm not sure about that. I can help with questions about:\n"
            "• How to vote\n"
            "• Election status and dates\n"
            "• Voting privacy and security\n"
            "• Candidate information\n"
            "• System features\n\n"
            "Type 'help' for more options or contact your administrator for specific issues."
        )
        return {'response': default_response, 'confidence': 0.0}


# Initialize the chatbot instances
voting_bot = VotingChatbot()


class AdminChatbot:
    """Rule-based chatbot for helping administrators use the voting system."""
    
    def __init__(self):
        """Initialize the admin chatbot with admin-specific FAQs."""
        self.name = "AdminAssistant"
        self.confidence_threshold = 0.60  # 60% confidence minimum
        
        # Base static admin FAQs
        self.base_responses = {
            # Core administration tasks
            'how do i create a new election': 'Go to the Admin Dashboard → Elections → Add Election. Fill in the name, start and end dates, and save.',
            'create election': 'Go to the Admin Dashboard → Elections → Add Election. Fill in the name, start and end dates, and save.',
            'how do i add positions to an election': 'In the election details page, click \'Add Position\' and specify the position name (e.g., President, Secretary).',
            'add positions': 'In the election details page, click \'Add Position\' and specify the position name (e.g., President, Secretary).',
            'how do i add candidates': 'Click on the position you want, then \'Add Candidate\'. Enter the candidate\'s full name, select the student, upload a photo, and add their manifesto.',
            'add candidates': 'Click on the position you want, then \'Add Candidate\'. Enter the candidate\'s full name, select the student, upload a photo, and add their manifesto.',
            
            # Student management
            'how do i upload students': 'Go to Admin Dashboard → Students → Upload. You can upload CSV or Excel files containing student details.',
            'upload students': 'Go to Admin Dashboard → Students → Upload. You can upload CSV or Excel files containing student details.',
            'can i upload pdfs for student data': 'No, only CSV or Excel files are accepted for uploading students.',
            'student upload format': 'Only CSV or Excel files are accepted. Download the template from the upload page for the correct format.',
            'how do i reset a student\'s password': 'Go to Admin Dashboard → Students → Select Student → Reset Password. Enter a new password and save.',
            'reset password': 'Go to Admin Dashboard → Students → Select Student → Reset Password. Enter a new password and save.',
            
            # Monitoring and reporting
            'how do i view audit logs': 'Go to Admin Dashboard → Audit Logs to see a history of actions performed in the system.',
            'view audit logs': 'Go to Admin Dashboard → Audit Logs to see a history of actions performed in the system.',
            'audit logs': 'Go to Admin Dashboard → Audit Logs to see a history of actions performed in the system.',
            'how do i check election results': 'Navigate to Admin Dashboard → Elections → Select Election → Results. You can see the winners for each position.',
            'check results': 'Navigate to Admin Dashboard → Elections → Select Election → Results. You can see the winners for each position.',
            'election results': 'Navigate to Admin Dashboard → Elections → Select Election → Results. You can see the winners for each position.',
            
            # System management
            'can i delete a candidate or election': 'Yes, but be careful. Deleting will remove all related votes. Use the delete button in the election or candidate view.',
            'delete candidate': 'Yes, but be careful. Deleting will remove all related votes. Use the delete button in the election or candidate view.',
            'delete election': 'Yes, but be careful. Deleting will remove all related votes. Use the delete button in the election or candidate view.',
            'how do i suspend the system': 'In Admin Dashboard → System → Suspend. This temporarily disables voting until resumed.',
            'suspend system': 'In Admin Dashboard → System → Suspend. This temporarily disables voting until resumed.',
            'how do i unlock the system': 'Go to Admin Dashboard → System → Unlock. Voting will resume once unlocked.',
            'unlock system': 'Go to Admin Dashboard → System → Unlock. Voting will resume once unlocked.',
            
            # Support
            'how do i contact support': 'Reach out to the technical team via email or your designated system administrator.',
            'contact support': 'Reach out to the technical team via email or your designated system administrator.',
            
            # Help & Navigation
            'help': 'I can help with: creating elections, adding positions & candidates, uploading students, checking results, viewing audit logs, and system management. What do you need?',
            'hello': 'Hello Admin! I\'m the Admin Assistant. I\'m here to help you manage elections, students, and system operations. What do you need?',
            'hi': 'Hello Admin! I\'m the Admin Assistant. I\'m here to help you manage elections, students, and system operations. What do you need?',
            'quick start': 'Quick start: 1) Upload students 2) Create election 3) Add positions 4) Add & approve candidates 5) Activate election 6) Monitor results.',
            'features': 'Key features: Create & manage elections, Add positions & candidates, Upload students, Track voting results, View audit logs, System settings.',
            
            # Dashboard navigation
            'admin dashboard': 'The Admin Dashboard shows key metrics: active elections, total votes cast, participation rate, and quick navigation to major features.',
            'dashboard': 'The Admin Dashboard shows key metrics: active elections, total votes cast, participation rate, and quick navigation to major features.',
        }
        
        # Load dynamically trained responses
        self.dynamic_responses = load_dynamic_training_data()
        
        # Combine both - dynamic responses take precedence
        self.responses = {**self.base_responses, **self.dynamic_responses}
    
    def get_response(self, user_input):
        """
        Get a response based on admin's question with confidence score.
        
        Args:
            user_input (str): The admin's question or message
            
        Returns:
            dict: {'response': str, 'confidence': float (0.0-1.0)}
        """
        if not user_input or not isinstance(user_input, str):
            return {
                'response': "I didn't understand that. Please ask about admin features like elections, students, results, or security.",
                'confidence': 0.0
            }
        
        # Normalize input
        normalized = user_input.lower().strip()
        
        # Try exact matches first (highest confidence)
        for keyword, response in self.responses.items():
            if normalized == keyword:
                return {'response': response, 'confidence': 1.0}
        
        # Try partial matches
        for keyword, response in self.responses.items():
            if keyword in normalized:
                return {'response': response, 'confidence': 0.85}
        
        # Default response
        default_response = (
            "I'm not sure about that. I can help with:\n"
            "• Creating and managing elections\n"
            "• Adding positions and candidates\n"
            "• Uploading and managing students\n"
            "• Viewing election results\n"
            "• Accessing audit logs\n"
            "• System security and settings\n\n"
            "Type 'help' for more or 'quick start' for getting started."
        )
        return {'response': default_response, 'confidence': 0.0}


# Initialize both chatbot instances
admin_bot = AdminChatbot()

