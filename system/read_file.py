import chardet
import fitz  # type: ignore
from ai.nlp import ask_gpt  # Make sure this import works in your project


def read_file(filepath):
    try:
        if filepath.lower().endswith(".pdf"):
            return read_pdf(filepath)
        
        with open(filepath, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result.get("encoding") or "ISO-8859-1"

        with open(filepath, 'r', encoding=encoding, errors='replace') as f:
            return f.read()

    except Exception as e:
        return f"Error reading file: {e}"


def read_pdf(filepath):
    try:
        doc = fitz.open(filepath)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text if text else "The PDF file doesn't contain readable text."
    except Exception as e:
        return f"Error reading PDF file: {e}"


def read_and_summarize_file(filepath):
    content = read_file(filepath)

    if not content or "Error" in content:
        return content

    content = content.strip()
    if not content:
        return "The file is empty."

    # Limit to first 5000 characters for GPT input
    content = content[:5000]
    prompt = f"Summarize the following content:\n\n{content}"

    try:
        summary = ask_gpt(prompt)
        return summary
    except Exception as e:
        return f"Failed to summarize the file: {e}"
