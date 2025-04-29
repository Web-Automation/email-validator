# email-validator
This Python project provides an email validation tool that verifies the existence of an email address by performing several checks:

- Format Check: Validates if the email follows the correct syntax using regular expressions.
- Domain Suggestion: If the domain part of the email appears mistyped (e.g., "gmil.com"), the tool suggests a correction (e.g., "gmail.com").  
  This is implemented using:
   - **Fuzzy string matching** (via the `fuzzywuzzy` library)
   - **Machine learning-based similarity**, using **n-gram character features** with `TfidfVectorizer` and **cosine similarity** from `scikit-learn`.

- Ping Check: Pings the domain to confirm it is reachable and not a disposable or dead domain.
- MX Record Lookup:
    - Checks if the domain has valid Mail Exchange (MX) records.
    - Validates that the domain has Mail Exchange (MX) records
    - Ensures it isn't a suspicious domain by requiring multiple MX record

- SMTP Check: Connects to the SMTP server of the domain and simulates sending an email to see if the recipient email exists.
- Catch-All Domain Detection:
    - Detects if a domain accepts any email address (i.e., is a catch-all)
    - Flags such domains as suspicious because the recipient may not actually exist even if the SMTP server accepts it

The project is designed as a set of modular Python functions that can be reused for different use cases. It works by first validating the email format, then checking if the domain responds to pings, and finally verifying if the domain has a valid MX record and SMTP server that accepts the recipient email.

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
