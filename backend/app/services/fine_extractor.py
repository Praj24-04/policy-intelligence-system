import re

PENALTY_KEYWORDS = [
    'fine', 'penalty', 'penalties', 'sanction', 'liable',
    'imprisonment', 'punishable', 'violation', 'non-compliance',
    'enforcement', 'maximum', 'up to', 'not exceeding', 'subject to'
]

IMPRISONMENT_PATTERN = re.compile(
    r'imprisonment\s+(?:of\s+)?(?:up\s+to\s+)?(\d+)\s*(year|month|day)s?',
    re.IGNORECASE
)

PERCENTAGE_PATTERN = re.compile(
    r'(\d+(?:\.\d+)?)\s*(?:percent|%)\s*of\s*(?:global\s*)?(?:annual\s*)?(?:turnover|revenue|income)',
    re.IGNORECASE
)

# Currency symbols with their codes
SYMBOL_MAP = {
    '€': 'EUR', '$': 'USD', '£': 'GBP',
    '¥': 'CNY/JPY', '₹': 'INR', 'R$': 'BRL',
    'S$': 'SGD', 'A$': 'AUD', 'CAD$': 'CAD',
}

# Word-based currency patterns (handles "50 million yuan", "50 million euros" etc.)
WORD_CURRENCY_PATTERNS = [
    # Symbol-based
    (r'(?:up\s+to\s+|fines?\s+of\s+|penalties?\s+of\s+|maximum\s+)?'
     r'([€$£¥₹])\s*(\d+(?:[.,]\d+)?)\s*(million|billion|thousand|crore|lakh)?',
     lambda m: (m.group(2), m.group(3) or '', SYMBOL_MAP.get(m.group(1), m.group(1)), m.group(1))),

    # R$ Brazilian Real
    (r'R\$\s*(\d+(?:[.,]\d+)?)\s*(million|billion|thousand)?',
     lambda m: (m.group(1), m.group(2) or '', 'BRL', 'R$')),

    # S$ Singapore Dollar
    (r'S\$\s*(\d+(?:[.,]\d+)?)\s*(million|billion|thousand)?',
     lambda m: (m.group(1), m.group(2) or '', 'SGD', 'S$')),

    # A$ Australian Dollar
    (r'A\$\s*(\d+(?:[.,]\d+)?)\s*(million|billion|thousand)?',
     lambda m: (m.group(1), m.group(2) or '', 'AUD', 'A$')),

    # Word-based: "50 million yuan/renminbi"
    (r'(\d+(?:[.,]\d+)?)\s*(million|billion|thousand)?\s*yuan',
     lambda m: (m.group(1), m.group(2) or '', 'CNY', '¥')),

    # Word-based: "50 million euros"
    (r'(\d+(?:[.,]\d+)?)\s*(million|billion|thousand)?\s*euros?',
     lambda m: (m.group(1), m.group(2) or '', 'EUR', '€')),

    # Word-based: "50 million dollars"
    (r'(\d+(?:[.,]\d+)?)\s*(million|billion|thousand)?\s*(?:US\s*)?dollars?',
     lambda m: (m.group(1), m.group(2) or '', 'USD', '$')),

    # Word-based: "50 million pounds"
    (r'(\d+(?:[.,]\d+)?)\s*(million|billion|thousand)?\s*pounds?',
     lambda m: (m.group(1), m.group(2) or '', 'GBP', '£')),

    # Word-based: "250 crore rupees"
    (r'(\d+(?:[.,]\d+)?)\s*(crore|lakh)s?\s*rupees?',
     lambda m: (m.group(1), m.group(2) or '', 'INR', '₹')),

    # Word-based: "10 million rand"
    (r'(\d+(?:[.,]\d+)?)\s*(million|billion)?\s*rand',
     lambda m: (m.group(1), m.group(2) or '', 'ZAR', 'R')),

    # Word-based: "100 million yen"
    (r'(\d+(?:[.,]\d+)?)\s*(million|billion)?\s*yen',
     lambda m: (m.group(1), m.group(2) or '', 'JPY', '¥')),

    # Word-based: "1 million Singapore dollars"
    (r'(\d+(?:[.,]\d+)?)\s*(million|billion)?\s*Singapore\s*dollars?',
     lambda m: (m.group(1), m.group(2) or '', 'SGD', 'S$')),

    # Word-based: "50 million Canadian dollars"
    (r'(\d+(?:[.,]\d+)?)\s*(million|billion)?\s*Canadian\s*dollars?',
     lambda m: (m.group(1), m.group(2) or '', 'CAD', 'CAD$')),

    # Word-based: "50 million Australian dollars"
    (r'(\d+(?:[.,]\d+)?)\s*(million|billion)?\s*Australian\s*dollars?',
     lambda m: (m.group(1), m.group(2) or '', 'AUD', 'A$')),

    # Generic large number with "fine/penalty" nearby — last resort
    (r'(?:fines?|penalties?)\s+(?:up\s+to\s+|of\s+)?(\d+(?:[.,]\d+)?)\s*(million|billion|thousand)',
     lambda m: (m.group(1), m.group(2) or '', 'UNK', '')),
]


