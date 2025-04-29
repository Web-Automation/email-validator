import smtplib
import re
from ping import ping_domain
from dns_lookup import get_mx_record
from suggestion import suggest_email_correction


"""*********************************************************************************************************************************************************************************
* Function to validate an email address by checking its format, domain ping, MX record lookup, and SMTP verification.

* @param {string} email - The email address to validate.
* @param {string} [sender_email='validuser@yourdomain.com'] - A valid sender email to use in the SMTP validation process (replace 'validuser@yourdomain.com' with a valid email id).
* @returns {boolean} - Returns True if the email address is valid, False otherwise.
**********************************************************************************************************************************************************************************"""

def validate_email_smtp(email, sender_email='aliduser@yourdomain.com'):   # Replace with the sender_email with a valid email
    # Use regex to check if the email format is correct
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(regex, email):
        return {"status": False, "reason": "Invalid format"}  # Exit if the format is invalid

    # Extract the domain from the email
    domain = email.split('@')[1]

    # Suggest domain correction if a typo is found (e.g., "gmial.com" -> "gmail.com")
    suggested_email = suggest_email_correction(email)
    if suggested_email:
        return {"status": False, "reason": "Domain suggestion", "suggestion": suggested_email}  # Exit if the domain suggestion is made
    
    # Ping the domain to check if it's active/reachable before checking the MX record
    if not ping_domain(domain):
        print(f"{email}: Domain is not responsive to ping. Likely a disposable domain.")
        return {"status": False, "reason": f"{email}: Domain is not responsive to ping. Likely a disposable domain."}

    # Retrieve MX record (mail exchange server) for the domain
    mx_record = get_mx_record(domain)
    if not mx_record:
        print(f"{email}: Unable to find a valid mail server (MX record).")
        return {"status": False, "reason": f"{email}: Unable to find a valid mail server (MX record)."}

    # Try to connect to the SMTP server with a valid sender email for SMTP verification
    try:
        print(f"Connecting to SMTP server: {mx_record}")
        # Initialize SMTP server object
        server = smtplib.SMTP(mx_record)
        server.set_debuglevel(0)  # Disable verbose output

        # Establish connection with the mail server
        server.connect(mx_record)

        # Send HELO command for SMTP handshake
        server.helo()

        # Send MAIL FROM command (using a valid sender email to avoid anti-spoofing issues)
        server.mail(sender_email)

        # Send RCPT TO command (the email we are verifying)
        code, message = server.rcpt(email)
        
        if code == 250:
            print(f"{email} exists on the server!")
            return {"status": True}
        else:
            print(f"{email} does not exist on the server: {message}")
            return {"status": False, "reason": f"{email} does not exist on server"}
    except smtplib.SMTPConnectError:
        print(f"Could not connect to the SMTP server for {domain}")
        return {"status": False, "reason": f"Could not connect to the SMTP server for {domain}"}
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {e}")
        return {"status": False, "reason": f"SMTP error occurred: {e}"}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"status": False, "reason": f"Unexpected error: {e}"}
    finally:
        # Ensure server.quit() is only called if the server was successfully initialized
        if 'server' in locals():
            server.quit()


# Usage
if __name__ == '__main__':
    email_to_check = "anshuman.jswal@tsn.com"    # Replace with the email you want to validate
    
    result = validate_email_smtp(email_to_check)

    if result["status"]:
        print(f"{email_to_check} is a valid email address!")
    elif result.get("reason") == "Domain suggestion":
        print(f"Did you mean: {result['suggestion']}?")
    elif result.get("reason") == "Invalid format":
        print(f"{email_to_check} is not a valid email address (bad format).")
    else:
        print(f"{email_to_check} is not a valid email address.")
