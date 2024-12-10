import os
import openai
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# OpenAI API Key
openai.api_key = ""

# Gmail API Scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate_gmail():
    """Authenticate with Gmail API and return the service."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def generate_email_content(prompt):
    """Generate email content using OpenAI API."""
    try:
        response = openai.openai.chat.completions.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )
        return response.model_dump()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Error generating email content: {e}")
        return None

def create_email(sender, to, subject, body_text):
    """Create an email message."""
    message = MIMEText(body_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_email(service, sender, to, subject, body_text):
    """Send an email via Gmail API."""
    email = create_email(sender, to, subject, body_text)
    try:
        service.users().messages().send(userId="me", body=email).execute()
        print("Email sent successfully!")
    except Exception as e:
        print(f"An error occurred while sending the email: {e}")

if __name__ == '__main__':
    # Authenticate Gmail API
    gmail_service = authenticate_gmail()
    
    # User input for email generation
    print("Enter the prompt to generate the email content:")
    user_prompt = input("> ")
    email_body = generate_email_content(user_prompt)
    
    if email_body:
        print("\nGenerated Email Content:")
        print(email_body)
        
        # Send the email
        sender_email = ""
        recipient_email = ""
        subject = "Generated Email from ChatGPT"
        
        send_email(gmail_service, sender_email, recipient_email, subject, email_body)
    else:
        print("Failed to generate email content.")
