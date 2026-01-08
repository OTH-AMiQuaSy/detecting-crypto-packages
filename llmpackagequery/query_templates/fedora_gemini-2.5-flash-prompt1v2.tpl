You are analyzing a Fedora package.

Goal:
Decide if the package is related to cryptography in any way.

"Cryptographic relevance" means the package:
- Implements, uses, or helps cryptographic functions such as encryption, decryption, hashing, signing, key exchange, authentication, certificate handling, or secure random number generation.

If there is no clear sign of cryptographic use, return false.

Output only valid JSON:
{{
  "package": "<package name>",
  "cryptographic_relevance": true | false,
  "justification": "2 short sentences explaining the reasoning. Mention relevant clues from name, description, or dependencies."
}}

Package name: "{name}"
Description: "{description}"
Dependencies: "{dependencies}"
