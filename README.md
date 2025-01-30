# email-validator
This Python project provides an email validation tool that verifies the existence of an email address by performing several checks:

- Format Check: Validates if the email follows the correct format.
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
