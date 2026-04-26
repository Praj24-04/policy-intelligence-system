import re

def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        import fitz  # pymupdf
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text_parts = []
        for page in doc:
            text = page.get_text("text")
            text_parts.append(text)
        doc.close()
        full_text = "\n".join(text_parts)
        full_text = re.sub(r'\n{3,}', '\n\n', full_text)
        full_text = re.sub(r'[ \t]{2,}', ' ', full_text)
        return full_text.strip()
    except Exception as e:
        raise ValueError(f"Could not extract text from PDF: {e}")


def extract_policy_metadata(text: str) -> dict:
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    title = lines[0] if lines else "Uploaded Policy"
    if len(title) > 120:
        title = title[:120] + "..."

    year = None
    year_match = re.search(r'\b(20\d{2})\b', text[:500])
    if year_match:
        year = int(year_match.group(1))

    common_policy_keywords = [
        "transparency", "accountability", "privacy", "security",
        "compliance", "risk", "data protection", "cybersecurity",
        "artificial intelligence", "governance", "human rights",
        "safety", "ethics", "regulation", "enforcement"
    ]

    text_lower = text.lower()
    detected_tags = [
        kw for kw in common_policy_keywords
        if kw in text_lower
    ][:6]

    return {
        "title": title,
        "year": year,
        "tags": detected_tags,
    }