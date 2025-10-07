import uuid


"""***********************************************************************************************************
* Function to detect if a domain is configured as a catch-all mail server. 
* A catch-all server accepts emails sent to any address at the domain, even if the email address doesn't exist.

* @param {string} domain - The domain to be tested for catch-all configuration.
* @param {string} sender_email - A valid sender email to use during the SMTP handshake.
* @returns {bool} - Returns True if the domain behaves like a catch-all, False otherwise.
************************************************************************************************************"""
def is_catch_all_domain(server, domain):
    try:
        # Generate a random, likely non-existent email address on the domain
        test_email = f"{uuid.uuid4().hex[:10]}@{domain}"
        # Test sending to the generated (fake) recipient
        code, _ = server.rcpt(test_email)

        if code == 250:
            return True  # Server accepts unknown address = likely catch-all
    except Exception as e:
        print(f"Unexpected error: {e}")
    return False  # None of the MX records accepted the fake address
