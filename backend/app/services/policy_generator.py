import os
import json
import uuid
from datetime import datetime
import google.generativeai as genai
from app.database import get_connection
from app.ml.vector_store import semantic_search
from data.country_profiles import COUNTRY_PROFILES
from app.services.sector_templates import SECTOR_FALLBACK_TEMPLATES
from app.config import GOOGLE_API_KEY, LLM_PROVIDER, GEMINI_MODEL

# Configure Gemini if GOOGLE_API_KEY is configured
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

def lookup_policy_url_in_db(title: str, country: str = None) -> str:
    """
    Looks up a policy in the database by title and country to find its true source_url.
    """
    if not title:
        return None
    try:
        conn = get_connection()
        try:
            # 1. Exact match by title and country
            if country:
                row = conn.execute(
                    "SELECT source_url FROM policies WHERE LOWER(title) = %s AND LOWER(country) = %s",
                    (title.lower().strip(), country.lower().strip())
                ).fetchone()
                if row and row["source_url"]:
                    return row["source_url"]
            
            # 2. Exact match by title
            row = conn.execute(
                "SELECT source_url FROM policies WHERE LOWER(title) = %s",
                (title.lower().strip(),)
            ).fetchone()
            if row and row["source_url"]:
                return row["source_url"]

            # 3. Substring match by title
            row = conn.execute(
                "SELECT source_url FROM policies WHERE LOWER(title) LIKE %s",
                (f"%{title.lower().strip()}%",)
            ).fetchone()
            if row and row["source_url"]:
                return row["source_url"]
        finally:
            conn.close()
    except Exception as e:
        print(f"[WARN] Database lookup failed for title '{title}': {e}")
    return None

def sanitize_source_url(url: str, title: str, country: str) -> str:
    url = (url or "").strip()
    url_lower = url.lower()
    
    # Check for known broken URLs or redirect patterns
    if "estrategia-nacional-de-seguranca-cibernetica" in url_lower or "copy_of_dsic" in url_lower or "dsi/estrategia" in url_lower:
        return "https://www.gov.br/gsi/pt-br/seguranca-da-informacao-e-cibernetica"
    
    if "ebia.pdf" in url_lower or "ebia-documento_referencia" in url_lower or "transformacaodigital/arquivosdigital" in url_lower:
        return "https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/transformacaodigital/inteligencia-artificial"

    # If the URL is empty or invalid (e.g. doesn't start with http), fall back to google search
    if not url or not (url.startswith("http://") or url.startswith("https://")):
        import urllib.parse
        q = urllib.parse.quote_plus(f"{title} {country} policy framework")
        return f"https://www.google.com/search?q={q}"
        
    return url

def post_process_generated_document(result: dict, context: dict) -> dict:
    """
    Sanitizes reference links in the generated document to prevent LLM hallucinations.
    """
    if not result or "document" not in result:
        return result
        
    document = result["document"]
    if not isinstance(document, dict) or "references" not in document:
        return result
        
    refs = document["references"]
    if not isinstance(refs, list):
        return result
        
    context_refs = context.get("reference_policies", [])
    
    for ref in refs:
        if not isinstance(ref, dict):
            continue
            
        gen_title = ref.get("title", "").lower().strip()
        gen_country = ref.get("country", "").lower().strip()
        
        # Try to match to one of the 5 reference policies in context
        best_match = None
        for cr in context_refs:
            cr_title = cr.get("title", "").lower().strip()
            if gen_title == cr_title or cr_title in gen_title or gen_title in cr_title:
                best_match = cr
                break
                
        if not best_match:
            for cr in context_refs:
                cr_country = cr.get("country", "").lower().strip()
                if gen_country == cr_country:
                    best_match = cr
                    break
                    
        # Determine raw URL from matched reference or database lookup
        raw_url = ""
        if best_match:
            raw_url = best_match.get("source_url") or ""
            # Synchronize title and country with the database record
            ref["title"] = best_match.get("title")
            ref["country"] = best_match.get("country")
        else:
            # Query full database to see if we can find this policy
            db_url = lookup_policy_url_in_db(ref.get("title"), ref.get("country"))
            if db_url:
                raw_url = db_url
            else:
                raw_url = ref.get("source_url") or ""
                
        # Clean and sanitize the URL using helper
        ref["source_url"] = sanitize_source_url(raw_url, ref.get("title", ""), ref.get("country", ""))
        
    return result


