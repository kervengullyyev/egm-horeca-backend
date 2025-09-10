import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # Check if email configuration is available
        self.mail_username = os.getenv("MAIL_USERNAME")
        self.mail_password = os.getenv("MAIL_PASSWORD")
        
        if not self.mail_username or not self.mail_password:
            logger.warning("Email configuration not found. Password reset emails will not be sent.")
            self.fastmail = None
            return
            
        self.config = ConnectionConfig(
            MAIL_USERNAME=self.mail_username,
            MAIL_PASSWORD=self.mail_password,
            MAIL_FROM=os.getenv("MAIL_FROM", "noreply@horeca.com"),
            MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
            MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
        self.fastmail = FastMail(self.config)
    
    async def send_password_reset_email(self, email: str, reset_token: str, user_name: str = None) -> bool:
        """Send password reset email to user"""
        try:
            if not self.fastmail:
                logger.warning("Email service not configured. Cannot send password reset email.")
                return False
            # Create reset URL - you'll need to update this with your frontend URL
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            reset_url = f"{frontend_url}/reset-password?token={reset_token}"
            
            # Email template
            html_content = f"""
            <html>
            <body>
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #333;">Password Reset Request</h2>
                    <p>Hello {user_name or 'User'},</p>
                    <p>You have requested to reset your password. Click the button below to reset your password:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_url}" 
                           style="background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">
                            Reset Password
                        </a>
                    </div>
                    <p>If the button doesn't work, copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #666;">{reset_url}</p>
                    <p>This link will expire in 1 hour for security reasons.</p>
                    <p>If you didn't request this password reset, please ignore this email.</p>
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                    <p style="color: #666; font-size: 12px;">This is an automated message, please do not reply to this email.</p>
                </div>
            </body>
            </html>
            """
            
            message = MessageSchema(
                subject="Password Reset Request - Horeca",
                recipients=[email],
                body=html_content,
                subtype="html"
            )
            
            await self.fastmail.send_message(message)
            logger.info(f"Password reset email sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {str(e)}")
            return False
    
    async def send_password_reset_confirmation(self, email: str, user_name: str = None) -> bool:
        """Send password reset confirmation email"""
        try:
            if not self.fastmail:
                logger.warning("Email service not configured. Cannot send confirmation email.")
                return False
            html_content = f"""
            <html>
            <body>
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #333;">Password Reset Successful</h2>
                    <p>Hello {user_name or 'User'},</p>
                    <p>Your password has been successfully reset.</p>
                    <p>If you didn't make this change, please contact our support team immediately.</p>
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                    <p style="color: #666; font-size: 12px;">This is an automated message, please do not reply to this email.</p>
                </div>
            </body>
            </html>
            """
            
            message = MessageSchema(
                subject="Password Reset Successful - Horeca",
                recipients=[email],
                body=html_content,
                subtype="html"
            )
            
            await self.fastmail.send_message(message)
            logger.info(f"Password reset confirmation email sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send password reset confirmation email to {email}: {str(e)}")
            return False

# Global email service instance
email_service = EmailService()
