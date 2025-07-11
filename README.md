# Messing with Google Docs

This is an experimental project where I explore using Python to interact with Google Docs, Google Drive, and Gemini's API (Google GenAI). The main idea is to take free-form user input, parse it into structured data using NLP, and generate customized invoices automatically.

## 🔧 What It Does

- Parses and formats free-form input into structured invoice data using Gemini's API.
- Duplicates a Google Docs invoice template via the Google Drive API.
- Populates and formats the new invoice using the Google Docs API.
- Simple CLI-style script that runs via `main.py`.

## 🚀 Technologies Used

- [Google GenAI (Gemini API)](https://ai.google.dev/)
- [Google Docs API](https://developers.google.com/docs/api)
- [Google Drive API](https://developers.google.com/drive)
- Python 3.10+

## 📦 Requirements

- Python 3.10+
- Install dependencies:

  ```bash
  pip install -r requirements.txt
