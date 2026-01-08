Decide if this Fedora package is cryptography-related.

True if it uses or provides encryption, hashing, signing, key exchange, authentication, certificates, or secure randomness.  
If unclear, return false.

Output only JSON:
{{
  "package": "<package name>",
  "cryptographic_relevance": true or false,
  "justification": "1 short reason citing clues from name, description, or dependencies."
}}

Name: "{name}"
Desc: "{description}"
Deps: "{dependencies}"
