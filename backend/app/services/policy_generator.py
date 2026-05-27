import os
import json
import uuid
from datetime import datetime
from anthropic import Anthropic
from app.database import get_connection
from app.ml.vector_store import semantic_search
from data.country_profiles import COUNTRY_PROFILES

# Initialize Anthropic API Client
from app.config import ANTHROPIC_API_KEY
api_key = ANTHROPIC_API_KEY
if not api_key:
    # We will raise a ValueError if the key is missing when the functions are called
    # but do not crash on import so that the app still boots.
    print("[WARN] ANTHROPIC_API_KEY is not set in environment.")

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

    # 3. Retrieve Top 5 reference policies from OTHER countries in same sector
    reference_policies = []
    try:
        search_query = f"{sector} policy framework {country}"
        raw_matches = semantic_search(
            query_text=search_query,
            n=5,
            sector_filter=sector,
            exclude_country=country
        )
        conn = get_connection()
        try:
            for m in raw_matches:
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
        if sector == "Cybersecurity":
            gaps = {"incident response plans", "supply chain oversight", "critical infrastructure baselines"}
        elif sector == "AI Governance":
            gaps = {"algorithmic transparency", "human-in-the-loop oversight", "model risk assessments"}
        else:
            gaps = {"audit logs", "compliance penalties", "monitoring metrics"}

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
        "gaps": list(gaps)
    }

