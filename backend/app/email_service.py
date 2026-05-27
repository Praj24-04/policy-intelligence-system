import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FRONTEND_URL

def send_reset_email(to_email: str, reset_token: str) -> bool:
    """
    Send a password reset email.
    Returns True on success, False on failure.
    Uses Gmail SMTP with an App Password (not your account password).
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        print(f"[EMAIL] SMTP not configured. Reset link: {FRONTEND_URL}/reset-password?token={reset_token}")
        return True  # Don't break the flow if email not configured in dev

    reset_link = f"{FRONTEND_URL}/reset-password?token={reset_token}"

    html = f"""
    <div style="font-family: Inter, sans-serif; max-width: 560px; margin: 0 auto; padding: 40px 24px;">
      <div style="margin-bottom: 32px;">
        <div style="display: inline-flex; align-items: center; gap: 8px;">
          <div style="width: 32px; height: 32px; background: #A3E635; border-radius: 8px;"></div>
          <span style="font-weight: 800; font-size: 18px;">PolicyIQ</span>
        </div>
      </div>
      <h1 style="font-size: 24px; font-weight: 800; margin-bottom: 16px; color: #0C0A09;">
        Reset your password
      </h1>
      <p style="color: #57534E; line-height: 1.6; margin-bottom: 32px;">
        We received a request to reset the password for your PolicyIQ account 
        associated with <strong>{to_email}</strong>. Click the button below to 
        choose a new password. This link expires in <strong>1 hour</strong>.
      </p>
      <a href="{reset_link}" 
         style="display: inline-block; background: #A3E635; color: #000; 
                padding: 14px 28px; border-radius: 8px; text-decoration: none;
                font-weight: 700; font-size: 15px; margin-bottom: 32px;">
        Reset Password &rarr;
      </a>
      <p style="color: #A8A29E; font-size: 13px; line-height: 1.6;">
        If you didn't request a password reset, you can safely ignore this email. 
        Your password will not change.
      </p>
      <hr style="border: none; border-top: 1px solid #E7E5E4; margin: 32px 0;" />
      <p style="color: #A8A29E; font-size: 12px;">
        &copy; 2026 PolicyIQ Inc. &bull; 
        <a href="{FRONTEND_URL}" style="color: #A8A29E;">policyiq.app</a>
      </p>
    </div>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Reset your PolicyIQ password"
    msg["From"]    = f"PolicyIQ <{SMTP_USER}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
        print(f"[EMAIL] Reset email sent to {to_email}")
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send to {to_email}: {e}")
        return False
