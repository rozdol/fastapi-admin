import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import secrets
import string


class EmailService:
    def __init__(self):
        self.smtp_server = getattr(settings, 'SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_username = getattr(settings, 'SMTP_USERNAME', '')
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', '')
        self.from_email = getattr(settings, 'FROM_EMAIL', 'noreply@fastapiadmin.com')

    def generate_activation_token(self, length=32):
        """Generate a secure random activation token"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def send_activation_email(self, user_email: str, username: str, activation_token: str):
        """Send activation email to new user"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = user_email
            msg['Subject'] = "Activate Your Account - FastAPI Admin"

            # Create activation URL
            base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
            activation_url = f"{base_url}/activate/{activation_token}"

            # Email body
            body = f"""
            <html>
            <body>
                <h2>Welcome to FastAPI Admin!</h2>
                <p>Hello {username},</p>
                <p>Thank you for registering with FastAPI Admin. To complete your registration, please click the link below to activate your account:</p>
                <p><a href="{activation_url}" style="background-color: #3B82F6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">Activate Account</a></p>
                <p>Or copy and paste this URL into your browser:</p>
                <p>{activation_url}</p>
                <p>This link will expire in 24 hours.</p>
                <p>If you didn't create this account, please ignore this email.</p>
                <br>
                <p>Best regards,<br>FastAPI Admin Team</p>
            </body>
            </html>
            """

            msg.attach(MIMEText(body, 'html'))

            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            text = msg.as_string()
            server.sendmail(self.from_email, user_email, text)
            server.quit()

            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def send_welcome_email(self, user_email: str, username: str):
        """Send welcome email after successful activation"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = user_email
            msg['Subject'] = "Account Activated - Welcome to FastAPI Admin!"

            base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
            body = f"""
            <html>
            <body>
                <h2>Welcome to FastAPI Admin!</h2>
                <p>Hello {username},</p>
                <p>Your account has been successfully activated. You can now log in to your account.</p>
                <p><a href="{base_url}/login" style="background-color: #3B82F6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">Login Now</a></p>
                <br>
                <p>Best regards,<br>FastAPI Admin Team</p>
            </body>
            </html>
            """

            msg.attach(MIMEText(body, 'html'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            text = msg.as_string()
            server.sendmail(self.from_email, user_email, text)
            server.quit()

            return True
        except Exception as e:
            print(f"Error sending welcome email: {e}")
            return False