def _generate_high_fidelity_mock(country: str, sector: str, scope: str, focus_areas: list, context: dict) -> dict:
    """
    Generates a beautifully tailored, high-fidelity legislative framework template mock 
    so the platform remains completely interactive and functional even without active API keys.
    """
    # Tailor national institutions dynamically
    inst_map = {
        "India": {
            "authority": "National AI Regulatory Authority (NAIRA) / Ministry of Electronics and Information Technology (MeitY)",
            "cert": "CERT-In (Indian Computer Emergency Response Team)",
            "appellate": "Cyber Appellate Tribunal",
            "commission": "National AI Commission"
        },
        "United States": {
            "authority": "Federal Artificial Intelligence Council (FAIC) / National Institute of Standards and Technology (NIST)",
            "cert": "CISA (Cybersecurity and Infrastructure Security Agency)",
            "appellate": "Federal Courts of Appeals",
            "commission": "Federal Trade Commission (FTC)"
        },
        "European Union": {
            "authority": "European Artificial Intelligence Board (EAIB)",
            "cert": "ENISA (European Union Agency for Cybersecurity)",
            "appellate": "Court of Justice of the European Union",
            "commission": "European Commission"
        }
    }
    
    inst = inst_map.get(country, {
        "authority": f"National Joint Council for {sector} / Department of Digital Services",
        "cert": f"National Cyber Defense Centre (NCDC)",
        "appellate": "National Administrative Tribunal",
        "commission": f"Department of Technology & Standards"
    })
    
    # Custom tailored sections
    sections = [
        {
            "number": "1",
            "title": "Definitions and Scope",
            "content": f"This regulatory framework establishes the legal and procedural guidelines governing {sector} activities throughout the jurisdiction of {country}. It applies directly to all public and private entities operating, developing, or distributing systems and technologies classified within this scope. This includes national and foreign corporations providing service layers to resident citizens. Major definitions herein establish classifications for 'High-Risk Applications', 'Data Processor Fiduciaries', and 'Algorithmic Decision Entities' to coordinate with international standards.",
            "subsections": [
                {
                    "number": "1.1",
                    "title": "Jurisdictional Applicability",
                    "content": f"Extends to any digital service layer offering {sector} products directly impacting {country}'s domestic economy, regardless of physical servers or regional corporate registration."
                }
            ]
        },
        {
            "number": "2",
            "title": "Guiding Principles",
            "content": f"Decisions and interpretations arising under this framework shall be strictly guided by the principles of transparent operations, human-centric design, risk-proportional accountability, and robust security baselines. Regulators and developers must cooperate to ensure that technological advancements respect individual privacy rights, national sovereignty, and economic development priorities. These principles establish a robust principles-based safety posture.",
            "subsections": [
                {
                    "number": "2.1",
                    "title": "Proportional Regulatory Response",
                    "content": "Regulatory oversight shall remain strictly proportionate to the potential societal impact, ensuring compliance barriers do not inhibit grassroots innovation or small enterprise initiatives."
                }
            ]
        },
        {
            "number": "3",
            "title": "Institutional Framework and Governance",
            "content": f"A dedicated regulatory division, functioning as the {inst['authority']}, is hereby formally established. The authority is empowered to draft binding administrative rules, conduct compliance audits on high-risk deployment architectures, and collaborate with standard-setting bodies globally. In instances of incident escalations or national cybersecurity threat reports, the authority shall maintain immediate data links with {inst['cert']} to contain threat factors.",
            "subsections": [
                {
                    "number": "3.1",
                    "title": "The Advisory Council",
                    "content": "An advisory panel of academic researchers, industry experts, and civil advocates shall meet quarterly to review standard frameworks and draft update briefs for the Ministry."
                }
            ]
        },
        {
            "number": "4",
            "title": "Core Obligations and Requirements",
            "content": f"All registered entities developing or implementing high-risk technology architectures must complete mandatory registration and present standard impact assessments. Developers must ensure that all codebases maintain audit logs and clear explainability parameters. Under the national requirements, these systems must integrate robust failure safeguards, local backup repositories, and standardized reporting mechanisms to track potential operational anomalies.",
            "subsections": [
                {
                    "number": "4.1",
                    "title": "Audit and Transparency Requirements",
                    "content": "System developers are required to present detailed algorithmic impact reports and register high-risk system architectures with the National Registry."
                }
            ]
        },
        {
            "number": "5",
            "title": "Rights and Protections",
            "content": f"Citizens of {country} are hereby guaranteed fundamental digital protections under this section. Any consumer subject to automated high-stakes decisions has the right to demand explicit human review and complete technical explanation of the underlying logic. Furthermore, entities must ensure no unfair bias is encoded in the processing algorithms, offering immediate avenues of appeal via the established {inst['appellate']}.",
            "subsections": [
                {
                    "number": "5.1",
                    "title": "Right to Human Intervention",
                    "content": "Any automated decision significantly affecting employment, financial status, or legal rights can be appealed directly for manual human evaluation."
                }
            ]
        },
        {
            "number": "6",
            "title": "Enforcement and Penalties",
            "content": f"Failure to comply with register requirements, audit demands, or mandatory safety provisions shall result in immediate administrative review. The {inst['commission']} is authorized to levy statutory fines scaled dynamically to the offending entity's global revenue, capping administrative liabilities up to 4% of annual turnovers for systemic negligence. Continued compliance failures shall result in temporary operation suspensions.",
            "subsections": [
                {
                    "number": "6.1",
                    "title": "Administrative Liabilities",
                    "content": "Statutory fines are scaled proportionally based on risk profiles, with maximum caps allocated to systemic data breaches and unnotified algorithmic manipulations."
                }
            ]
        },
        {
            "number": "7",
            "title": "Implementation Roadmap",
            "content": f"The national adoption of this framework follows a progressive, phased schedule over a 24-month horizon. This provides ample adaptation buffers for startups and local developers. Initial phases prioritize institutional setup and basic registry creation, moving sequentially into comprehensive audit enforcing and strict penalty compliance in final quarters.",
            "subsections": [
                {
                    "number": "7.1",
                    "title": "Voluntary Compliance Window",
                    "content": "A 12-month grace window is established to support local developer adaptations, offering free compliance sandboxes and government training modules."
                }
            ]
        },
        {
            "number": "8",
            "title": "International Cooperation",
            "content": f"Given the borderless scale of digital service layers, {country}'s regulatory bodies shall participate in global threat sharing networks, bilateral data validation trusts, and regulatory harmonization groups. Compliance audits conducted by recognized foreign authorities may be accepted under equivalence agreements to minimize regulatory duplication for multinational enterprises.",
            "subsections": [
                {
                    "number": "8.1",
                    "title": "Cross-Border Threat Synchronization",
                    "content": f"Mandatory real-time security logs sharing with friendly neighboring states and ENISA / CERT networks to synchronize defenses against systemic digital exploits."
                }
            ]
        },
        {
            "number": "9",
            "title": "Review and Amendment Procedures",
            "content": f"The technological landscape of {sector} shifts rapidly. To prevent legislative obsolescence, the Ministry shall order a complete legislative audit of this framework every two years. Any amendment proposals must be presented to the National Legislature, incorporating feedback gathered during public stakeholder roundtables.",
            "subsections": [
                {
                    "number": "9.1",
                    "title": "Dynamic Standards Updates",
                    "content": "Technical specifications, standard parameters, and specific cybersecurity thresholds can be updated via administrative circulars, avoiding formal legislative cycles."
                }
            ]
        }
    ]
    
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
                "source_url": "https://www.oecd.org/digital/",
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
        "title": f"{country.upper()} NATIONAL {sector.upper()} STRATEGY & LEGISLATIVE FRAMEWORK BLUEPRINT",
        "short_title": f"{country} {sector} Framework",
        "executive_summary": f"This comprehensive policy framework blueprint establishes the statutory and operational parameters for {sector} systems within {country}. Addressing key regulatory gaps identified during multi-jurisdiction semantic comparisons, the blueprint drafts clear boundaries for system audits, consumer transparency rights, and robust institutional oversight. It aligns {country}'s domestic industries with international standards, balancing security posture with technical innovation.",
        "preamble": f"Recognizing the transformative scale of {sector} technologies and their deep impact on commerce, governance, and citizen welfare; the Government of {country} hereby decrees this draft framework to establish safe, accountable, and highly resilient technology systems.",
        "sections": sections,
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
                    "Activate mandatory audit compliance checks for high-risk systems",
                    "Establish appellate tribunals for citizen dispute reviews",
                    "Enable cross-border sharing links with international peers"
                ]
            }
        ],
        "enforcement_mechanisms": f"Administered by the {inst['authority']} in coordination with national courts and local data commissioners.",
        "monitoring_framework": "Continuous impact reports, annual statutory reviews, and mandatory independent external auditing loops.",
        "references": refs,
        "gap_analysis_addressed": gap_addressed
    }

