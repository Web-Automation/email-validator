# email-validator
A comprehensive Python email validation tool that verifies the existence and reliability of email addresses through multiple checks. Designed as modular functions, it can be integrated into various applications, including user registration systems, marketing campaigns, and email list validation.

- **Format Check:** Validates if the email follows the correct syntax using regular expressions.
- **Domain Suggestion:** Detects typos in the domain and suggests corrections (e.g., "gmil.com"), the tool suggests a correction (e.g., "gmail.com").  
  This is implemented using:
   - Fuzzy string matching (via the `fuzzywuzzy` library)
   - Machine learning-based similarity, using **n-gram character features** with `TfidfVectorizer` and **cosine similarity** from `scikit-learn`.

- **Ping Check:** Pings the domain to confirm it is reachable and not a disposable or dead domain.
- **MX Record Lookup:**
    - Checks if the domain has valid Mail Exchange (MX) records.
    - Validates that the domain has Mail Exchange (MX) records
    - Ensures it isn't a suspicious domain by requiring multiple MX record

- **MTP Check:** Connects to the SMTP server of the domain and simulates sending an email to see if the recipient email exists.
- **Catch-All Domain Detection:**
    - Detects if a domain accepts any email address (i.e., is a catch-all)
    - Flags such domains as suspicious because the recipient may not actually exist even if the SMTP server accepts it

-- **Output Summary:**
The function returns a JSON object with the email validation results:
- `email`: Original email
- `result`: "Valid", "Invalid", "Suspicious", or "Risky"
- `did_you_mean`: Suggested correction (if any)
- `format_valid`: True/False (regex format check)
- `ping_success`: True/False (domain reachable)
- `mx_found`: True/False (MX records exist)
- `single_mx_record`: True/False (only one MX record)
- `smtp_deliverable`: True/False (SMTP accepts the address)
- `is_catch_all`: True/False (domain accepts all emails)

# Requirements

- Python 3.x
- External Python modules:
  - dns.resolver: Used for DNS lookups (install via pip install dnspython).
  - smtplib: Built-in module for SMTP communication.
  - platform: Built-in module for platform-specific commands.
  - re: Built-in module for regular expression operations.
 
# Usage

Install dependencies:
- pip install dnspython

Configuration:
- Replace the default sender email i.e. 'validuser@yourdomain.com' with a valid email id in the main.py file in function 'def validate_email_smtp(email, sender_email='validuser@yourdomain.com')'.
- To test the validity of an email, replace "email to test" with the email address you want to check in this line: email_to_check = "email to test".

The project is structured into three main components:

- ping.py: Contains the ping_domain function for pinging the domain.
- dns_lookup.py: Contains the get_mx_record function to fetch MX records for a domain.
- main.py: The main script that uses the above functions to validate email addresses.

Run the Script:
-  Run the main.py script as 'python main.py'.


# License

This project is licensed under the MIT License - see the LICENSE file for details.


# Acknowledgements

- Thanks to 'dnspython' for providing the DNS resolver.
- Thanks to Python's built-in 'smtplib' module for handling SMTP interactions