def _normalize_amount(amount_str: str, multiplier: str, symbol: str) -> str:
    try:
        amount = float(amount_str.replace(',', ''))
        mult_map = {
            'billion': 1_000_000_000,
            'million': 1_000_000,
            'thousand': 1_000,
            'crore': 10_000_000,
            'lakh': 100_000,
        }
        if multiplier and multiplier.lower() in mult_map:
            amount *= mult_map[multiplier.lower()]
            if amount >= 1_000_000_000:
                return f"{symbol}{amount/1_000_000_000:.1f} billion"
            elif amount >= 1_000_000:
                return f"{symbol}{amount/1_000_000:.0f} million"
            elif amount >= 1_000:
                return f"{symbol}{amount/1_000:.0f} thousand"
        return f"{symbol}{amount:,.0f}"
    except Exception:
        return f"{symbol}{amount_str}"


def extract_fines(content: str) -> dict:
    if not content:
        return None

    text_lower = content.lower()

    # Must have penalty context
    has_penalty = any(kw in text_lower for kw in PENALTY_KEYWORDS)
    if not has_penalty:
        return None

    fines_found = []
    percentage_fines = []
    seen_amounts = set()

    # Extract percentage fines
    for match in PERCENTAGE_PATTERN.finditer(content):
        pct = match.group(1)
        ctx_start = max(0, match.start() - 100)
        ctx = content[ctx_start:match.end() + 50].strip()
        percentage_fines.append({
            "percentage": f"{pct}%",
            "context": ctx
        })

    # Extract monetary fines
    for pattern, extractor in WORD_CURRENCY_PATTERNS:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            try:
                amount_str, multiplier, currency, symbol = extractor(match)
                if not amount_str:
                    continue

                # Get context around match
                ctx_start = max(0, match.start() - 100)
                ctx_end = min(len(content), match.end() + 100)
                ctx = content[ctx_start:ctx_end].strip()
                ctx_lower = ctx.lower()

                # Only include if penalty context nearby
                if not any(kw in ctx_lower for kw in PENALTY_KEYWORDS):
                    continue

                display = _normalize_amount(amount_str, multiplier, symbol)

                # Deduplicate
                if display in seen_amounts:
                    continue
                seen_amounts.add(display)

                fines_found.append({
                    "amount": display,
                    "currency": currency,
                    "context_snippet": ctx[:150] + "..." if len(ctx) > 150 else ctx
                })
            except Exception:
                continue

    # Extract imprisonment
    imprisonment = None
    imp_match = IMPRISONMENT_PATTERN.search(content)
    if imp_match:
        imprisonment = f"Up to {imp_match.group(1)} {imp_match.group(2)}(s) imprisonment"

    if not fines_found and not percentage_fines and not imprisonment:
        return None

    # Build summary
    parts = []
    if fines_found:
        amounts = [f["amount"] for f in fines_found[:2]]
        parts.append(f"Fines up to {' or '.join(amounts)}")
    if percentage_fines:
        pcts = [f["percentage"] for f in percentage_fines[:2]]
        parts.append(f"{' or '.join(pcts)} of annual revenue")
    if imprisonment:
        parts.append(imprisonment)

    return {
        "has_fines": True,
        "monetary_fines": fines_found[:3],
        "percentage_fines": percentage_fines[:2],
        "imprisonment": imprisonment,
        "summary": " · ".join(parts) if parts else "Penalties apply"
    }