def _parse_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return []
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else [parsed]
        except json.JSONDecodeError:
            return [item.strip() for item in value.split(",") if item.strip()]
    return []

def build_generation_context(country: str, sector: str) -> dict:
    """
    Builds a rich context for the country and sector, querying the database and vector store
    to construct intelligence details for the generator.
    """
    # 1. Retrieve Country Profile metadata
    profile = COUNTRY_PROFILES.get(country, {})
    
    # 2. Get existing policies for this country + sector from PostgreSQL
    conn = get_connection()
    existing_policies = []
    try:
        cur = conn.execute(
            "SELECT id, title, tags, content FROM policies WHERE country = %s AND sector = %s",
            (country, sector)
        )
        rows = cur.fetchall()
        for row in rows:
            existing_policies.append({
                "id": row["id"],
                "title": row["title"],
                "tags": _parse_list(row["tags"]),
                "content": row["content"]
            })
    except Exception as e:
        print(f"[ERROR] Failed to query existing policies for context: {e}")
    finally:
        conn.close()

    # 3. Retrieve Top 10 reference policies from OTHER countries in same sector
    reference_policies = []
    retrieval_metadata = {
        "sector": sector,
        "documents_retrieved": 0,
        "unique_documents": 0,
        "top_similarity": 0.0,
        "countries_referenced": []
    }
    
    try:
        search_query = f"{sector} policy framework {country}"
        raw_matches = semantic_search(
            query_text=search_query,
            n=10,
            sector_filter=sector,
            exclude_country=country
        )
        
        # Deduplicate references by title (keeping highest scoring)
        seen_titles = set()
        deduplicated_matches = []
        for m in raw_matches:
            title_clean = m["title"].lower().strip()
            if title_clean not in seen_titles:
                seen_titles.add(title_clean)
                deduplicated_matches.append(m)
                
        # Take the top 5 distinct/diverse ones
        selected_matches = deduplicated_matches[:5]
        
        conn = get_connection()
        try:
            for m in selected_matches:
                policy_id = m["id"]
                # Query postgres to get the true source_url for this reference
                row = conn.execute("SELECT source_url FROM policies WHERE id = %s", (policy_id,)).fetchone()
                src_url = row["source_url"] if (row and row["source_url"]) else ""
                
                reference_policies.append({
                    "id": m["id"],
                    "title": m["title"],
                    "country": m["country"],
                    "year": m.get("year", 2023),
                    "source_url": src_url,
                    "tags": _parse_list(m.get("tags", [])) if "tags" in m else ["security", "framework", "compliance"],
                    "relevance": m.get("relevance", "")
                })
        finally:
            conn.close()
            
        # Compile diagnostics
        retrieved_count = len(raw_matches)
        unique_count = len(seen_titles)
        top_sim = raw_matches[0]["approx_similarity"] if raw_matches else 0.0
        countries_ref = list(set(m["country"] for m in selected_matches if m.get("country")))
        
        retrieval_metadata = {
            "sector": sector,
            "documents_retrieved": retrieved_count,
            "unique_documents": unique_count,
            "top_similarity": round(top_sim, 4),
            "countries_referenced": countries_ref
        }
        
        print(f"\n[RETRIEVAL AUDIT]")
        print(f"Sector: {sector}")
        print(f"Retrieved: {retrieved_count} docs")
        print(f"Unique: {unique_count} docs")
        print(f"Top similarity: {round(top_sim, 4)}\n")
        
    except Exception as e:
        print(f"[ERROR] Failed to query semantic references for context: {e}")

    # 4. Identify Gaps
    # Collect tags from both reference and existing policies
    reference_tags = set()
    for ref in reference_policies:
        for tag in ref["tags"]:
            reference_tags.add(tag.strip().lower())

    existing_tags = set()
    for ex in existing_policies:
        for tag in ex["tags"]:
            existing_tags.add(tag.strip().lower())

    gaps = reference_tags - existing_tags
    # Fallback to some default gaps if sets are empty
    if not gaps:
        sector_lower = sector.lower()
        if "esg" in sector_lower:
            gaps = {"climate disclosure", "sustainability reporting", "board accountability", "supply chain transparency", "emissions reporting"}
        elif "posh" in sector_lower:
            gaps = {"internal complaints committee", "investigation procedure", "anti-retaliation protection"}
        elif "financial" in sector_lower:
            gaps = {"capital adequacy", "consumer protection", "risk controls"}
        elif "healthcare" in sector_lower:
            gaps = {"clinical validation", "patient safety", "auditability"}
        elif "privacy" in sector_lower:
            gaps = {"consent management", "data subject rights", "data fiduciary oversight", "breach notifications"}
        elif "cyber" in sector_lower:
            gaps = {"incident response plans", "supply chain oversight", "critical infrastructure baselines"}
        elif "ai" in sector_lower:
            gaps = {"algorithmic transparency", "human-in-the-loop oversight", "model risk assessments"}
        elif "iot" in sector_lower or "robot" in sector_lower:
            gaps = {"embedded systems security", "physical safety overrides", "firmware update validation"}
        else:
            gaps = {"compliance auditing", "oversight mechanisms", "reporting requirements"}

    # 5. Build maturity context
    maturity = profile.get("regulatory_maturity", "developing")
    priority_needs = profile.get("priority_needs", [])
    existing_sectors = profile.get("existing_sectors", [])

    return {
        "country": country,
        "sector": sector,
        "maturity": maturity,
        "priority_needs": priority_needs,
        "existing_sectors": existing_sectors,
        "existing_count": len(existing_policies),
        "existing_policies": existing_policies,
        "reference_policies": reference_policies,
        "gaps": list(gaps),
        "retrieval_metadata": retrieval_metadata
    }

