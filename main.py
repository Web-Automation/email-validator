import re
import time
import socket 
import smtplib
from ping import ping_domain
from dns_lookup import get_mx_record
from suggestion import suggest_email_correction
from suspicious_email import is_catch_all_domain


"""******************************************************************************************************************
* Function to validate an email address by checking its format, domain ping, MX record lookup, and SMTP verification.
* Validation Steps:
*   - Format validation using regex
*   - Domain typo correction suggestion
*   - Domain ping test
*   - MX record lookup
*   - SMTP RCPT check using ports 25 and 587
*   - Classification based on MX record and catch-all behavior

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
    # Initialize diagnostic flags and default result
    format_valid = False
    ping_success = False
    mx_found = False
    single_mx_record = False
    smtp_deliverable = False
    is_catch_all = False
    suggestion = ""
    result = "Invalid"  # Default result unless proved otherwise
    
    # Step 1: Use regex to check if the email format is correct
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    format_valid = bool(re.match(regex, email))

    # Step 2: If format is valid, extract domain: 
    if format_valid:
        local_part, domain = email.lower().split('@') # Extract the domain part from the email

    # Step 3: Suggest domain correction if a typo is found (e.g., "gmial.com" -> "gmail.com")
    suggested_email = suggest_email_correction(email) or ""
    suggestion = suggested_email
    
    # Step 4: Ping the domain to check if it's active/reachable before checking the MX record
    ping_success = ping_domain(domain)

    # Step 5: Retrieve MX record (mail exchange server) for the domain
    has_a_record, has_mx_record, sorted_mx = get_mx_record(domain)
    mx_found = has_mx_record
    print("MX Lookup Result:", has_a_record, has_mx_record, sorted_mx)

    # Step 6: Check if only one MX record exists — flag it as "suspicious"
    if has_mx_record:
        # If only one MX record exists, treat the email as suspicious (not valid)
        if(len(sorted_mx) == 1):
                single_mx_record = True 
    
    # Step 7: Begin SMTP validation using MX records      
    if mx_found:
        print(f"Attempting SMTP connection to: {sorted_mx[0][1]}")
        smtp_host = sorted_mx[0][1] # Use top-priority MX record
        smtp_connected = False
        server = None  # To clean up later

        # Try to connect to the SMTP server with a valid sender email for SMTP verification
        # Try SMTP on port 25 first (default SMTP port)
        try:
            print(f"Trying SMTP on port 25 for host: {smtp_host}")
            server = smtplib.SMTP(smtp_host, port=25, timeout=10)
            server.set_debuglevel(0)
            server.helo()
            server.mail(sender_email)
            smtp_connected = True
        except (socket.timeout, TimeoutError) as e:
            print(f"Port 25 timed out: {e}")
        except ConnectionRefusedError as e:
            print(f"Port 25: Connection refused: {e}")
        except Exception as e:
            print(f"Port 25 failed due to error: {e}")
            
        # If port 25 did not connect, fallback to port 587 with STARTTLS (secure alternative)
        if not smtp_connected:
            try:
                print(f"Falling back to port 587 with STARTTLS for host: {smtp_host}")
                server = smtplib.SMTP(smtp_host, port=587, timeout=10)
                server.set_debuglevel(0)
                server.ehlo()
                server.starttls()  # Upgrade to secure TLS connection
                server.ehlo()
                server.mail(sender_email)
                smtp_connected = True
            except Exception as e2:
                print(f"Port 587 with STARTTLS also failed: {e2}")

        # Step 8: If connected successfully, test the recipient email using RCPT TO
        if smtp_connected and server:
            try:
                code, _ = server.rcpt(email)
                smtp_deliverable = code == 250   # 250 means OK (email accepted)
                # Check for catch-all behaviour if email is deliverable
                if smtp_deliverable:
                    is_catch_all = is_catch_all_domain(server, domain)

            except smtplib.SMTPException as e:
                print(f"SMTP RCPT TO error: {e}")
            except Exception as e:
                print(f"Unexpected error during RCPT TO: {e}")
            finally:
                server.quit()
            
    # Result classification based on test outcomes whether email is valid, invalid, risky or suspicious    
    # Disposable = all valid but ping fails (possible temporary domain or fake)
    if format_valid and mx_found and not ping_success:
        result = "Disposable"
        
    # Invalid if any core failure:  bad format, ping fails, no MX, SMTP failed, or both catch-all + single MX
    elif (
        not format_valid or 
        not ping_success or 
        not mx_found or 
        not smtp_deliverable or 
        (is_catch_all and single_mx_record)
    ):
        result = "Invalid"
        
    # Suspicious when passes delivery but domain is catch-all (no real validation)
    elif is_catch_all:   
        result = "Suspicious"
        
    # Risky when domain only has one MX record, but not catch-all
    elif single_mx_record:
        result = "Risky"

    # Valid if all checks passed, no red flags and domain not risky/suspicious
    else:
        result = "Valid"

    # Return structured result dictionary
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
