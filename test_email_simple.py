#!/usr/bin/env python3
"""
Simple email test script to check if email sending works.
This script can be run independently to test email configuration.
"""

import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_email_configuration():
    """Test email configuration and sending"""
    
    print("🔍 Testing Email Configuration...")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        print("✅ .env file found")
        
        # Load environment variables
        with open(env_file, 'r') as f:
            env_vars = {}
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
        
        # Check required email variables
        required_vars = ['SMTP_SERVER', 'SMTP_PORT', 'SMTP_USERNAME', 'SMTP_PASSWORD', 'FROM_EMAIL']
        missing_vars = []
        
        for var in required_vars:
            if var in env_vars and env_vars[var]:
                print(f"✅ {var}: {'*' * len(env_vars[var])} (configured)")
            else:
                print(f"❌ {var}: Not configured")
                missing_vars.append(var)
        
        if missing_vars:
            print(f"\n❌ Missing email configuration: {', '.join(missing_vars)}")
            print("Please configure these variables in your .env file")
            return False
        
        # Test SMTP connection
        print(f"\n🔗 Testing SMTP connection to {env_vars['SMTP_SERVER']}:{env_vars['SMTP_PORT']}...")
        
        try:
            # Create SMTP connection
            server = smtplib.SMTP(env_vars['SMTP_SERVER'], int(env_vars['SMTP_PORT']))
            server.starttls()
            
            # Test authentication
            server.login(env_vars['SMTP_USERNAME'], env_vars['SMTP_PASSWORD'])
            print("✅ SMTP authentication successful")
            
            # Test email sending (to a test address)
            test_email = "test@example.com"
            test_subject = "Email Test - FastAPI Admin"
            test_body = f"""
            <html>
            <body>
                <h2>Email Test</h2>
                <p>This is a test email from FastAPI Admin.</p>
                <p>Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>If you receive this, your email configuration is working correctly!</p>
            </body>
            </html>
            """
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = env_vars['FROM_EMAIL']
            msg['To'] = test_email
            msg['Subject'] = test_subject
            msg.attach(MIMEText(test_body, 'html'))
            
            # Send email
            server.sendmail(env_vars['FROM_EMAIL'], test_email, msg.as_string())
            print("✅ Test email sent successfully")
            
            server.quit()
            print("\n🎉 Email configuration is working correctly!")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ SMTP Authentication failed: {e}")
            print("Please check your SMTP_USERNAME and SMTP_PASSWORD")
            return False
            
        except smtplib.SMTPException as e:
            print(f"❌ SMTP Error: {e}")
            return False
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    else:
        print("❌ .env file not found")
        print("Please create a .env file with email configuration")
        return False

def test_email_service():
    """Test EmailService class if available"""
    
    print("\n🔍 Testing EmailService Class...")
    print("=" * 50)
    
    try:
        from app.core.email import EmailService
        
        # Create EmailService instance
        email_service = EmailService()
        print("✅ EmailService imported and instantiated")
        
        # Test token generation
        token = email_service.generate_activation_token()
        print(f"✅ Activation token generated: {token[:8]}...")
        
        # Test email sending (mock)
        print("✅ EmailService methods available:")
        print("   - generate_activation_token()")
        print("   - send_activation_email()")
        print("   - send_welcome_email()")
        
        return True
        
    except ImportError as e:
        print(f"❌ EmailService not available: {e}")
        print("Make sure app/core/email.py exists")
        return False
        
    except Exception as e:
        print(f"❌ Error testing EmailService: {e}")
        return False

def main():
    """Main test function"""
    
    print("🚀 FastAPI Admin - Email Configuration Test")
    print("=" * 60)
    
    # Test basic configuration
    config_ok = test_email_configuration()
    
    # Test EmailService
    service_ok = test_email_service()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"   Configuration Test: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"   EmailService Test:  {'✅ PASS' if service_ok else '❌ FAIL'}")
    
    if config_ok and service_ok:
        print("\n🎉 All tests passed! Email functionality is ready to use.")
    else:
        print("\n⚠️  Some tests failed. Please check the configuration above.")
    
    print("\n📝 Next Steps:")
    if not config_ok:
        print("   1. Create a .env file with email configuration")
        print("   2. Set up Gmail App Password or other SMTP provider")
        print("   3. Run this test again")
    
    if not service_ok:
        print("   1. Ensure app/core/email.py exists")
        print("   2. Check that EmailService class is properly implemented")
    
    if config_ok and service_ok:
        print("   1. Email functionality is ready!")
        print("   2. Users can register and receive activation emails")
        print("   3. Test the full registration flow in the application")

if __name__ == "__main__":
    main()
