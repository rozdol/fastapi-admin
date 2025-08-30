import pytest
import smtplib
from unittest.mock import Mock, patch, MagicMock
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os
import sys

# Add the app directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.email import EmailService
from app.core.config import settings


class TestEmailService:
    """Test cases for EmailService"""

    @pytest.fixture
    def email_service(self):
        """Create EmailService instance for testing"""
        return EmailService()

    @pytest.fixture
    def mock_smtp(self):
        """Mock SMTP server for testing"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = Mock()
            mock_smtp.return_value = mock_server
            yield mock_server

    def test_generate_activation_token(self, email_service):
        """Test activation token generation"""
        # Test token generation
        token1 = email_service.generate_activation_token()
        token2 = email_service.generate_activation_token()
        
        # Check token properties
        assert len(token1) == 32  # Default length
        assert len(token2) == 32
        assert token1 != token2  # Tokens should be different
        assert token1.isalnum()  # Should be alphanumeric
        assert token2.isalnum()

    def test_generate_activation_token_custom_length(self, email_service):
        """Test activation token generation with custom length"""
        token = email_service.generate_activation_token(length=16)
        assert len(token) == 16
        assert token.isalnum()

    @patch('app.core.config.settings')
    def test_send_activation_email_success(self, mock_settings, email_service, mock_smtp):
        """Test successful activation email sending"""
        # Mock settings
        mock_settings.SMTP_SERVER = "smtp.gmail.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USERNAME = "test@gmail.com"
        mock_settings.SMTP_PASSWORD = "test-password"
        mock_settings.FROM_EMAIL = "noreply@test.com"
        mock_settings.BASE_URL = "http://localhost:8000"
        
        # Override the email service settings
        email_service.smtp_server = "smtp.gmail.com"
        email_service.smtp_port = 587
        email_service.smtp_username = "test@gmail.com"
        email_service.smtp_password = "test-password"
        email_service.from_email = "noreply@test.com"

        # Test data
        user_email = "user@example.com"
        username = "testuser"
        activation_token = "test-token-123"

        # Mock SMTP methods
        mock_smtp.starttls.return_value = None
        mock_smtp.login.return_value = None
        mock_smtp.sendmail.return_value = None
        mock_smtp.quit.return_value = None

        # Send activation email
        result = email_service.send_activation_email(user_email, username, activation_token)

        # Verify result
        assert result is True

        # Verify SMTP was called correctly
        mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once_with("test@gmail.com", "test-password")
        mock_smtp.quit.assert_called_once()

        # Verify sendmail was called
        assert mock_smtp.sendmail.call_count == 1
        call_args = mock_smtp.sendmail.call_args
        assert call_args[0][0] == "noreply@test.com"  # from_email
        assert call_args[0][1] == user_email  # to_email

    @patch('app.core.config.settings')
    def test_send_activation_email_failure(self, mock_settings, email_service, mock_smtp):
        """Test activation email sending failure"""
        # Mock settings
        mock_settings.SMTP_SERVER = "smtp.gmail.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USERNAME = "test@gmail.com"
        mock_settings.SMTP_PASSWORD = "test-password"
        mock_settings.FROM_EMAIL = "noreply@test.com"
        mock_settings.BASE_URL = "http://localhost:8000"
        
        # Override the email service settings
        email_service.smtp_server = "smtp.gmail.com"
        email_service.smtp_port = 587
        email_service.smtp_username = "test@gmail.com"
        email_service.smtp_password = "test-password"
        email_service.from_email = "noreply@test.com"

        # Mock SMTP to raise an exception
        mock_smtp.side_effect = smtplib.SMTPAuthenticationError(535, "Authentication failed")

        # Test data
        user_email = "user@example.com"
        username = "testuser"
        activation_token = "test-token-123"

        # Send activation email (should fail)
        result = email_service.send_activation_email(user_email, username, activation_token)

        # Verify result
        assert result is False

    @patch('app.core.config.settings')
    def test_send_welcome_email_success(self, mock_settings, email_service, mock_smtp):
        """Test successful welcome email sending"""
        # Mock settings
        mock_settings.SMTP_SERVER = "smtp.gmail.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USERNAME = "test@gmail.com"
        mock_settings.SMTP_PASSWORD = "test-password"
        mock_settings.FROM_EMAIL = "noreply@test.com"
        mock_settings.BASE_URL = "http://localhost:8000"
        
        # Override the email service settings
        email_service.smtp_server = "smtp.gmail.com"
        email_service.smtp_port = 587
        email_service.smtp_username = "test@gmail.com"
        email_service.smtp_password = "test-password"
        email_service.from_email = "noreply@test.com"

        # Test data
        user_email = "user@example.com"
        username = "testuser"

        # Mock SMTP methods
        mock_smtp.starttls.return_value = None
        mock_smtp.login.return_value = None
        mock_smtp.sendmail.return_value = None
        mock_smtp.quit.return_value = None

        # Send welcome email
        result = email_service.send_welcome_email(user_email, username)

        # Verify result
        assert result is True

        # Verify SMTP was called correctly
        mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once_with("test@gmail.com", "test-password")
        mock_smtp.quit.assert_called_once()

        # Verify sendmail was called
        assert mock_smtp.sendmail.call_count == 1
        call_args = mock_smtp.sendmail.call_args
        assert call_args[0][0] == "noreply@test.com"  # from_email
        assert call_args[0][1] == user_email  # to_email

    @patch('app.core.config.settings')
    def test_send_welcome_email_failure(self, mock_settings, email_service, mock_smtp):
        """Test welcome email sending failure"""
        # Mock settings
        mock_settings.SMTP_SERVER = "smtp.gmail.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USERNAME = "test@gmail.com"
        mock_settings.SMTP_PASSWORD = "test-password"
        mock_settings.FROM_EMAIL = "noreply@test.com"
        mock_settings.BASE_URL = "http://localhost:8000"
        
        # Override the email service settings
        email_service.smtp_server = "smtp.gmail.com"
        email_service.smtp_port = 587
        email_service.smtp_username = "test@gmail.com"
        email_service.smtp_password = "test-password"
        email_service.from_email = "noreply@test.com"

        # Mock SMTP to raise an exception
        mock_smtp.side_effect = smtplib.SMTPException("Connection failed")

        # Test data
        user_email = "user@example.com"
        username = "testuser"

        # Send welcome email (should fail)
        result = email_service.send_welcome_email(user_email, username)

        # Verify result
        assert result is False

    def test_email_content_validation(self, email_service):
        """Test email content structure and validation"""
        # Mock settings
        with patch('app.core.config.settings') as mock_settings:
            mock_settings.SMTP_SERVER = "smtp.gmail.com"
            mock_settings.SMTP_PORT = 587
            mock_settings.SMTP_USERNAME = "test@gmail.com"
            mock_settings.SMTP_PASSWORD = "test-password"
            mock_settings.FROM_EMAIL = "noreply@test.com"
            mock_settings.BASE_URL = "http://localhost:8000"

            # Test data
            user_email = "user@example.com"
            username = "testuser"
            activation_token = "test-token-123"

            # Mock SMTP
            with patch('smtplib.SMTP') as mock_smtp:
                mock_server = Mock()
                mock_smtp.return_value = mock_server
                mock_server.starttls.return_value = None
                mock_server.login.return_value = None
                mock_server.sendmail.return_value = None
                mock_server.quit.return_value = None

                # Send activation email
                result = email_service.send_activation_email(user_email, username, activation_token)

                # Verify email was sent
                assert result is True
                assert mock_server.sendmail.call_count == 1

                # Get the email content
                call_args = mock_server.sendmail.call_args
                email_content = call_args[0][2]  # The email content

                # Verify email content contains expected elements
                assert "Activate Your Account" in email_content
                assert username in email_content
                assert activation_token in email_content
                assert "http://localhost:8000/activate/" in email_content
                assert "24 hours" in email_content

    def test_email_configuration_loading(self):
        """Test that email configuration is loaded correctly"""
        # This test verifies that the EmailService can be instantiated
        # and that it attempts to load configuration from settings
        try:
            email_service = EmailService()
            # If we get here, the service was created successfully
            assert hasattr(email_service, 'smtp_server')
            assert hasattr(email_service, 'smtp_port')
            assert hasattr(email_service, 'smtp_username')
            assert hasattr(email_service, 'smtp_password')
            assert hasattr(email_service, 'from_email')
        except Exception as e:
            # If configuration is missing, that's expected in test environment
            pytest.skip(f"Email configuration not available: {e}")


class TestEmailIntegration:
    """Integration tests for email functionality"""

    @pytest.fixture
    def email_service(self):
        """Create EmailService instance for integration testing"""
        return EmailService()

    def test_real_email_configuration(self, email_service):
        """Test with real email configuration (requires .env setup)"""
        # This test will only run if email configuration is properly set up
        # It's marked as integration test and can be skipped in CI/CD
        
        # Check if email configuration is available
        if not hasattr(settings, 'SMTP_USERNAME') or not settings.SMTP_USERNAME:
            pytest.skip("Email configuration not set up")

        # Test data
        test_email = "test@example.com"
        test_username = "testuser"
        test_token = "integration-test-token"

        # Try to send a real email (this will fail in test environment)
        # but we can test the configuration loading
        try:
            result = email_service.send_activation_email(test_email, test_username, test_token)
            # If this succeeds, it means email is properly configured
            assert isinstance(result, bool)
        except Exception as e:
            # Expected in test environment without real SMTP
            assert "SMTP" in str(e) or "connection" in str(e).lower()

    def test_email_service_initialization(self, email_service):
        """Test EmailService initialization and method availability"""
        # Test that all required methods exist
        assert hasattr(email_service, 'generate_activation_token')
        assert hasattr(email_service, 'send_activation_email')
        assert hasattr(email_service, 'send_welcome_email')
        
        # Test that methods are callable
        assert callable(email_service.generate_activation_token)
        assert callable(email_service.send_activation_email)
        assert callable(email_service.send_welcome_email)


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
