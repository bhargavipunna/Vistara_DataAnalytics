"""
Email Service using SendGrid
Handles application confirmation and status update emails
"""
import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent

logger = logging.getLogger(__name__)

# Configurable sender — change this when domain is verified
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "careers@vistaravidyaanidhi.org.in")
FROM_NAME = os.getenv("SENDGRID_FROM_NAME", "Vistara Vidyaanidhi Educational Trust")


def get_base_html_template(title: str, preheader: str, content: str) -> str:
    """Returns a base HTML template with Vistara branding."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin:0;padding:0;background-color:#f4f7f4;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;">
        <span style="display:none;font-size:1px;color:#f4f7f4;line-height:1px;max-height:0px;max-width:0px;opacity:0;overflow:hidden;">
            {preheader}
        </span>
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f7f4;padding:32px 16px;">
            <tr>
                <td align="center">
                    <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
                        <!-- Header -->
                        <tr>
                            <td style="background-color:#1a3c2a;padding:32px 40px;text-align:center;">
                                <h1 style="color:#ffffff;margin:0;font-size:22px;font-weight:700;letter-spacing:0.5px;">
                                    Vistara Vidyaanidhi Educational Trust
                                </h1>
                                <p style="color:#a8d5ba;margin:8px 0 0;font-size:13px;letter-spacing:1px;text-transform:uppercase;">
                                    {title}
                                </p>
                            </td>
                        </tr>
                        <!-- Body Content -->
                        <tr>
                            <td style="padding:40px;">
                                {content}
                                <p style="color:#555;font-size:14px;line-height:1.6;margin:32px 0 0;">
                                    Warm regards,<br>
                                    <strong>Recruitment Team</strong><br>
                                    Vistara Vidyaanidhi Educational Trust
                                </p>
                            </td>
                        </tr>
                        <!-- Footer -->
                        <tr>
                            <td style="background-color:#f8faf8;padding:20px 40px;border-top:1px solid #e8efe8;text-align:center;">
                                <p style="color:#999;font-size:12px;margin:0;line-height:1.5;">
                                    This is an automated message. Please do not reply to this email.<br>
                                    &copy; 2026 Vistara Vidyaanidhi Educational Trust. All rights reserved.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


def send_application_confirmation(
    to_email: str,
    applicant_name: str,
    applicant_id: str,
    job_title: str,
    requisition_id: str,
    department: str = "",
    location: str = "",
    employment_type: str = "",
    work_mode: str = "Hybrid",
) -> bool:
    """Send confirmation email after successful submission."""
    if not SENDGRID_API_KEY:
        logger.warning("SENDGRID_API_KEY not set — skipping email")
        return False

    subject = f"Application Received — {job_title} | Vistara Vidyaanidhi Educational Trust"
    
    content = f"""
        <h2 style="color:#1a3c2a;margin:0 0 8px;font-size:20px;">
            Thank You for Your Application
        </h2>
        <p style="color:#555;font-size:15px;line-height:1.6;margin:0 0 24px;">
            Dear {applicant_name},
        </p>
        <p style="color:#555;font-size:15px;line-height:1.6;margin:0 0 24px;">
            We have successfully received your application. Our recruitment team will carefully review your profile, and we will reach out to you if your qualifications align with the requirements for this position.
        </p>

        <!-- Application Details Card -->
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f0f7f2;border-radius:8px;border:1px solid #d4e8da;margin-bottom:24px;">
            <tr>
                <td style="padding:24px;">
                    <p style="color:#1a3c2a;font-weight:700;font-size:14px;margin:0 0 16px;text-transform:uppercase;letter-spacing:1px;">
                        Application Details
                    </p>
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                        <tr>
                            <td style="padding:6px 0;color:#777;font-size:13px;width:140px;">Applicant ID</td>
                            <td style="padding:6px 0;color:#1a3c2a;font-size:14px;font-weight:600;">{applicant_id}</td>
                        </tr>
                        <tr>
                            <td style="padding:6px 0;color:#777;font-size:13px;">Job Title</td>
                            <td style="padding:6px 0;color:#333;font-size:14px;font-weight:600;">{job_title}</td>
                        </tr>
                        <tr>
                            <td style="padding:6px 0;color:#777;font-size:13px;">Requisition ID</td>
                            <td style="padding:6px 0;color:#333;font-size:14px;">{requisition_id}</td>
                        </tr>
                        <tr>
                            <td style="padding:6px 0;color:#777;font-size:13px;">Department</td>
                            <td style="padding:6px 0;color:#333;font-size:14px;">{department}</td>
                        </tr>
                        <tr>
                            <td style="padding:6px 0;color:#777;font-size:13px;">Location</td>
                            <td style="padding:6px 0;color:#333;font-size:14px;">{location}</td>
                        </tr>
                        <tr>
                            <td style="padding:6px 0;color:#777;font-size:13px;">Employment Type</td>
                            <td style="padding:6px 0;color:#333;font-size:14px;">{employment_type}</td>
                        </tr>
                        <tr>
                            <td style="padding:6px 0;color:#777;font-size:13px;">Work Mode</td>
                            <td style="padding:6px 0;color:#333;font-size:14px;">{work_mode}</td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>

        <p style="color:#555;font-size:14px;line-height:1.6;margin:0 0 8px;">
            Please save your <strong>Applicant ID ({applicant_id})</strong> for future reference and correspondence.
        </p>
        <p style="color:#555;font-size:14px;line-height:1.6;margin:0;">
            All subsequent communication will be sent to this email address.
        </p>
    """

    html_content = get_base_html_template("CAREERS", "We have received your application", content)

    try:
        message = Mail(
            from_email=(FROM_EMAIL, FROM_NAME),
            to_emails=to_email,
            subject=subject,
            html_content=html_content,
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        logger.info(f"Confirmation email sent to {to_email} — status: {response.status_code}")
        return response.status_code in (200, 201, 202)
    except Exception as e:
        logger.error(f"Failed to send confirmation email to {to_email}: {str(e)}")
        return False


def send_application_status_update(
    to_email: str,
    applicant_name: str,
    applicant_id: str,
    job_title: str,
    status: str,
    custom_message: str = "",
) -> bool:
    """Send an update email to the applicant regarding their application status."""
    if not SENDGRID_API_KEY:
        logger.warning("SENDGRID_API_KEY not set — skipping email")
        return False

    status_formatted = status.replace('_', ' ').title()
    subject = f"Application Update: {status_formatted} — {job_title}"
    
    # Define custom content based on status
    if status == 'shortlisted':
        title = "Application Shortlisted"
        main_text = f"We are pleased to inform you that your application for the <strong>{job_title}</strong> position has been shortlisted."
    elif status == 'interview_scheduled':
        title = "Interview Scheduled"
        main_text = f"We are writing to confirm that an interview has been scheduled for your application for the <strong>{job_title}</strong> position."
    elif status == 'offer_extended':
        title = "Offer Extended"
        main_text = f"Congratulations! We are delighted to extend an offer for the <strong>{job_title}</strong> position."
    elif status == 'rejected':
        title = "Application Update"
        main_text = f"Thank you for your interest in the <strong>{job_title}</strong> position. After careful consideration, we have decided to move forward with other candidates who more closely align with our current needs."
    elif status == 'under_review':
        title = "Application Under Review"
        main_text = f"Your application for the <strong>{job_title}</strong> position is currently under review by our team."
    else:
        title = "Application Status Update"
        main_text = f"There is an update regarding your application for the <strong>{job_title}</strong> position."

    content_html = f"""
        <h2 style="color:#1a3c2a;margin:0 0 8px;font-size:20px;">
            {title}
        </h2>
        <p style="color:#555;font-size:15px;line-height:1.6;margin:0 0 24px;">
            Dear {applicant_name},
        </p>
        <p style="color:#555;font-size:15px;line-height:1.6;margin:0 0 24px;">
            {main_text}
        </p>
    """

    if custom_message:
        # Format the custom message with basic line breaks
        formatted_message = custom_message.replace('\n', '<br>')
        content_html += f"""
        <div style="background-color:#f8f9fa;border-left:4px solid #1a3c2a;padding:16px 24px;margin-bottom:24px;">
            <p style="color:#444;font-size:14px;line-height:1.6;margin:0;">
                {formatted_message}
            </p>
        </div>
        """

    content_html += f"""
        <p style="color:#555;font-size:14px;line-height:1.6;margin:0;">
            Applicant ID: <strong>{applicant_id}</strong>
        </p>
    """

    html_content = get_base_html_template("CAREERS UPDATE", title, content_html)

    try:
        message = Mail(
            from_email=(FROM_EMAIL, FROM_NAME),
            to_emails=to_email,
            subject=subject,
            html_content=html_content,
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        logger.info(f"Status update email sent to {to_email} — status: {response.status_code}")
        return response.status_code in (200, 201, 202)
    except Exception as e:
        logger.error(f"Failed to send status update email to {to_email}: {str(e)}")
        return False
