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

- **SMTP Check:**
    - Connects to the SMTP server to simulate sending an email.
    - Validates whether the recipient email address exists.
    - Tries port 25 first, and falls back to port 587 with STARTTLS if the connection fails.

- **Catch-All Domain Detection:**
    - Detects if a domain accepts any email address (i.e., is a catch-all)
    - Flags such domains as suspicious because the recipient may not actually exist, even if the SMTP server accepts it

- **Output Summary:**
The function returns a JSON object with the email validation results:
  - `email`: Original email that needs to be validated
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
  - dns.resolver: Used for DNS lookups.
  - smtplib: Built-in module for SMTP communication.
  - platform: Built-in module for platform-specific commands.
  - re: Built-in module for regular expression operations.
  - socket: Handles low-level network connections and timeouts.
  - platform: Used for OS-specific ping operations.
  - fuzzywuzzy: Used for fuzzy string matching in domain correction
  - scikit-learn: Used for ML-based domain suggestions using TF-IDF & cosine similarity
 
# Usage

Install dependencies:
- pip install dnspython fuzzywuzzy scikit-learn

Configuration:
- Replace the default sender email i.e. 'validuser@yourdomain.com' with a valid email id in the main.py file in function 'def validate_email_smtp(email, sender_email='validuser@yourdomain.com')'.
- To test the validity of an email, replace "email to test" with the email address you want to check in this line: email_to_check = "email to test".

The project is structured into different components:

- main.py: The main script that integrates all modules and performs full email validation, including SMTP verification.
- ping.py: Contains the ping_domain function for pinging the domain.
- dns_lookup.py: Contains the get_mx_record function to fetch MX records for a domain.
- suggestion.py: Provides domain correction suggestions using fuzzy matching.
- suspicious_email.py: Detects if a domain is configured as a catch-all mail server.
- smtp_validation.py: Handles SMTP-level verification by connecting to the domain’s MX server, performing a handshake, and issuing an RCPT TO command to test if the target email address is deliverable.

Run the Script:
-  Run the main.py script as 'python main.py'.