def get_sector_institutions(country: str, sector: str) -> dict:
    default = {
        "authority": f"National Joint Council for {sector} / Department of Digital Services",
        "cert": "National Cyber Defense Centre (NCDC)",
        "appellate": "National Administrative Tribunal",
        "commission": f"Department of Technology & Standards"
    }
    
    sector_lower = sector.lower()
    
    # 1. Tech / AI Governance / Healthcare AI / IoT
    if any(k in sector_lower for k in ["ai", "robot", "iot", "governance"]):
        if country == "United States":
            return {
                "authority": "Federal Artificial Intelligence Council (FAIC) / National Institute of Standards and Technology (NIST)",
                "cert": "CISA (Cybersecurity and Infrastructure Security Agency)",
                "appellate": "Federal Courts of Appeals",
                "commission": "Federal Trade Commission (FTC)"
            }
        elif country == "India":
            return {
                "authority": "National AI Regulatory Authority (NAIRA) / Ministry of Electronics and Information Technology (MeitY)",
                "cert": "CERT-In (Indian Computer Emergency Response Team)",
                "appellate": "Telecom Disputes Settlement and Appellate Tribunal (TDSAT)",
                "commission": "National AI Commission"
            }
        elif country == "European Union":
            return {
                "authority": "European Artificial Intelligence Board (EAIB)",
                "cert": "ENISA (European Union Agency for Cybersecurity)",
                "appellate": "Court of Justice of the European Union",
                "commission": "European Commission"
            }
            
    # 2. Cybersecurity / Data Privacy
    elif any(k in sector_lower for k in ["cyber", "privacy", "data"]):
        if country == "United States":
            return {
                "authority": "Federal Trade Commission (FTC) / Cybersecurity and Infrastructure Security Agency (CISA)",
                "cert": "CISA (Cybersecurity and Infrastructure Security Agency)",
                "appellate": "Federal Courts of Appeals",
                "commission": "Federal Trade Commission (FTC)"
            }
        elif country == "India":
            return {
                "authority": "Data Protection Board of India (DPBI) / Ministry of Electronics and Information Technology (MeitY)",
                "cert": "CERT-In (Indian Computer Emergency Response Team)",
                "appellate": "Telecom Disputes Settlement and Appellate Tribunal (TDSAT)",
                "commission": "Ministry of Electronics and Information Technology (MeitY)"
            }
        elif country == "European Union":
            return {
                "authority": "European Data Protection Board (EDPB)",
                "cert": "ENISA (European Union Agency for Cybersecurity)",
                "appellate": "Court of Justice of the European Union",
                "commission": "European Commission"
            }
            
    # 3. ESG Policies / Financial Regulation
    elif any(k in sector_lower for k in ["esg", "financial", "regulation", "sustainability"]):
        if country == "United States":
            return {
                "authority": "Securities and Exchange Commission (SEC) / Environmental Protection Agency (EPA)",
                "cert": "SEC Enforcement Division",
                "appellate": "Federal District Courts",
                "commission": "Securities and Exchange Commission (SEC)"
            }
        elif country == "India":
            return {
                "authority": "Securities and Exchange Board of India (SEBI) / Ministry of Finance",
                "cert": "SEBI ESG Advisory Committee",
                "appellate": "Securities Appellate Tribunal (SAT)",
                "commission": "Securities and Exchange Board of India (SEBI)"
            }
        elif country == "European Union":
            return {
                "authority": "European Securities and Markets Authority (ESMA)",
                "cert": "ESMA Sustainability Division",
                "appellate": "Court of Justice of the European Union",
                "commission": "European Commission DG Financial Stability"
            }
            
    # 4. POSH Policies
    elif "posh" in sector_lower or "harassment" in sector_lower:
        if country == "United States":
            return {
                "authority": "Equal Employment Opportunity Commission (EEOC) / Department of Labor",
                "cert": "EEOC Enforcement Division",
                "appellate": "Federal Appeals Courts",
                "commission": "Equal Employment Opportunity Commission (EEOC)"
            }
        elif country == "India":
            return {
                "authority": "Ministry of Women and Child Development / Local Complaints Committee (LCC)",
                "cert": "District Officer / Internal Complaints Committee (ICC)",
                "appellate": "Industrial Tribunal / Central Administrative Tribunal",
                "commission": "Ministry of Women and Child Development"
            }
        elif country == "European Union":
            return {
                "authority": "European Institute for Gender Equality (EIGE) / DG Employment",
                "cert": "National Equality Bodies",
                "appellate": "Court of Justice of the European Union",
                "commission": "European Commission"
            }
            
    return default

