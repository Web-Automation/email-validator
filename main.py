import re
from ping import ping_domain
from dns_lookup import get_mx_record
from suggestion import suggest_email_correction
from smtp_validation import smtp_delivery_check


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
    
    # Step 7: Begin SMTP validation using MX records & test recipient email using RCPT check to see if the email is deliverable   
    if mx_found:
        smtp_host = sorted_mx[0][1] # Use top-priority MX record
        print(f"Attempting SMTP connection to: {smtp_host}")
        
        # Check SMTP deliverability and catch-all status
        smtp_deliverable, is_catch_all = smtp_delivery_check(
            email=email,
            domain=smtp_host,      # Use MX host for connection
            sender_email=sender_email
        )
            
    # Result classification based on test outcomes whether email is valid, invalid, risky, suspicious, or disposable    
    # Disposable: Valid format, MX found, but ping failed (possibly a temporary or fake domain)
    if format_valid and mx_found and not ping_success:
        result = "Disposable"

    # Invalid: Any core failure like bad format, ping failure, no MX record
    elif not format_valid or not ping_success or not mx_found:
        result = "Invalid"

    # Risky: If SMTP deliverability is None and MX exists, or if the domain is a catch-all
    elif (smtp_deliverable is None and mx_found) or is_catch_all:
        result = "Risky"

    # Suspicious: Domain has only one MX record, and it's not a catch-all
    elif single_mx_record:
        result = "Suspicious"
 
    # Safe to Send: All checks passed, no issues, domain is healthy
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
