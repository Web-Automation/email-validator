from fuzzywuzzy import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Commonly mistyped but valid email service domains
COMMON_DOMAINS = [
    "tax2win.in", "fisdom.com", "gmail.com", "yahoo.com", "outlook.com",
    "icloud.com", "protonmail.com", "live.com", "mail.com", "msn.com",
    "zoho.com", "gmx.com", "microsoft.com", "google.com", "nvidia.com", 
    "intel.com", "hotstar.com", "cleartax.in", "quicko.com", "taxbuddy.com", 
    "hotmail.com", "aol.com", "groww.com", "zerodha.com", "itrconsultant.in",
    "rediffmail.com"
]


"""****************************************************************************************************
* Function that suggests the closest known domain using fuzzy string matching.

* @param {string} user_domain - The domain part of the email entered by the user.
* @returns {string|null} - Returns the closest domain suggestion if the score ≥ 80, otherwise None.
******************************************************************************************************"""

def suggest_with_fuzzywuzzy(user_domain):
    best_match = None
    best_score = 0
    
    # Loop through each common domain to compare with the user-entered domain
    for domain in COMMON_DOMAINS:
        # Calculate Levenshtein similarity between the user domain and the common domain
        score = fuzz.ratio(user_domain, domain) 
        
        # If the current domain has a higher similarity score, update the best match and score
        if score > best_score:
            best_match = domain
            best_score = score
            
    # If the best score is above a threshold (80), return the best match, else return None
    return best_match if best_score >= 80 else None



"""*************************************************************************************************************
* Function that suggests a domain using machine learning via TF-IDF + cosine similarity.

* @param {string} user_domain - The domain part of the email entered by the user.
* @returns {string|null} - Returns the closest domain suggestion if similarity score ≥ 0.75, otherwise None.
*************************************************************************************************************"""

def suggest_with_ml(user_domain):
    
    user_domain = user_domain.strip().lower()
    # Combine user domain with known domains to form a comparison corpus
    corpus = COMMON_DOMAINS + [user_domain]
    
    # Convert characters into n-gram features for comparison
    vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(1, 3))
    tfidf = vectorizer.fit_transform(corpus)
    
    # Compare user domain to known domains using cosine similarity
    similarity = cosine_similarity(tfidf[-1], tfidf[:-1])
    best_index = similarity.argmax()
    best_score = similarity[0, best_index]
    return COMMON_DOMAINS[best_index] if best_score >= 0.6 else None


"""****************************************************************************************
* Function that suggests a corrected email if the domain appears to be mistyped.

* @param {string} email - Full email address to be checked for domain correction.
* @returns {string|null} - Suggested corrected email if domain is mistyped, otherwise None.
*****************************************************************************************"""

def suggest_email_correction(email):
    try:
        local_part, domain = email.lower().split('@')
        
        # Try fuzzywuzzy suggestion first
        fuzzy_suggestion = suggest_with_fuzzywuzzy(domain)
        
        # If fuzzy match fails, use ML-based approach
        if not fuzzy_suggestion:
            ml_suggestion = suggest_with_ml(domain)
        else:
            ml_suggestion = None  # No need to use ML if fuzzy matched
        
        # If a suggestion is found and it's different from the original domain, return corrected email
        suggestion = fuzzy_suggestion if fuzzy_suggestion else ml_suggestion
        if suggestion and suggestion != domain:
            return f"{local_part}@{suggestion}"
        return None
    except ValueError:
        # Return None if the email doesn't have a valid format (missing '@')
        return None