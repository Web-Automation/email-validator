import smtplib
import uuid
from dns_lookup import get_mx_record

"""***********************************************************************************************************
* Function to detect if a domain is configured as a catch-all mail server. 
* A catch-all server accepts emails sent to any address at the domain, even if the email address doesn't exist.

* @param {string} domain - The domain to be tested for catch-all configuration.
* @param {string} sender_email - A valid sender email to use during the SMTP handshake.
* @returns {bool} - Returns True if the domain behaves like a catch-all, False otherwise.
************************************************************************************************************"""
def is_catch_all_domain(domain, sender_email):
    # Generate a random, likely non-existent email address on the domain
    test_email = f"{uuid.uuid4().hex[:10]}@{domain}"

    # Retrieve MX records for the domain
    mx_records = get_mx_record(domain)
    if not mx_records:
        return False  # Domain does not handle email

    # Sort MX records by priority
    for _, mx in sorted(mx_records, key=lambda x: x[0]):
        try:
            # Establish SMTP connection
            with smtplib.SMTP(mx, 25, timeout=10) as server:
                server.helo()
                server.mail(sender_email)

                # Test sending to the generated (fake) recipient
                code, _ = server.rcpt(test_email)

                if code == 250:
                    return True  # Server accepts unknown address = likely catch-all
        except Exception:
            continue  # If error occurs, try next MX

    return False  # None of the MX records accepted the fake address
