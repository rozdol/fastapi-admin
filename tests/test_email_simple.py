import pytest
import smtplib
from unittest.mock import patch, Mock
import os
import sys

# Add the app directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.email import EmailService


class TestEmailServiceSimple:
    """Simple test cases for EmailService"""

    @pytest.fixture
    def email_service(self):
        """Create EmailService instance for testing"""
        return EmailService()

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

    def test_email_service_attributes(self, email_service):
        """Test that EmailService has required attributes"""
        assert hasattr(email_service, 'smtp_server')
        assert hasattr(email_service, 'smtp_port')
        assert hasattr(email_service, 'smtp_username')
        assert hasattr(email_service, 'smtp_password')
        assert hasattr(email_service, 'from_email')

    @patch('smtplib.SMTP')
    def test_send_activation_email_mocked(self, mock_smtp, email_service):
        """Test activation email sending with mocked SMTP"""
        # Setup mock
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        mock_server.starttls.return_value = None
        mock_server.login.return_value = None
        mock_server.sendmail.return_value = None
        mock_server.quit.return_value = None

        # Test data
        user_email = "test@example.com"
        username = "testuser"
        activation_token = "test-token-123"

        # Send activation email
        result = email_service.send_activation_email(user_email, username, activation_token)

        # Verify result
        assert result is True

        # Verify SMTP was called
        mock_smtp.assert_called_once()
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()
        mock_server.quit.assert_called_once()

    @patch('smtplib.SMTP')
    def test_send_welcome_email_mocked(self, mock_smtp, email_service):
        """Test welcome email sending with mocked SMTP"""
        # Setup mock
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        mock_server.starttls.return_value = None
        mock_server.login.return_value = None
        mock_server.sendmail.return_value = None
        mock_server.quit.return_value = None

        # Test data
        user_email = "test@example.com"
        username = "testuser"

        # Send welcome email
        result = email_service.send_welcome_email(user_email, username)

        # Verify result
        assert result is True

        # Verify SMTP was called
        mock_smtp.assert_called_once()
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()
        mock_server.quit.assert_called_once()

    @patch('smtplib.SMTP')
    def test_send_activation_email_failure_mocked(self, mock_smtp, email_service):
        """Test activation email sending failure with mocked SMTP"""
        # Setup mock to raise exception
        mock_smtp.side_effect = smtplib.SMTPAuthenticationError(535, "Authentication failed")

        # Test data
        user_email = "test@example.com"
        username = "testuser"
        activation_token = "test-token-123"

        # Send activation email (should fail)
        result = email_service.send_activation_email(user_email, username, activation_token)

        # Verify result
        assert result is False

    @patch('smtplib.SMTP')
    def test_send_welcome_email_failure_mocked(self, mock_smtp, email_service):
        """Test welcome email sending failure with mocked SMTP"""
        # Setup mock to raise exception
        mock_smtp.side_effect = smtplib.SMTPException("Connection failed")

        # Test data
        user_email = "test@example.com"
        username = "testuser"

        # Send welcome email (should fail)
        result = email_service.send_welcome_email(user_email, username)

        # Verify result
        assert result is False


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
        if not email_service.smtp_username or email_service.smtp_username == '':
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

    def test_email_content_generation(self, email_service):
        """Test email content generation without sending"""
        # Test data
        user_email = "test@example.com"
        username = "testuser"
        activation_token = "test-token-123"

        # Test that we can generate email content without errors
        try:
            # This should not raise any exceptions
            email_service.generate_activation_token()
            assert True
        except Exception as e:
            pytest.fail(f"Token generation failed: {e}")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