def validate_policy_document_content(sector: str, doc: dict) -> tuple[bool, str]:
    """
    Validates that the generated policy framework text adheres to sector-specific constraints.
    Returns (is_valid, error_reason).
    """
    import json
    doc_str = json.dumps(doc).lower()
    sector_lower = sector.lower()
    
    if "esg" in sector_lower:
        required = ["sustainability", "environmental", "governance", "disclosure", "reporting"]
        prohibited = ["high-risk ai", "algorithmic impact", "foundation models", "ai system"]
        
        has_req = any(req in doc_str for req in required)
        if not has_req:
            return False, "ESG Policies document lacks required sustainability/environmental keywords."
            
        has_proh = any(proh in doc_str for proh in prohibited)
        if has_proh:
            return False, "ESG Policies document contains prohibited AI-governance terminology."
            
    elif "posh" in sector_lower:
        required = ["harassment", "workplace", "complaints", "committee", "redressal"]
        prohibited = ["algorithmic", "cybersecurity", "gdpr", "artificial intelligence"]
        
        has_req = any(req in doc_str for req in required)
        if not has_req:
            return False, "POSH Policies document lacks required workplace harassment prevention keywords."
            
        has_proh = any(proh in doc_str for proh in prohibited)
        if has_proh:
            return False, "POSH Policies document contains prohibited tech/privacy terminology."
            
    return True, ""