def generate_policy_document(
    country: str,
    sector: str,
    scope: str = None,
    focus_areas: list = None
) -> dict:
    """
    Constructs contextual prompts and uses Claude to generate a structured legislative document draft.
    """
    global api_key
    
    print(f"--- DEBUG: api_key is {repr(api_key)} ---")

    context = build_generation_context(country, sector)

    # High-fidelity mock fallback if ANTHROPIC_API_KEY is not set
    if not api_key or "sk-ant" not in api_key:
        mock_doc = _generate_high_fidelity_mock(country, sector, scope, focus_areas, context)
        return {
            "policy_id": str(uuid.uuid4()),
            "country": country,
            "sector": sector,
            "generated_at": datetime.now().isoformat(),
            "document": mock_doc,
            "context_used": {
                "existing_policies_count": context["existing_count"],
                "reference_policies": context["reference_policies"],
                "gaps_identified": list(context["gaps"]),
                "demo_mode": True
            }
        }

    anthropic_client = Anthropic(api_key=api_key)


    context = build_generation_context(country, sector)

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

    try:
        response = anthropic_client.messages.create(
            model="claude-opus-4-5",
            max_tokens=8000,
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt
        )
        raw_text = response.content[0].text.strip()
    except Exception as e:
        print(f"[WARN] Claude Opus failed or returned error: {e}. Trying fallback model...")
        # Fallback in case claude-opus-4-5 model is not available or errors
        try:
            response = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=8000,
                messages=[{"role": "user", "content": user_prompt}],
                system=system_prompt
            )
            raw_text = response.content[0].text.strip()
        except Exception as ex:
            raise RuntimeError(f"Failed to generate policy via Anthropic API: {str(ex)}")

    # Clean JSON if wrapped in markdown code blocks
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
    raw_text = raw_text.strip()

    try:
        document = json.loads(raw_text)
    except Exception as parse_err:
        print(f"[ERROR] Failed parsing Claude JSON. Raw text: {raw_text}")
        raise ValueError(f"AI response was not valid JSON: {str(parse_err)}")

    return {
        "policy_id": str(uuid.uuid4()),
        "country": country,
        "sector": sector,
        "generated_at": datetime.now().isoformat(),
        "document": document,
        "context_used": {
            "existing_policies_count": context["existing_count"],
            "reference_policies": context["reference_policies"],
            "gaps_identified": list(context["gaps"])
        }
    }
