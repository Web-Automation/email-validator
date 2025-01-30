import smtplib
import re
from ping import ping_domain
from dns_lookup import get_mx_record


"""*********************************************************************************************************************************************************************************
* Function to validate an email address by checking its format, domain ping, and SMTP server connection.

* @param {string} email - The email address to validate.
* @param {string} [sender_email='validuser@yourdomain.com'] - A valid sender email to use in the SMTP validation process (replace 'validuser@yourdomain.com' with a valid email id).
* @returns {boolean} - Returns True if the email address is valid, False otherwise.
**********************************************************************************************************************************************************************************"""

def validate_email_smtp(email, sender_email='validuser@yourdomain.com'):
    # Use regex to check if the email format is correct
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(regex, email):
        print(f"Invalid email format: {email}")
        return False

    # Extract the domain from the email
    domain = email.split('@')[1]

    # Ping the domain before checking the MX record
    if not ping_domain(domain):
        print(f"{email}: Domain is not responsive to ping. Likely a disposable domain.")
        return False

    # Get the MX record for the domain
    mx_record = get_mx_record(domain)
    if not mx_record:
        print(f"{email}: Unable to find a valid mail server (MX record).")
        return False

    # Try to connect to the SMTP server with a valid sender email
    try:
        print(f"Connecting to SMTP server: {mx_record}")
        server = smtplib.SMTP(mx_record)
        server.set_debuglevel(0)  # Disable verbose output

        # Connect to the server
        server.connect(mx_record)

        # Send HELO command
        server.helo()

        # Send MAIL FROM command (using a valid sender email to avoid anti-spoofing issues)
        server.mail(sender_email)

        # Send RCPT TO command (the email we are verifying)
        code, message = server.rcpt(email)
        
        if code == 250:
            print(f"{email} exists on the server!")
            return True
        else:
            print(f"{email} does not exist on the server: {message}")
            return False
    except smtplib.SMTPConnectError:
        print(f"Could not connect to the SMTP server for {domain}")
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    finally:
        # Ensure server.quit() is only called if the server was successfully initialized
        if 'server' in locals():
            server.quit()


# Usage
if __name__ == '__main__':
    email_to_check = "email to test"
    if validate_email_smtp(email_to_check):
        print(f"{email_to_check} is a valid email address!")
    else:
        print(f"{email_to_check} is not a valid email address.")
