# email-validator
This Python project provides an email validation tool that verifies the existence of an email address by performing several checks:

- Format Check: Validates if the email follows the correct format.
- Domain Suggestion: If the domain part of the email appears mistyped (e.g., "gmil.com"), it suggests a correction (e.g., "gmail.com") using fuzzy matching and machine learning techniques.
- Ping Check: Verifies if the domain of the email address responds to ping requests.
- MX Record Lookup: Checks if the domain has valid Mail Exchange (MX) records.
- SMTP Check: Connects to the SMTP server of the domain and simulates sending an email to see if the recipient email exists.
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
