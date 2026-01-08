You are given a Fedora package.
Your task is to determine whether the package is relevant in the context of cryptography, i.e. utilizes cryptographic building blocks. Thus if the package clearly implements, uses, or supports cryptography (encryption, decryption, hashing, signing, key exchange, authentication, certificates, or secure random numbers)
Respond strictly in the following JSON format:
{{
  "package": "<package>",
  "cryptographic_relevance": <true | false>,
  "justification": "2-3 sentences justification of your response"
}}

Now determine the cryptographic relevance of package: "{name}" with description: "{description}" and dependencies: "{dependencies}"