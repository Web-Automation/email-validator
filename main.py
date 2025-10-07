import smtplib
import re
from ping import ping_domain
from dns_lookup import get_mx_record
from suggestion import suggest_email_correction
from suspicious_email import is_catch_all_domain



"""******************************************************************************************************************
* Function to validate an email address by checking its format, domain ping, MX record lookup, and SMTP verification.

* It performs:
*   - Format validation
*   - Domain typo suggestions
*   - Ping check
*   - MX record lookup
*   - SMTP RCPT check
*   - CSingle MX record & Catch-all based risk classification
*
* @param email {string} - Email address to validate.
* @param sender_email {string} - A valid sender email used for SMTP communication.
* @returns {dict} - JSON object with full diagnostic result including:
*                   - email: original email tested
*                   - result: "Valid", "Invalid", "Suspicious" or "Risky"
*                   - did_you_mean: suggested corrected email, if any
*                   - format_valid: True/False (regex format validation)
*                   - ping_success: True/False (whether domain is reachable)
*                   - mx_found: True/False (whether MX records are present)
*                   - single_mx_record: True/False,
*                   - smtp_deliverable: True/False (whether SMTP accepted the address)
*                   - is_catch_all: True/False (if domain accepts all emails)
********************************************************************************************************************"""

def validate_email_smtp(email, sender_email='validuser@yourdomain.com'):   # Replace with the sender_email with a valid email
    # Initialize all diagnostic flags
    format_valid = False
    ping_success = False
    mx_found = False
    single_mx_record = False
    smtp_deliverable = False
    is_catch_all = False
    suggestion = ""
    result = "Invalid"  # Default result unless proved otherwise
    
    # Use regex to check if the email format is correct
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    format_valid = bool(re.match(regex, email))

    if format_valid:
        # Extract the domain part from the email
        local_part, domain = email.lower().split('@')

   
    # Suggest domain correction if a typo is found (e.g., "gmial.com" -> "gmail.com")
    suggested_email = suggest_email_correction(email) or ""
    suggestion = suggested_email
    
    # Ping the domain to check if it's active/reachable before checking the MX record
    ping_success = ping_domain(domain)
    
    # Retrieve MX record (mail exchange server) for the domain
    has_a_record, has_mx_record, sorted_mx = get_mx_record(domain)
    mx_found = has_mx_record
    print("MX Lookup Result:", has_a_record, has_mx_record, sorted_mx)

    if has_mx_record:
        # If only one MX record exists, treat the email as suspicious (not valid)
        if(len(sorted_mx) == 1):
                single_mx_record = True   
            
    # Try to connect to the SMTP server with a valid sender email for SMTP verification
    try:
        if mx_found:
            print(f"Connecting to SMTP server: {sorted_mx[1][1]}")
            smtp_host = sorted_mx[1][1]
    
            # Initialize SMTP server object
            with smtplib.SMTP(smtp_host, port=587, timeout=50) as server:
                server.set_debuglevel(0)  # Disable verbose output

                # Start TLS (encryption)
                server.starttls()

                # Send HELO command for SMTP handshake
                server.helo()

                # Send MAIL FROM command (using a valid sender email to avoid anti-spoofing issues)
                server.mail(sender_email)

                # Send RCPT TO command (the email we are verifying)
                code, _ = server.rcpt(email)
                
                # Check if the SMTP server accepts the recipient email (code 250 means OK)
                smtp_deliverable = code == 250
                            
                # Check if the domain is catch-all (accepts any email)
                if smtp_deliverable:
                    is_catch_all = is_catch_all_domain(server, domain)
                    
    except smtplib.SMTPConnectError:
        print(f"Could not connect to the SMTP server for {domain}")
        pass
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {e}")
        pass
    except Exception as e:
        print(f"Unexpected error: {e}")
        pass
    
    # Final result classification whether email is valid, invalid, risky or suspicious
    # Disposable if: format valid, MX found, ping fails
    if(
        format_valid and mx_found and not ping_success
    ):
        result = "Disposable"
    # Invalid if: format bad, ping fails, no MX, SMTP failed, or both catch-all + single MX
    elif(
        not format_valid or 
        not ping_success or 
        not mx_found or 
        not smtp_deliverable or 
        (is_catch_all and single_mx_record)
    ):
        result = "Invalid"
    # Suspicious if catch-all domain only
    elif is_catch_all:   
        result = "Suspicious"
    # Risky if only 1 MX record but not a catch-all 
    elif single_mx_record:
        result = "Risky"
    # Valid if all checks passed and domain not risky/suspicious
    else:
        result = "Valid"

    # Return structured diagnostic report
    return {
        "email_valid": {
            "email": email,
            "result": result,
            "did_you_mean": suggestion,
            "format_valid": format_valid,
            "ping_success": ping_success,
            "mx_found": mx_found,
            "single_mx_record": single_mx_record,
            "smtp_deliverable": smtp_deliverable,
            "is_catch_all": is_catch_all
        }
    }
    
    


# Usage
if __name__ == '__main__':
    # Define the email address to check
    email_to_check = "validuser@yourdomain.com"    # Replace with the email you want to validate    
    # Call the validate_email_smtp function to check the validity of the email
    result = validate_email_smtp(email_to_check)
    print(result)  # Log the result(jSON Format)
