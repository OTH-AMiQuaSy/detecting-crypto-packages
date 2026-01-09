# Detect cryptographic Packages using LLMs

This repository contains code and resources to detect cryptographic packages in Linux distributions using Large Language Models (LLMs). The project leverages LLMs to analyze package metadata and descriptions to identify packages that are relevant to cryptography.

This work is part of a larger effort to enhance the discovery and classification of cryptographic assets in software ecosystems and has been developed based on research conducted at [OTH Amberg/Weiden](https://www.oth-aw.de/) in the scope of the scientific project [AMiQuaSy](https://www.forschung-it-sicherheit-kommunikationssysteme.de/projekte/amiquasy).

**Important:** This approach will be integrated into a broader cryptographic asset discovery framework, to which this repository will refer once it becomes available.



## Prompt Templates

The prompt templates used for querying LLMs are located in the `llmpackagequery/query_templates/` directory. These templates are designed to extract relevant information about cryptographic packages effectively.

## Result JSON of LLM Queries

```json
{
  "package": "<package name>",
  "cryptographic_relevance": true | false,
  "justification": "2 short sentences explaining the reasoning. Mention relevant clues from name, description, or dependencies."
}
```

## Disclaimer

This project is intended for educational and research purposes only. The authors do not endorse or promote the use of cryptographic packages for malicious activities. Users are responsible for ensuring that their use of cryptographic software complies with all applicable laws and regulations.

Furthermore, the accuracy of LLMs in identifying cryptographic packages may vary, and users should independently verify the results before relying on them for critical applications.