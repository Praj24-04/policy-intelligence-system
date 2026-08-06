import os
import sys
import json

# Setup import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.services.policy_generator import build_generation_context, validate_policy_document_content
from app.services.pdf_generator import generate_policy_pdf
import google.generativeai as genai

def main():
    country = "United States"
    sector = "ESG Policies"
    scope = "national"
    focus_areas = ["climate disclosure", "carbon tax", "board accountability"]

    print(f"--- Running generation pipeline for: Country={country}, Sector={sector} ---")

    # 1. Build generation context
    context = build_generation_context(country, sector)

    # 2. Get API key
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key:
        print("[ERROR] GOOGLE_API_KEY is not set in the environment. Cannot perform live generation.")
        sys.exit(1)

    genai.configure(api_key=api_key)

    system_prompt = """
You are an expert policy drafter with 20 years experience drafting legislation for international government bodies including the UN, EU, and national governments across Asia, Africa, and the Americas.

You produce structured, formal policy framework documents that follow international standards.
Your output is always:
- Specific to the country's legal and regulatory context
- Grounded in existing global best practices
- Written in formal legislative language
- Structured like real government policy documents
- Immediately usable as a working draft

Always respond with valid JSON only. 
No markdown, no explanation outside the JSON.
"""

    user_prompt = f"""
Generate a comprehensive {sector} policy framework document for {country}.

COUNTRY CONTEXT:
- Regulatory maturity: {context['maturity']}
- Existing sectors covered: {context['existing_sectors']}
- Priority needs: {context['priority_needs']}
- Existing {sector} policies: {context['existing_count']}

REFERENCE POLICIES FROM OTHER COUNTRIES:
{json.dumps(context['reference_policies'], indent=2)}

IDENTIFIED GAPS TO ADDRESS:
{json.dumps(list(context['gaps']), indent=2)}

SCOPE: {scope or 'national'}
FOCUS AREAS: {json.dumps(focus_areas or [])}

Generate a complete policy framework document.
Return ONLY this JSON structure:
{{
  "title": "formal policy document title",
  "short_title": "abbreviated name",
  "executive_summary": "2-3 paragraph summary",
  "preamble": "formal preamble text",
  "sections": [
    {{
      "number": "1",
      "title": "Definitions and Scope",
      "content": "full section text",
      "subsections": [
        {{
          "number": "1.1",
          "title": "subsection title",
          "content": "subsection text"
        }}
      ]
    }}
  ],
  "implementation_timeline": [
    {{
      "phase": "Phase 1",
      "duration": "0-6 months",
      "actions": ["action 1", "action 2"]
    }}
  ],
  "enforcement_mechanisms": "text",
  "monitoring_framework": "text",
  "references": [
    {{
      "id": "ref_1",
      "title": "policy title",
      "country": "country",
      "year": 2023,
      "source_url": "copy exact source_url from the reference context, or leave empty if none",
      "relevance": "why cited"
    }}
  ],
  "gap_analysis_addressed": [
    {{
      "gap": "gap identified",
      "how_addressed": "section reference"
    }}
  ]
}}

Required sections (include all):
1. Definitions and Scope
2. Guiding Principles  
3. Institutional Framework and Governance
4. Core Obligations and Requirements
5. Rights and Protections
6. Enforcement and Penalties
7. Implementation Roadmap
8. International Cooperation
9. Review and Amendment Procedures

Make section content substantive — minimum 150 words per section. Be specific to {country}.
Reference actual institutions that exist in {country}.

STRICT REFERENCE RULE:
- Do NOT invent or hallucinate any reference policies, titles, years, or links.
- Strictly choose your references from the provided list of "REFERENCE POLICIES FROM OTHER COUNTRIES".
- For each selected reference, copy the exact "title", "country", "year", and "source_url" metadata verbatim into the "references" array. Under no circumstances should you generate a "source_url" that was not present in the reference list.
"""

    # Export prompt sent
    prompt_file = "prompt_sent.txt"
    with open(prompt_file, "w", encoding="utf-8") as pf:
        pf.write("=== SYSTEM PROMPT ===\n")
        pf.write(system_prompt)
        pf.write("\n\n=== USER PROMPT ===\n")
        pf.write(user_prompt)
    print(f"[OK] Prompt sent exported to: {prompt_file}")

    print("Sending request to Gemini API...")
    try:
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_prompt
        )
        response = model.generate_content(
            contents=user_prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        raw_text = response.text.strip()
        model_used = model_name
    except Exception as e:
        print(f"[ERROR] Gemini generation failed: {e}")
        sys.exit(1)

    print(f"Response received successfully using {model_used}!")

    # Clean JSON
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
    raw_text = raw_text.strip()

    # Save raw JSON response
    response_file = "response_received.json"
    try:
        parsed_json = json.loads(raw_text)
        with open(response_file, "w", encoding="utf-8") as rf:
            json.dump(parsed_json, rf, indent=2)
        print(f"[OK] Parsed JSON response saved to: {response_file}")
    except Exception as je:
        print(f"[WARN] Response text is not valid JSON. Saving raw response. Error: {je}")
        with open(response_file, "w", encoding="utf-8") as rf:
            rf.write(raw_text)
        print(f"[OK] Raw text response saved to: {response_file}")
        sys.exit(1)

    # Validate document content
    is_valid, err_reason = validate_policy_document_content(sector, parsed_json)
    if not is_valid:
        print(f"[ERROR] Generated document failed content validation: {err_reason}")
    else:
        print("[OK] Document passed all content validation checks.")

    # 3. Create full policy payload
    import uuid
    from datetime import datetime
    
    policy_data = {
        "policy_id": str(uuid.uuid4()),
        "country": country,
        "sector": sector,
        "demo_mode": False,
        "generated_at": datetime.now().isoformat(),
        "document": parsed_json,
        "context_used": {
            "existing_policies_count": context["existing_count"],
            "reference_policies": context["reference_policies"],
            "gaps_identified": list(context["gaps"]),
            "demo_mode": False
        }
    }

    # Generate PDF
    pdf_file = "final_policy.pdf"
    try:
        pdf_bytes = generate_policy_pdf(policy_data)
        with open(pdf_file, "wb") as f:
            f.write(pdf_bytes)
        print(f"[OK] PDF compiled and saved to: {pdf_file}")
    except Exception as pe:
        print(f"[ERROR] Failed to compile PDF: {pe}")

if __name__ == "__main__":
    main()