def _generate_high_fidelity_mock(country: str, sector: str, scope: str, focus_areas: list, context: dict) -> dict:
    """
    Generates a beautifully tailored, high-fidelity legislative framework template mock 
    based on the requested sector, so the platform remains completely interactive and functional.
    """
    # Normalize sector matching
    matched_sector = "AI Governance"
    for s_key in SECTOR_FALLBACK_TEMPLATES.keys():
        if s_key.lower() == sector.lower() or s_key.lower().replace(" policies", "") == sector.lower().replace(" policies", ""):
            matched_sector = s_key
            break
            
    template = SECTOR_FALLBACK_TEMPLATES[matched_sector]
    inst = get_sector_institutions(country, sector)
    
    # Process and normalize focus areas
    clean_focus_areas = []
    if isinstance(focus_areas, list):
        for fa in focus_areas:
            if isinstance(fa, str) and fa.strip():
                clean_focus_areas.append(fa.strip())
    elif isinstance(focus_areas, str):
        clean_focus_areas = [item.strip() for item in focus_areas.split(",") if item.strip()]

    # Weave focus areas dynamically into the text
    if clean_focus_areas:
        focus_str = ", ".join(clean_focus_areas)
        focus_emphasis_summary = f" In response to designated national priorities, this framework places particular regulatory emphasis on governing and strengthening capabilities in the areas of {focus_str}."
        focus_definitions = f" Specific definitions and compliance metrics are established for technologies and operational vectors associated with {focus_str}."
        focus_obligations = f" Under the core obligations, registered entities must integrate explicit mitigation strategies and security baselines addressing {focus_str}."
        focus_roadmap = f" Dedicated standards and enforcement protocols for {focus_str} will be finalized within this transition horizon."
        
        focus_sub_applicability = f" deployments, with dedicated oversight rules for {focus_str}."
        focus_sub_obligations = f", documenting explicit safeguards and compliance plans for {focus_str}."
        focus_sub_roadmap = f" specifically addressing best practices in {focus_str}."
    else:
        focus_emphasis_summary = ""
        focus_definitions = ""
        focus_obligations = ""
        focus_roadmap = ""
        focus_sub_applicability = "."
        focus_sub_obligations = "."
        focus_sub_roadmap = "."

    # Format the template fields using country and institution mappings
    formatted_sections = []
    for sec in template["sections"]:
        formatted_subsections = []
        for sub in sec["subsections"]:
            sub_content = sub["content"].format(
                country=country,
                authority=inst["authority"],
                cert=inst["cert"],
                appellate=inst["appellate"],
                commission=inst["commission"]
            )
            # Weave in focus area logic dynamically
            if sec["number"] == "1":
                sub_content += focus_sub_applicability
            elif sec["number"] == "4":
                sub_content += focus_sub_obligations
            elif sec["number"] == "7":
                sub_content += focus_sub_roadmap
                
            formatted_subsections.append({
                "number": sub["number"],
                "title": sub["title"],
                "content": sub_content
            })
            
        sec_content = sec["content"].format(
            country=country,
            authority=inst["authority"],
            cert=inst["cert"],
            appellate=inst["appellate"],
            commission=inst["commission"]
        )
        # Weave in focus area logic dynamically to sections
        if sec["number"] == "1":
            sec_content += focus_definitions
        elif sec["number"] == "4":
            sec_content += focus_obligations
        elif sec["number"] == "7":
            sec_content += focus_roadmap
            
        formatted_sections.append({
            "number": sec["number"],
            "title": sec["title"],
            "content": sec_content,
            "subsections": formatted_subsections
        })

    # Custom tailored references
    refs = []
    for idx, r_pol in enumerate(context.get("reference_policies", [])):
        refs.append({
            "id": f"ref_{idx+1}",
            "title": r_pol["title"],
            "country": r_pol["country"],
            "year": r_pol["year"],
            "source_url": r_pol.get("source_url") or "",
            "relevance": f"Blueprints key compliance baseline and {sector.lower()} safety benchmarks used to draft Sections {idx%4 + 1} and {idx%4 + 5}."
        })
        
    if not refs:
        refs = [
            {
                "id": "ref_1",
                "title": f"Global {sector} Cooperation Agreement",
                "country": "OECD",
                "year": 2024,
                "source_url": f"https://www.google.com/search?q={sector.replace(' ', '+')}+global+standards",
                "relevance": "Underpins transparent reporting models and core legislative safety clauses."
            }
        ]

    # Gaps addressed list
    gap_addressed = []
    for gap in context.get("gaps", []):
        gap_addressed.append({
            "gap": gap,
            "how_addressed": f"Remediated via Section {len(gap_addressed)%4 + 3} audit requirements."
        })

    return {
        "title": template["title"].format(country_upper=country.upper()),
        "short_title": template["short_title"].format(country=country),
        "executive_summary": template["executive_summary"].format(country=country) + focus_emphasis_summary,
        "preamble": template["preamble"].format(country=country),
        "sections": formatted_sections,
        "implementation_timeline": [
            {
                "phase": "Phase 1: Institution Setup",
                "duration": "0-6 months",
                "actions": [
                    f"Establish the {inst['authority']}",
                    "Assemble the stakeholder advisory panel",
                    "Draft initial compliance registry guidelines"
                ]
            },
            {
                "phase": "Phase 2: Registry Opening",
                "duration": "6-12 months",
                "actions": [
                    "Launch compliance developer sandbox portal",
                    "Conduct voluntary registration drives for startups",
                    "Publish technical standard baselines"
                ]
            },
            {
                "phase": "Phase 3: Full Enforcement",
                "duration": "12-24 months",
                "actions": [
                    "Activate mandatory audit compliance checks",
                    "Establish appellate tribunals for citizen dispute reviews",
                    "Enable cross-border sharing links with international peers"
                ]
            }
        ],
        "enforcement_mechanisms": template["enforcement_mechanisms"].format(authority=inst["authority"]),
        "monitoring_framework": template["monitoring_framework"],
        "references": refs,
        "gap_analysis_addressed": gap_addressed
    }

