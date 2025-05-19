# Pseudonymizer Tool

A data anonymization tool that replaces sensitive information in text with pseudonyms while maintaining format and structure.

## Features
- Automatic detection of personal info (emails, phones, SSNs, etc)
- Named Entity Recognition (NER) with spaCy
- Customizable token mapping system
- Streamlit interface for interactive use
- Support for multiple entity types including:
  - PERSON, GPE, ORG, TIME, MONEY, FAC, NORP, WORK_OF_ART, EVENT

## Getting Started

1. Clone the repository
2. Create virtual environment
3. Install dependencies

```bash
./run.sh
```

##  Using the Interface
The app interface has three main panels:

Plain Text:
Paste or edit the text you want to pseudonymize here. Click "Run SpaCy and Update Pseu and Mapping" to detect sensitive data and generate pseudonyms.

Mapping:
View or edit the token mappings — the replacements used to pseudonymize the sensitive data. You can add new mappings or tweak existing ones.

Pseudonymized:
View the resulting text with sensitive info replaced by tokens. You can edit and update this area as well.

## Additional Features
Add custom entries to the mapping to pseudonymize specific text patterns.

Use the reset and clear buttons to start fresh.

The app maintains state between edits, allowing you to switch between original and pseudonymized views smoothly.

## Example
You can start with the default sample email text loaded in the Plain Text panel to explore the app features.