def resolve_provider():
    from app.config import LLM_PROVIDER, GOOGLE_API_KEY
    prov = (LLM_PROVIDER or "auto").lower().strip()
    if prov == "auto":
        if GOOGLE_API_KEY:
            return "gemini", GOOGLE_API_KEY
        else:
            return "mock", ""
    elif prov == "gemini":
        if GOOGLE_API_KEY:
            return "gemini", GOOGLE_API_KEY
        else:
            return "mock", ""
    else:
        return "mock", ""

def generate_policy_document(
    country: str,
    sector: str,
    scope: str = None,
    focus_areas: list = None
) -> dict:
    """
    Constructs contextual prompts and uses Gemini or mock fallback to generate a structured legislative document draft.
    """
    start_time = datetime.now()
    context = build_generation_context(country, sector)
    provider_name, api_key_val = resolve_provider()
    
    print(f"[INFO] Resolved LLM provider: {provider_name}")
    
    # 1. MOCK PROVIDER FLOW
    if provider_name == "mock":
        print(f"[GENERATION AUDIT] Provider: mock, Model: sector_template, Demo Mode: True, Fallback mock generation executed: True")
        mock_doc = _generate_high_fidelity_mock(country, sector, scope, focus_areas, context)
        gen_time = (datetime.now() - start_time).total_seconds()
        
        # Ensure generation_metadata is present inside the document object
        metadata = {
            "provider": "mock",
            "model": "sector_template",
            "demo_mode": True,
            "country": country,
            "sector": sector,
            "generation_timestamp": datetime.now().isoformat(),
            "generation_time_seconds": round(gen_time, 2),
            "prompt_length": 0,
            "response_length": len(json.dumps(mock_doc)),
            "validation_retry_count": 0
        }
        mock_doc["generation_metadata"] = metadata
        
        res = {
            "policy_id": str(uuid.uuid4()),
            "country": country,
            "sector": sector,
            "demo_mode": True,
            "generated_at": datetime.now().isoformat(),
            "generation_metadata": metadata,
            "document": mock_doc,
            "context_used": {
                "existing_policies_count": context["existing_count"],
                "reference_policies": context["reference_policies"],
                "gaps_identified": list(context["gaps"]),
                "demo_mode": True
            }
        }
        
        # Save prompt and response files
        try:
            safe_country = country.replace(" ", "_")
            safe_sector = sector.replace(" ", "_")
            scratch_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scratch"))
            os.makedirs(scratch_dir, exist_ok=True)
            
            prompt_content = f"No prompt sent (Mock provider active for sector {sector} and country {country})"
            with open(os.path.join(scratch_dir, "prompt_sent.txt"), "w", encoding="utf-8") as f:
                f.write(prompt_content)
            with open(os.path.join(scratch_dir, f"{safe_country}_{safe_sector}_prompt_sent.txt"), "w", encoding="utf-8") as f:
                f.write(prompt_content)
                
            resp_content = json.dumps(res, indent=2)
            with open(os.path.join(scratch_dir, "response_received.json"), "w", encoding="utf-8") as f:
                f.write(resp_content)
            with open(os.path.join(scratch_dir, f"{safe_country}_{safe_sector}_response_received.json"), "w", encoding="utf-8") as f:
                f.write(resp_content)
        except Exception as e:
            print(f"[WARN] Failed to write mock audit logs to disk: {e}")
            
        return post_process_generated_document(res, context)

    # Common prompts
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

    max_attempts = 2
    last_error = None
    
    for attempt in range(max_attempts):
        try:
            # 2. GEMINI LLM FLOW
            if provider_name == "gemini":
                model_name = GEMINI_MODEL
                print(f"[GENERATION AUDIT] Provider: gemini, Model: {model_name}, Demo Mode: False, Fallback mock generation executed: False")
                
                # Setup model
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=system_prompt
                )
                
                # Save prompt sent
                try:
                    safe_country = country.replace(" ", "_")
                    safe_sector = sector.replace(" ", "_")
                    scratch_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scratch"))
                    os.makedirs(scratch_dir, exist_ok=True)
                    
                    full_prompt = f"=== SYSTEM INSTRUCTION ===\n{system_prompt}\n\n=== USER PROMPT ===\n{user_prompt}"
                    with open(os.path.join(scratch_dir, "prompt_sent.txt"), "w", encoding="utf-8") as f:
                        f.write(full_prompt)
                    with open(os.path.join(scratch_dir, f"{safe_country}_{safe_sector}_prompt_sent.txt"), "w", encoding="utf-8") as f:
                        f.write(full_prompt)
                except Exception as pe:
                    print(f"[WARN] Failed to write prompt audit files: {pe}")
                
                response = model.generate_content(
                    contents=user_prompt,
                    generation_config=genai.types.GenerationConfig(
                        response_mime_type="application/json"
                    ),
                    request_options={"timeout": 60.0}
                )
                raw_text = response.text.strip()
                
                # Save raw response
                try:
                    with open(os.path.join(scratch_dir, "response_received.json"), "w", encoding="utf-8") as f:
                        f.write(raw_text)
                    with open(os.path.join(scratch_dir, f"{safe_country}_{safe_sector}_response_received.json"), "w", encoding="utf-8") as f:
                        f.write(raw_text)
                except Exception as re:
                    print(f"[WARN] Failed to write raw response audit files: {re}")
                


            # Clean JSON if wrapped in markdown code blocks
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
            raw_text = raw_text.strip()

            document = json.loads(raw_text)
            
            # Validate document content
            is_valid, err_reason = validate_policy_document_content(sector, document)
            if is_valid:
                gen_time = (datetime.now() - start_time).total_seconds()
                prompt_len = len(system_prompt) + len(user_prompt)
                resp_len = len(raw_text)
                
                # Add generation_metadata directly inside the document object
                metadata = {
                    "provider": provider_name,
                    "model": model_name,
                    "demo_mode": False,
                    "country": country,
                    "sector": sector,
                    "generation_timestamp": datetime.now().isoformat(),
                    "generation_time_seconds": round(gen_time, 2),
                    "prompt_length": prompt_len,
                    "response_length": resp_len,
                    "validation_retry_count": attempt
                }
                document["generation_metadata"] = metadata
                
                res = {
                    "policy_id": str(uuid.uuid4()),
                    "country": country,
                    "sector": sector,
                    "demo_mode": False,
                    "generated_at": datetime.now().isoformat(),
                    "generation_metadata": metadata,
                    "document": document,
                    "context_used": {
                        "existing_policies_count": context["existing_count"],
                        "reference_policies": context["reference_policies"],
                        "gaps_identified": list(context["gaps"]),
                        "demo_mode": False
                    }
                }
                return post_process_generated_document(res, context)
            else:
                print(f"[WARN] Generated content failed validation check on attempt {attempt + 1}: {err_reason}")
                last_error = ValueError(f"Content validation failed: {err_reason}")
                
        except Exception as err:
            print(f"[ERROR] Exception during generation attempt {attempt + 1}: {err}")
            last_error = err

    raise last_error or RuntimeError("Policy generation failed all validation and retry attempts.")
