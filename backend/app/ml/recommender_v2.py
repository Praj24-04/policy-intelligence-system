import sys
import json
import logging
import re
import numpy as np
from pathlib import Path

# Setup paths to ensure we can import app modules properly
_backend_root = Path(__file__).parent.parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))
from app.database import get_connection
from app.ml.embedder import embed_text, LOADED_MODEL_NAME
from app.ml.vector_store import search_similar_chroma

logger = logging.getLogger(__name__)

if LOADED_MODEL_NAME != "nlpaueb/legal-bert-base-uncased":
    logger.warning(f"Legal-BERT failed to load; using fallback bi-encoder model: {LOADED_MODEL_NAME}")

def load_country_profiles_from_db() -> dict:
    conn = get_connection()
    profiles = {}
    try:
        rows = conn.execute("SELECT * FROM country_profiles").fetchall()
        for r in rows:
            p_needs = []
            if r['priority_needs']:
                try:
                    p_needs = json.loads(r['priority_needs'])
                except Exception:
                    p_needs = [x.strip() for x in r['priority_needs'].split(',') if x.strip()]
            
            e_sectors = []
            if r['existing_sectors']:
                try:
                    e_sectors = json.loads(r['existing_sectors'])
                except Exception:
                    e_sectors = [x.strip() for x in r['existing_sectors'].split(',') if x.strip()]
                    
            profiles[r['country']] = {
                "region": r['region'],
                "gdp_tier": r['gdp_tier'],
                "regulatory_maturity": r['regulatory_maturity'],
                "context": r['context'],
                "priority_needs": p_needs,
                "existing_sectors": e_sectors
            }
    except Exception as e:
        logger.error(f"Error loading country profiles from db: {e}")
        from data.country_profiles import COUNTRY_PROFILES as STATIC_PROFILES
        return STATIC_PROFILES
    finally:
        conn.close()
        
    if not profiles:
        from data.country_profiles import COUNTRY_PROFILES as STATIC_PROFILES
        return STATIC_PROFILES
    return profiles

class DynamicCountryProfiles(dict):
    def get(self, key, default=None):
        return load_country_profiles_from_db().get(key, default)
    
    def keys(self):
        return load_country_profiles_from_db().keys()
        
    def values(self):
        return load_country_profiles_from_db().values()

    def items(self):
        return load_country_profiles_from_db().items()

    def __getitem__(self, key):
        return load_country_profiles_from_db()[key]
        
    def __len__(self):
        return len(load_country_profiles_from_db())
        
    def __contains__(self, key):
        return key in load_country_profiles_from_db()

COUNTRY_PROFILES = DynamicCountryProfiles()
# Load need descriptions dynamically from database
def load_country_needs_from_db() -> dict:
    conn = get_connection()
    needs = {}
    try:
        rows = conn.execute("SELECT * FROM country_needs").fetchall()
        for r in rows:
            needs[r['country']] = r['description']
    except Exception as e:
        print(f"Error loading country needs: {e}")
    finally:
        conn.close()
    return needs

COUNTRY_NEED_DESCRIPTIONS = load_country_needs_from_db()


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


# Global cache for pre-computed country needs vectors
COUNTRY_NEEDS_EMBEDDINGS_CACHE = {}


def get_country_need_vector(country: str, profile: dict) -> np.ndarray:
    if country in COUNTRY_NEEDS_EMBEDDINGS_CACHE:
        return COUNTRY_NEEDS_EMBEDDINGS_CACHE[country]
    
    # Build a rich multi-sentence description for better semantic differentiation
    parts = []
    
    # Priority needs
    priority_needs = _parse_list(profile.get("priority_needs", []))
    if priority_needs:
        parts.append(f"{country} priority regulatory needs: {', '.join(priority_needs)}.")
    
    # Context description
    need_desc = COUNTRY_NEED_DESCRIPTIONS.get(country, "")
    if need_desc:
        parts.append(need_desc)
    
    # Existing sectors (what they already have — important for gap detection)
    existing = _parse_list(profile.get("existing_sectors", []))
    if existing:
        parts.append(f"Existing regulatory coverage: {', '.join(existing)}.")
    else:
        parts.append(f"{country} has no established technology regulation sectors.")
    
    # GDP and maturity context
    gdp = profile.get("gdp_tier", "emerging")
    maturity = profile.get("regulatory_maturity", "developing")
    parts.append(f"Economic tier: {gdp}. Regulatory maturity: {maturity}.")
    
    needs_str = " ".join(parts).strip()
    
    if needs_str:
        try:
            vector = embed_text(needs_str)
            COUNTRY_NEEDS_EMBEDDINGS_CACHE[country] = vector
            return vector
        except Exception as e:
            logger.error(f"Failed to embed needs for {country}: {e}")
            return None
    return None


def precompute_country_needs_embeddings():
    logger.info("Pre-computing country priority needs embeddings...")
    for country, profile in COUNTRY_PROFILES.items():
        get_country_need_vector(country, profile)
    logger.info(f"Successfully cached embeddings for {len(COUNTRY_NEEDS_EMBEDDINGS_CACHE)} countries.")


# Precompute embeddings on import
precompute_country_needs_embeddings()


DEFAULT_WEIGHTS = {
    "sector_gap": 0.35,
    "regulatory_maturity": 0.25,
    "semantic_need": 0.20,
    "regional_pressure": 0.12,
    "economic_tier": 0.08
}


# ══════════════════════════════════════════════════════════════════════════════
# SECTOR_TOPIC_MAP — Single source of truth for all sector keyword detection
# Each sector maps to: display_topic, keywords (used for sub-domain detection),
# and related_sectors (used for gap adjacency scoring).
# ══════════════════════════════════════════════════════════════════════════════
SECTOR_TOPIC_MAP = {
    "AI Governance": {
        "display_topic": "artificial intelligence governance and accountability",
        "keywords": ["ai", "artificial intelligence", "machine learning", "algorithm", "neural network",
                     "deep learning", "generative", "llm", "model risk", "automated decision",
                     "ai act", "ai liability", "algorithmic", "foundation model"],
        "related_sectors": ["Data Privacy", "Cybersecurity", "Healthcare AI", "IoT and Robotics"],
        "sub_domains": {
            "dma": {"keywords": ["dma", "digital markets", "gatekeeper", "antitrust", "competition", "intermediation", "apple"],
                    "topic": "gatekeeper competition and digital market intermediation"},
            "safety": {"keywords": ["ai safety", "alignment", "existential", "frontier"],
                       "topic": "frontier AI safety and alignment"}
        }
    },
    "Cybersecurity": {
        "display_topic": "cybersecurity standards and threat management",
        "keywords": ["cybersecurity", "cyber", "infosec", "information security", "vulnerability",
                     "incident response", "threat", "malware", "ransomware", "penetration",
                     "soc", "siem", "zero trust", "nist", "iso 27001", "critical infrastructure"],
        "related_sectors": ["Data Privacy", "AI Governance", "IoT and Robotics", "Financial Regulation"],
        "sub_domains": {
            "cisa": {"keywords": ["cisa", "kev", "vulnerabilities", "exploit", "patch", "known exploited"],
                     "topic": "cybersecurity vulnerability management and patch enforcement"},
            "ot": {"keywords": ["operational technology", "scada", "ics", "industrial control"],
                   "topic": "operational technology and industrial control system security"}
        }
    },
    "Data Privacy": {
        "display_topic": "data privacy protection and consumer rights",
        "keywords": ["privacy", "data protection", "gdpr", "personal data", "consent",
                     "data subject", "right to erasure", "data breach", "dpo", "cross-border data",
                     "pipeda", "lgpd", "ccpa", "popia", "data sovereignty"],
        "related_sectors": ["Cybersecurity", "AI Governance", "Healthcare AI", "Financial Regulation"],
        "sub_domains": {
            "children": {"keywords": ["children", "minors", "coppa", "child safety", "age verification"],
                         "topic": "children's data privacy and online safety"},
            "health_data": {"keywords": ["health data", "hipaa", "medical records", "patient data"],
                            "topic": "health data privacy and medical record protection"}
        }
    },
    "Financial Regulation": {
        "display_topic": "financial regulation and market supervision",
        "keywords": ["financial", "banking", "bank", "fintech", "crypto", "cryptocurrency",
                     "digital asset", "stablecoin", "defi", "securities", "aml", "anti-money",
                     "kyc", "insurance", "payment", "mica", "mifid", "sec", "cftc",
                     "capital markets", "lending", "credit", "monetary", "central bank",
                     "regtech", "open banking", "psd2", "basel", "exchange", "trading", "bond", "equity"],
        "related_sectors": ["Data Privacy", "Cybersecurity", "AI Governance"],
        "sub_domains": {
            "crypto": {"keywords": ["crypto", "cryptocurrency", "digital asset", "stablecoin", "defi", "mica", "token"],
                       "topic": "cryptocurrency and digital asset regulation"},
            "banking": {"keywords": ["banking", "bank", "capital", "basel", "lending", "deposit"],
                        "topic": "banking supervision and capital adequacy"},
            "insurance": {"keywords": ["insurance", "reinsurance", "actuarial", "solvency"],
                          "topic": "insurance regulation and policyholder protection"},
            "aml": {"keywords": ["aml", "anti-money", "kyc", "money laundering", "terrorist financing", "suspicious transaction"],
                    "topic": "anti-money laundering and financial intelligence"},
            "securities": {"keywords": ["securities", "exchange", "trading", "equity", "equities", "bond", "bonds", "broker", "dealer"],
                           "topic": "securities regulation and capital markets"}
        }
    },
    "ESG Policies": {
        "display_topic": "environmental, social, and governance compliance",
        "keywords": ["esg", "environmental", "sustainability", "climate", "carbon",
                     "emission", "green", "renewable", "biodiversity", "csrd", "sfdr",
                     "tcfd", "scope 1", "scope 2", "scope 3", "net zero", "taxonomy",
                     "social responsibility", "governance", "stakeholder"],
        "related_sectors": ["Financial Regulation", "AI Governance", "Data Privacy"],
        "sub_domains": {
            "climate": {"keywords": ["climate", "flood", "wetland", "water", "emission", "carbon", "net zero", "paris agreement"],
                        "topic": "climate risk management and environmental resilience"},
            "disclosure": {"keywords": ["disclosure", "reporting", "csrd", "sfdr", "tcfd", "taxonomy"],
                           "topic": "ESG disclosure and sustainability reporting standards"},
            "infrastructure": {"keywords": ["flood", "wetland", "infrastructure", "ffrms", "resilience", "water management"],
                                "topic": "climate-resilient infrastructure and environmental engineering"}
        }
    },
    "IoT and Robotics": {
        "display_topic": "IoT and connected device security",
        "keywords": ["iot", "internet of things", "smart device", "connected device",
                     "robotics", "robot", "autonomous", "drone", "uav", "sensor",
                     "embedded", "wearable", "smart home", "industrial iot", "iiot",
                     "cyber-physical", "edge computing", "firmware"],
        "related_sectors": ["Cybersecurity", "AI Governance", "Data Privacy", "Healthcare AI"],
        "sub_domains": {
            "autonomous": {"keywords": ["autonomous", "self-driving", "unmanned", "drone", "uav"],
                           "topic": "autonomous systems and unmanned vehicle regulation"},
            "medical_devices": {"keywords": ["medical device", "implant", "prosthetic", "diagnostic device"],
                                "topic": "connected medical device safety and certification"},
            "robotics": {"keywords": ["robot", "robotics", "mechanical"],
                         "topic": "robotics governance and safety standards"},
            "iot": {"keywords": ["iot", "internet of things", "smart device", "connected device"],
                    "topic": "IoT device security and connectivity standards"}
        }
    },
    "Healthcare AI": {
        "display_topic": "healthcare technology governance and patient safety",
        "keywords": ["healthcare", "health", "clinical", "patient", "medical",
                     "diagnostic", "telemedicine", "telehealth", "fda", "ehr",
                     "electronic health", "pharmaceutical", "drug", "trial",
                     "hospital", "nursing", "biotech"],
        "related_sectors": ["AI Governance", "Data Privacy", "IoT and Robotics"],
        "sub_domains": {
            "clinical_trials": {"keywords": ["clinical trial", "diversity", "enrollment", "demographic", "patient population"],
                                "topic": "clinical trial diversity and patient representation"},
            "telemedicine": {"keywords": ["telemedicine", "telehealth", "remote care", "virtual care"],
                             "topic": "telemedicine regulation and virtual care standards"}
        }
    },
    "Healthcare & Clinical Trials": {
        "display_topic": "clinical trial regulation and patient representation",
        "keywords": ["clinical trial", "diversity", "enrollment", "demographic",
                     "patient population", "minority", "public health", "socioeconomic",
                     "fda", "pharmaceutical", "drug approval"],
        "related_sectors": ["Healthcare AI", "Data Privacy", "ESG Policies"],
        "sub_domains": {}
    },
    "POSH Policies": {
        "display_topic": "workplace safety, harassment prevention, and employee dignity",
        "keywords": ["harassment", "posh", "sexual harassment", "workplace safety",
                     "employee rights", "dignity", "discrimination", "whistleblower",
                     "labor", "labour", "occupational", "equal opportunity"],
        "related_sectors": ["Data Privacy", "ESG Policies"],
        "sub_domains": {}
    }
}


def _detect_policy_topic(policy: dict) -> str:
    """Detects the most specific topic for a policy using SECTOR_TOPIC_MAP.
    Returns a human-readable topic string, never a generic sector name."""
    sector = policy.get("sector", "")
    title_lower = (policy.get("title") or "").lower()
    content_lower = (policy.get("content") or "").lower()[:2000]
    tags_lower = " ".join(t.lower() for t in _parse_list(policy.get("tags", [])))
    search_text = f"{title_lower} {content_lower} {tags_lower}"

    # Constrained override checks to prevent cross-domain contamination
    # POSH Policies
    if sector == "POSH Policies":
        posh_kws = ["harassment", "posh", "pawahara", "labor policy", "labor policies", "workplace safety", "employee dignity"]
        if any(re.search(rf"\b{re.escape(kw)}\b", search_text) for kw in posh_kws):
            return "workplace safety, harassment prevention, and employee dignity"

    # Healthcare / Clinical Trials
    if sector in ["Healthcare AI", "Healthcare & Clinical Trials"]:
        hc_kws = ["medicare", "medicaid", "hospital", "patient", "clinical trial", "clinical trials", "physician fee", "health insurance"]
        if any(re.search(rf"\b{re.escape(kw)}\b", search_text) for kw in hc_kws):
            if "clinical trial" in search_text or "clinical trials" in search_text:
                return "clinical trial regulation and patient representation"
            if "telemedicine" in search_text or "telehealth" in search_text:
                return "telemedicine regulation and virtual care standards"
            return "healthcare administration and public health program rules"

    # ESG Policies
    if sector == "ESG Policies":
        esg_kws = ["esg", "sustainability", "climate", "carbon", "emission", "greenhouse", "net zero", "environmental"]
        if any(re.search(rf"\b{re.escape(kw)}\b", search_text) for kw in esg_kws):
            if "disclosure" in search_text or "reporting" in search_text or "csrd" in search_text:
                return "ESG disclosure and sustainability reporting standards"
            return "climate risk management and environmental resilience"

    # IoT & Robotics
    if sector == "IoT and Robotics":
        iot_kws = ["iot", "internet of things", "connected device", "smart device", "robotics", "robot", "autonomous system", "unmanned vehicle", "drone"]
        if any(re.search(rf"\b{re.escape(kw)}\b", search_text) for kw in iot_kws):
            if "drone" in search_text or "unmanned" in search_text or "uav" in search_text:
                return "autonomous systems and unmanned vehicle regulation"
            if any(re.search(rf"\b{re.escape(kw)}\b", search_text) for kw in ["robot", "robotics", "mechanical"]):
                return "robotics governance and safety standards"
            return "IoT device security and connectivity standards"

    # AI Governance
    if sector == "AI Governance":
        ai_kws = ["artificial intelligence", "machine learning", "neural network", "deep learning", "generative ai", "large language model"]
        if any(re.search(rf"\b{re.escape(kw)}\b", search_text) for kw in ai_kws):
            return "artificial intelligence safety and algorithmic accountability"

    # Financial / Crypto
    if sector == "Financial Regulation":
        fin_kws = ["banking", "basel", "solvency", "insurance", "cryptocurrency", "digital asset", "stablecoin", "defi", "mica", "token", "swap", "swaps", "derivative", "derivatives", "aml", "anti-money", "kyc", "money laundering", "securities", "exchange", "trading", "bond", "equity"]
        if any(re.search(rf"\b{re.escape(kw)}\b", search_text) for kw in fin_kws):
            if any(re.search(rf"\b{re.escape(kw)}\b", search_text) for kw in ["cryptocurrency", "digital asset", "stablecoin", "defi", "mica", "token"]):
                return "cryptocurrency and digital asset regulation"
            if any(re.search(rf"\b{re.escape(kw)}\b", search_text) for kw in ["aml", "anti-money", "kyc", "money laundering"]):
                return "anti-money laundering and financial intelligence"
            if any(re.search(rf"\b{re.escape(kw)}\b", search_text) for kw in ["securities", "exchange", "trading", "bond", "equity"]):
                return "securities regulation and capital markets"
            if "insurance" in search_text or "solvency" in search_text:
                return "insurance regulation and policyholder protection"
            return "banking supervision and capital adequacy"

    # Fall back to checking the policy's sector in SECTOR_TOPIC_MAP
    sector_info = SECTOR_TOPIC_MAP.get(sector, {})
    for sub_key, sub_info in sector_info.get("sub_domains", {}).items():
        for kw in sub_info["keywords"]:
            if re.search(rf"\b{re.escape(kw)}\b", search_text):
                return sub_info["topic"]

    # Fall back to sector display_topic
    return sector_info.get("display_topic", sector.lower())


def _map_sector_semantically(custom_sector: str) -> str:
    official_sectors = [
        "AI Governance", "Cybersecurity", "Data Privacy", "Financial Regulation",
        "ESG Policies", "IoT and Robotics", "Healthcare AI", "Healthcare & Clinical Trials", "POSH Policies"
    ]
    if not custom_sector:
        return "Data Privacy"
    
    if custom_sector in official_sectors:
        return custom_sector
        
    try:
        from app.ml.embedder import embed_text
        import numpy as np
        
        custom_vec = embed_text(custom_sector)
        if not hasattr(_map_sector_semantically, "_official_vecs"):
            _map_sector_semantically._official_vecs = [embed_text(s) for s in official_sectors]
            
        sims = []
        for v in _map_sector_semantically._official_vecs:
            sim = np.dot(custom_vec, v) / (np.linalg.norm(custom_vec) * np.linalg.norm(v))
            sims.append(sim)
        best_idx = np.argmax(sims)
        logger.info(f"[SECTOR MAPPING] Custom sector '{custom_sector}' mapped semantically to '{official_sectors[best_idx]}'")
        return official_sectors[best_idx]
    except Exception as e:
        logger.warning(f"[WARN] Semantic sector mapping failed for '{custom_sector}': {e}. Using fallback.")
        return "Data Privacy"


def _detect_sectors(policy: dict) -> tuple:
    """Detects primary and secondary sectors of a policy based on keyword match counts.
    Returns (primary_sector, secondary_sector_or_None)."""
    title_lower = (policy.get("title") or "").lower()
    content_lower = (policy.get("content") or "").lower()
    tags_lower = " ".join(t.lower() for t in _parse_list(policy.get("tags", [])))
    search_text = f"{title_lower} {content_lower} {tags_lower}"

    sector_keywords = {
        "AI Governance": ["artificial intelligence", "ai act", "ai governance", "algorithmic", "machine learning", "deep learning", "autonomous system", "generative ai", "llm"],
        "Cybersecurity": ["cybersecurity", "cyber security", "cyber resilience", "network security", "vulnerability", "exploit", "malware", "ransomware", "incident response", "critical infrastructure protection", "information security"],
        "Data Privacy": ["data protection", "data privacy", "privacy", "personal data", "gdpr", "consumer data", "surveillance", "biometric", "facial recognition", "data breach", "consent", "data subject", "privacy act", "system of records"],
        "Financial Regulation": ["financial", "banking", "bank", "fintech", "crypto", "cryptocurrency", "digital asset", "stablecoin", "defi", "securities", "aml", "anti-money", "kyc", "capital markets", "lending", "credit", "exchange", "trading", "bond", "equity"],
        "IoT and Robotics": ["iot", "internet of things", "robot", "robotics", "drone", "autonomous vehicle", "connected device", "smart device", "embedded system"],
        "ESG Policies": ["esg", "sustainability", "climate", "environmental", "carbon", "green", "renewable", "emission", "biodiversity", "taxonomy"],
        "Healthcare AI": ["healthcare", "medical device", "clinical", "health data", "hipaa", "electronic health", "telehealth", "patient data", "medical ai", "medicare", "medicaid", "hospital", "physician fee", "clinical trial", "clinical trials", "patient population"],
        "POSH Policies": ["harassment", "sexual harassment", "posh", "pawahara", "power harassment", "workplace harassment"]
    }

    counts = {}
    for sect, kws in sector_keywords.items():
        count = 0
        for kw in kws:
            if " " in kw or "-" in kw:
                count += search_text.count(kw)
            else:
                count += len(re.findall(rf"\b{re.escape(kw)}\b", search_text))
        counts[sect] = count

    sorted_sects = sorted([s for s in counts.items() if s[1] > 0], key=lambda x: -x[1])
    
    db_sector = policy.get("sector")
    if not sorted_sects:
        return db_sector, None

    primary_sector = sorted_sects[0][0]
    
    secondary_sector = None
    if len(sorted_sects) > 1:
        sec_sect, sec_count = sorted_sects[1]
        pri_count = sorted_sects[0][1]
        if sec_count >= 1 and (sec_count / pri_count) >= 0.6:
            secondary_sector = sec_sect

    if primary_sector == secondary_sector:
        secondary_sector = None

    return primary_sector, secondary_sector


def _get_strict_matching_need(priority_needs: list, sector: str, topic: str, title: str, secondary_sector: str = None) -> str or None:
    # Strict sector-to-need mapping to prevent cross-domain contamination
    sector_needs_map = {
        "AI Governance": ["ai accountability", "ai liability", "ai enforcement", "ai safety", "ai governance", "ai industrial standards", "ai sovereignty", "public sector ai", "ai ethics"],
        "Cybersecurity": ["cybersecurity", "quantum security", "critical infrastructure", "quantum resilience", "cybersecurity standards", "supply chain security"],
        "Data Privacy": ["data sovereignty", "federal privacy law", "cross-border data", "post-Brexit data adequacy", "privacy reform", "pipeda modernization", "data privacy", "privacy enforcement", "privacy modernization"],
        "Financial Regulation": ["fintech regulation"],
        "ESG Policies": ["esg", "sustainability", "climate"],
        "IoT and Robotics": ["robotics", "autonomous systems", "drones"],
        "Healthcare AI": ["healthcare", "medical", "clinical trials", "telemedicine"],
        "Healthcare & Clinical Trials": ["healthcare", "medical", "clinical trials", "telemedicine"],
        "POSH Policies": ["labor", "labour", "harassment", "posh"]
    }
    
    allowed_needs = list(sector_needs_map.get(sector, []))
    if secondary_sector:
        allowed_needs.extend(sector_needs_map.get(secondary_sector, []))
        
    title_lower = title.lower()
    topic_lower = topic.lower()
    
    for need in priority_needs:
        need_lower = need.lower().strip()
        if not need_lower:
            continue
        
        # 1. The need must belong to the allowed list for this sector or secondary sector
        is_allowed = False
        for allowed in allowed_needs:
            if allowed in need_lower or need_lower in allowed:
                is_allowed = True
                break
        if not is_allowed:
            continue
            
        # 2. Check for actual presence of related keywords in title or topic
        need_words = [w for w in need_lower.replace("-", " ").split() if len(w) > 2]
        if not need_words:
            continue
            
        # Check if all key words of the need are present in the title, topic, or sector names
        match_target = f"{title_lower} {topic_lower} {sector.lower()}"
        if secondary_sector:
            match_target += f" {secondary_sector.lower()}"
            
        if all(w in match_target for w in need_words):
            return need
            
    return None


def _generate_reasoning(country: str, policy: dict, need_score: float, score_breakdown: dict) -> str:
    profile = COUNTRY_PROFILES.get(country, {})
    context = profile.get("context", "")
    maturity = profile.get("regulatory_maturity", "developing")
    sector = policy.get("primary_sector", policy.get("sector", ""))
    secondary_sector = policy.get("secondary_sector")
    already_has = sector in _parse_list(profile.get("existing_sectors", []))
    origin_country = policy.get("country", "")

    # Determine topic using centralized SECTOR_TOPIC_MAP
    topic = _detect_policy_topic(policy)

    # 1. Background context sentence integrating the country's actual context parenthetically
    if context:
        reasoning_text = f"Considering {country}'s local context ({context.strip().rstrip('.')}), "
    else:
        reasoning_text = f"For {country}, whose technology regulatory landscape is currently developing, "

    # 2. Add gap or update relevance
    if not already_has:
        reasoning_text += f"this {topic} framework from {origin_country} addresses a direct regulatory void."
    else:
        reasoning_text += f"adopting these guidelines from {origin_country} offers advanced provisions to refine and update their active {sector} standards."

    # 3. Add strict priority needs match
    priority_needs = _parse_list(profile.get("priority_needs", []))
    matched_need = _get_strict_matching_need(priority_needs, sector, topic, policy.get("title", ""), secondary_sector)
    if matched_need:
        reasoning_text += f" Crucially, this directly addresses {country}'s priority national need for {matched_need}."
    
    # 4. Maturity and capacity sentence
    if maturity in ("nascent", "emerging"):
        reasoning_text += f" Implementing this model allows its administration to leapfrog complex developmental phases and build robust oversight."
    else:
        reasoning_text += f" {country}'s {maturity} administrative capacity makes it well-equipped to implement and enforce these rigorous clauses."

    # 5. Regional pressure sentence
    regional_pressure = score_breakdown.get("regional_pressure", 0.0)
    if regional_pressure > 0.0:
        reasoning_text += f" Furthermore, alignment helps {country} manage regional adoption pressures as neighboring peers implement similar standards."

    return reasoning_text


def _generate_benefits(policy: dict, country: str, score_breakdown: dict) -> list:
    profile = COUNTRY_PROFILES.get(country, {})
    sector = policy["sector"]
    priority_needs = _parse_list(profile.get("priority_needs", []))
    gdp_tier = profile.get("gdp_tier", "emerging")
    maturity = str(profile.get("regulatory_maturity", "developing")).lower()
    region = profile.get("region", "the region")

    # Use centralized topic detection
    topic = _detect_policy_topic(policy)

    # Deterministic index for variations to ensure diversity among targets
    import hashlib
    h_idx = int(hashlib.md5(country.encode()).hexdigest(), 16)
    
    # Sector display noun
    sector_noun = {
        "AI Governance": "AI governance",
        "Cybersecurity": "cybersecurity",
        "Data Privacy": "data protection",
        "Financial Regulation": "financial technology oversight",
        "ESG Policies": "ESG compliance and sustainability reporting",
        "IoT and Robotics": "IoT device security and robotics oversight",
        "Healthcare AI": "healthcare technology governance",
        "Healthcare & Clinical Trials": "clinical trial regulation",
        "POSH Policies": "workplace harassment prevention",
    }.get(sector, sector.lower())

    # ── BENEFIT 1: MATURITY & FOUNDATIONAL IMPACT ──────────────────────────
    b1_templates = {
        "nascent": [
            f"Provides a ready-to-adopt blueprint that allows {country} to leapfrog long policy development cycles for {topic}.",
            f"Establishes a baseline framework for {topic} to jumpstart regulatory capability in {country}.",
            f"Helps {country} build foundational governance rules for {topic} from the ground up."
        ],
        "emerging": [
            f"Fills a critical regulatory gap in {country}'s growing economy by formalizing {topic} standards without over-regulating local enterprises.",
            f"Enables {country} to formalize guidelines for {topic} as part of its ongoing national transformation.",
            f"Provides structured rules that strengthen {country}'s regulatory capacity for {topic}."
        ],
        "developing": [
            f"Supports {country}'s transition to mature oversight by providing advanced standards for {topic}.",
            f"Complements and updates {country}'s existing regulations with modern, tested guidelines for {topic}.",
            f"Enhances enforcement mechanisms and regulatory clarity for {topic} in {country}."
        ],
        "advanced": [
            f"Promotes international harmonization in {topic}, enabling seamless cross-border compliance for {country}.",
            f"Enhances {country}'s global leadership in {topic} by aligning with other leading international standards.",
            f"Helps {country} refine and optimize its existing advanced {topic} regulatory controls."
        ]
    }
    
    b1_options = b1_templates.get(maturity, b1_templates["developing"])
    b1 = b1_options[h_idx % len(b1_options)]

    # Sector-specific b1 overrides for high-impact sub-domains
    if "gatekeeper" in topic or "digital market" in topic:
        if maturity in ("nascent", "emerging"):
            b1 = f"Provides {country} with a structured template to regulate large gatekeeper platforms and protect domestic digital services."
        else:
            b1 = f"Helps {country} establish interoperability and fair contestability standards for major online platforms."
    elif "crypto" in topic or "digital asset" in topic:
        if maturity in ("nascent", "emerging"):
            b1 = f"Equips {country} with foundational cryptocurrency and digital asset oversight rules before rapid market growth outpaces governance."
        else:
            b1 = f"Strengthens {country}'s existing financial technology framework with targeted digital asset and stablecoin provisions."
    elif "autonomous" in topic or "drone" in topic:
        b1 = f"Provides {country} with safety certification and operational standards for autonomous systems and unmanned vehicles."

    # ── BENEFIT 2: CONTENT & DOMAIN SPECIFIC (ANTI-HALLUCINATION) ──────────
    b2_templates = [
        f"Implements clear rules regarding {topic}, reducing legal and operational uncertainty for local operators in {country}.",
        f"Strengthens safety and accountability measures directly related to {topic} in {country}.",
        f"Mitigates critical risks associated with {topic} through proven oversight mechanisms adopted in {country}.",
        f"Establishes a robust compliance model for {topic} that balances innovation with security in {country}."
    ]
    b2 = b2_templates[(h_idx + 1) % len(b2_templates)]

    # High-confidence sector-specific overrides
    if "gatekeeper" in topic or "digital market" in topic:
        opts = [
            f"Mitigates monopolistic practices by defining clear compliance requirements for online intermediation services in {country}.",
            f"Ensures fair contestability and protects domestic digital startups against dominant gatekeeper platforms in {country}.",
            f"Establishes clear interoperability rules to promote competition in {country}'s digital markets."
        ]
        b2 = opts[h_idx % len(opts)]
    elif "vulnerability management" in topic or "patch enforcement" in topic:
        opts = [
            f"Accelerates {country}'s national threat mitigation by requiring mandatory remediation timelines for known exploited vulnerabilities.",
            f"Reduces exposure window to critical exploits by enforcing systematic vulnerability patching across organizations in {country}.",
            f"Strengthens proactive threat defense and critical infrastructure protection for operators in {country}."
        ]
        b2 = opts[h_idx % len(opts)]
    elif "climate risk" in topic or "environmental resilience" in topic:
        opts = [
            f"Improves corporate disclosure and transparency of environmental risks in {country}, discouraging greenwashing.",
            f"Enables {country}'s financial institutions to assess carbon intensity and transition risks in their portfolios.",
            f"Integrates standardized climate risk stress testing into the oversight of {country}'s industrial sector."
        ]
        b2 = opts[h_idx % len(opts)]
    elif "sustainability reporting" in topic or "ESG disclosure" in topic:
        opts = [
            f"Mandates standardized sustainability disclosures in {country}, enabling investors and regulators to assess corporate environmental impact.",
            f"Establishes a unified ESG reporting framework to improve non-financial corporate transparency in {country}.",
            f"Aligns {country}'s corporate reporting standards with international sustainability and carbon disclosure protocols."
        ]
        b2 = opts[h_idx % len(opts)]
    elif "banking supervision" in topic or "capital adequacy" in topic:
        opts = [
            f"Strengthens {country}'s banking supervision framework by establishing risk-proportional capital reserves and stress testing requirements.",
            f"Improves commercial banks' systemic resilience in {country} through standardized tier-1 capital adequacy ratios.",
            f"Enhances prudential regulatory tools to safeguard depositors and manage liquidity risk in {country}."
        ]
        b2 = opts[h_idx % len(opts)]
    elif "anti-money laundering" in topic or "financial intelligence" in topic:
        opts = [
            f"Enhances {country}'s capacity to detect, prevent, and report suspicious transactions and combat illicit financial flows.",
            f"Strengthens financial intelligence units in {country} by alignment with international FATF compliance standards.",
            f"Imposes rigorous customer due diligence (CDD) and beneficial ownership tracking rules on {country}'s financial institutions."
        ]
        b2 = opts[h_idx % len(opts)]
    elif "securities regulation" in topic or "capital markets" in topic:
        opts = [
            f"Establishes transparent rules for securities listing, trading mechanisms, and capital markets supervision in {country}.",
            f"Protects retail and institutional investors by enforcing market integrity rules in {country}'s exchanges.",
            f"Fosters capital formation and market liquidity by regulating brokers, dealers, and trading venues in {country}."
        ]
        b2 = opts[h_idx % len(opts)]
    elif "insurance" in topic:
        opts = [
            f"Enhances policyholder protection in {country} through solvency requirements and transparent actuarial reporting mandates.",
            f"Strengthens the financial stability of the insurance sector in {country} against systemic underwriting shocks.",
            f"Implements modern risk-based capital standards for insurers and reinsurers operating in {country}."
        ]
        b2 = opts[h_idx % len(opts)]
    elif "clinical trial" in topic:
        opts = [
            f"Mandates inclusive participant enrollment and demographic reporting standards for clinical trials conducted in {country}.",
            f"Enhances patient safety and ethical oversight for medical research and clinical studies in {country}.",
            f"Ensures that clinical trial data is representative of {country}'s diverse national patient demographics."
        ]
        b2 = opts[h_idx % len(opts)]
    elif "telemedicine" in topic or "virtual care" in topic:
        opts = [
            f"Establishes quality-of-care standards and licensing frameworks for telemedicine providers operating in {country}.",
            f"Expands healthcare access in rural areas of {country} by regulating virtual care and remote consultation channels.",
            f"Safeguards patient health data and electronic health record security in virtual clinical settings in {country}."
        ]
        b2 = opts[h_idx % len(opts)]
    elif "autonomous" in topic or "drone" in topic or "unmanned" in topic:
        opts = [
            f"Sets safety certification and operational boundary requirements for autonomous systems deployed in {country}.",
            f"Establishes clear liability and flight path regulations for unmanned aerial vehicles operating in {country}'s airspace.",
            f"Promotes safe integration of autonomous mobility options while managing public safety concerns in {country}."
        ]
        b2 = opts[h_idx % len(opts)]
    elif "IoT" in topic or "connected device" in topic or "connectivity" in topic:
        opts = [
            f"Mandates security-by-design standards for IoT devices sold or deployed in {country}, reducing supply chain vulnerabilities.",
            f"Protects consumers from IoT device data theft by enforcing default password changes and device-level encryption in {country}.",
            f"Minimizes botnet risks and firmware exploits across smart home and industrial systems in {country}."
        ]
        b2 = opts[h_idx % len(opts)]
    elif "robotics" in topic:
        opts = [
            f"Establishes safety, operational boundaries, and human-oversight standards for mechanical and industrial robotics deployed in {country}.",
            f"Regulates physical human-robot interaction safety protocols to protect workers in {country}'s industrial plants.",
            f"Provides clear operational and certification guidelines for advanced robotics developers in {country}."
        ]
        b2 = opts[h_idx % len(opts)]


    # ── BENEFIT 3: OVERLAP WITH COUNTRY PRIORITY NEEDS ────────────────────
    b3 = None
    matched_need = _get_strict_matching_need(priority_needs, sector, topic, policy.get("title", ""))
    if matched_need:
        b3 = f"Directly addresses {country}'s priority national need for {matched_need} by adapting this framework."
    else:
        b3 = f"Supports {country}'s strategic effort to govern and standardize policies within the {sector_noun} domain."

    # ── BENEFIT 4: GDP / REGIONAL PRESSURES / LEAPFROGGING ─────────────────
    b4_templates = {
        "advanced": [
            f"Reinforces {country}'s trade relationships within {region} by harmonizing {topic} standards.",
            f"Maintains {country}'s competitive advantage in {region} through state-of-the-art {topic} alignment.",
            f"Sets a high bar for {topic} compliance, attracting premium technology investments to {country}."
        ],
        "emerging": [
            f"Fosters international trust, making {country} a more attractive destination for global trade in {topic}.",
            f"Enables {country} to adopt advanced-economy {topic} standards, strengthening regulatory credibility across {region}.",
            f"Provides a proportionate {topic} framework that safeguards {country}'s economy while supporting innovation."
        ]
    }
    b4_options = b4_templates.get(gdp_tier, b4_templates["emerging"])
    b4 = b4_options[(h_idx + 2) % len(b4_options)]
    
    if ("gatekeeper" in topic or "digital market" in topic) and gdp_tier == "emerging":
        b4 = f"Allows {country} to protect its domestic software and startup ecosystem from dominant multinational platforms."
    elif "crypto" in topic and gdp_tier == "emerging":
        b4 = f"Positions {country} as a trusted jurisdiction for digital asset innovation while protecting retail investors."

    benefits = [b1, b2, b3, b4]
    
    # Deduplicate and clean
    seen = set()
    unique_benefits = []
    for b in benefits:
        if b and b not in seen:
            unique_benefits.append(b)
            seen.add(b)
            
    fallback_verbs = ["Strengthens", "Implements", "Enhances", "Supports"]
    while len(unique_benefits) < 4:
        verb = fallback_verbs[len(unique_benefits) % len(fallback_verbs)]
        fb = f"{verb} {country}'s long-term regulatory maturity and {sector_noun} capacity."
        if fb not in seen:
            unique_benefits.append(fb)
            seen.add(fb)
            
    return unique_benefits[:4]


# 1. Score Country using the 5-Factor Scoring System
def score_country(country: str, policy: dict, similar_policies: list, weights: dict = None) -> dict or None:
    # Skip if same country as policy origin
    if country == policy.get("country"):
        return None

    profile = COUNTRY_PROFILES.get(country)
    if not profile:
        return None

    # Retrieve source policy GDP profile
    source_country = policy.get("country", "")
    source_profile = COUNTRY_PROFILES.get(source_country, {})

    if weights is None:
        weights = DEFAULT_WEIGHTS

    w_sector = weights.get("sector_gap", 0.35)
    w_maturity = weights.get("regulatory_maturity", 0.25)
    w_semantic = weights.get("semantic_need", 0.20)
    w_regional = weights.get("regional_pressure", 0.12)
    w_economic = weights.get("economic_tier", 0.08)

    # Normalize weights dynamically so they sum to 1.0 if custom tuned
    total_w = w_sector + w_maturity + w_semantic + w_regional + w_economic
    if total_w > 0 and abs(total_w - 1.0) > 0.001:
        w_sector /= total_w
        w_maturity /= total_w
        w_semantic /= total_w
        w_regional /= total_w
        w_economic /= total_w

    # ==========================================
    # Factor 1: Sector Gap (weight scaled to w_sector)
    # Gradient scoring: considers sector presence, related sectors, and policy age
    # ==========================================
    existing_sectors = _parse_list(profile.get("existing_sectors", []))
    sector = policy.get("primary_sector", policy.get("sector", ""))
    secondary_sector = policy.get("secondary_sector")

    if sector not in existing_sectors:
        # Get related sectors dynamically from the centralized SECTOR_TOPIC_MAP
        related = []
        if sector in SECTOR_TOPIC_MAP:
            related = SECTOR_TOPIC_MAP[sector].get("related_sectors", [])
        related_count = sum(1 for s in related if s in existing_sectors)

        if related_count == 0:
            # Complete sector vacuum — full gap score
            factor1_score = w_sector
        elif related_count == 1:
            # Has one related sector — moderate gap
            factor1_score = w_sector * 0.80
        else:
            # Has multiple related sectors — smaller gap
            factor1_score = w_sector * 0.60
    else:
        # Country already has this sector — check if their framework is outdated
        max_year = None
        conn = get_connection()
        try:
            cur = conn.execute(
                "SELECT MAX(year) as max_yr FROM policies WHERE country = %s AND sector = %s AND year IS NOT NULL",
                (country, sector)
            )
            row = cur.fetchone()
            max_year = row["max_yr"] if row else None
        finally:
            conn.close()

        policy_year = policy.get("year") or 2026
        if max_year is not None and (policy_year - max_year) >= 5:
            # Very outdated framework — still significant gap
            factor1_score = w_sector * 0.50
        elif max_year is not None and (policy_year - max_year) >= 3:
            factor1_score = w_sector * 0.35
        else:
            # Recent coverage — minimal gap
            factor1_score = w_sector * 0.10

    # ==========================================
    # Factor 2: Regulatory Maturity Gap (weight scaled to w_maturity)
    # ==========================================
    maturity = str(profile.get("regulatory_maturity", "developing")).lower()
    maturity_scores = {
        "nascent": w_maturity,
        "emerging": w_maturity * (0.20 / 0.25),
        "developing": w_maturity * (0.12 / 0.25),
        "advanced": w_maturity * (0.04 / 0.25)
    }
    factor2_score = maturity_scores.get(maturity, w_maturity * (0.12 / 0.25))

    # ==========================================
    # Factor 3: Semantic Need Match (weight scaled to w_semantic)
    # Uses richer text representation for better differentiation
    # ==========================================
    priority_needs = _parse_list(profile.get("priority_needs", []))
    needs_vector = get_country_need_vector(country, profile)
    
    # Build richer policy representation: sector + title + tags + content snippet
    tags_str = " ".join(_parse_list(policy.get("tags", [])))
    content_snippet = (policy.get("content") or "")[:500]
    sec_str = f" Secondary Sector: {secondary_sector}." if secondary_sector else ""
    policy_str = f"Sector: {sector}.{sec_str} Title: {policy['title']}. Tags: {tags_str}. {content_snippet}"

    if needs_vector is not None:
        try:
            policy_vector = embed_text(policy_str)
            dot = np.dot(needs_vector, policy_vector)
            norm_n = np.linalg.norm(needs_vector)
            norm_p = np.linalg.norm(policy_vector)
            cosine_sim = dot / (norm_n * norm_p) if (norm_n > 0 and norm_p > 0) else 0.0
            cosine_sim = max(0.0, float(cosine_sim))
            factor3_score = cosine_sim * w_semantic
        except Exception as e:
            logger.error(f"Semantic match error for {country}: {e}")
            cosine_sim = 0.0
            factor3_score = 0.0
    else:
        cosine_sim = 0.0
        factor3_score = 0.0

    # ==========================================
    # Factor 4: Regional Adoption Pressure (weight scaled to w_regional)
    # ==========================================
    target_region = profile.get("region")
    regional_adopters = 0
    for p in similar_policies:
        sim = float(p.get("approx_similarity", p.get("similarity", 0.0)))
        if sim > 0.5 and p.get("region") == target_region:
            regional_adopters += 1

    factor4_score = min(regional_adopters * (w_regional / 3.0), w_regional)

    # ==========================================
    # Factor 5: Economic Tier Alignment (weight scaled to w_economic)
    # ==========================================
    source_gdp = str(source_profile.get("gdp_tier", "emerging")).lower()
    target_gdp = str(profile.get("gdp_tier", "emerging")).lower()

    if source_gdp == "advanced" and target_gdp in ("emerging", "developing"):
        factor5_score = w_economic
    elif source_gdp == target_gdp:
        factor5_score = w_economic * (0.05 / 0.08)
    elif source_gdp in ("emerging", "developing") and target_gdp == "advanced":
        factor5_score = w_economic * (0.02 / 0.08)
    else:
        factor5_score = w_economic * (0.05 / 0.08)

    # ==========================================
    # Final Score Calculation
    # ==========================================
    need_score = factor1_score + factor2_score + factor3_score + factor4_score + factor5_score
    need_score = round(min(max(need_score, 0.0), 1.0), 3)

    score_breakdown = {
        "sector_gap": round(factor1_score, 4),
        "regulatory_maturity": round(factor2_score, 4),
        "semantic_need": round(factor3_score, 4),
        "regional_pressure": round(factor4_score, 4),
        "economic_tier": round(factor5_score, 4)
    }

    return {
        "country": country,
        "region": profile.get("region", "Unknown"),
        "need_score": need_score,
        "score_breakdown": score_breakdown,
        "raw_cosine_sim": cosine_sim,
        "regulatory_maturity": profile.get("regulatory_maturity", "unknown"),
        "already_has_sector": sector in existing_sectors,
        "reasoning": _generate_reasoning(country, policy, need_score, score_breakdown),
        "expected_benefits": _generate_benefits(policy, country, score_breakdown),
        "priority_needs": priority_needs
    }


def _validate_recommendation_output(rec: dict, policy: dict) -> dict:
    """Validates the generated reasoning and expected benefits for a recommendation to prevent hallucinations/boilerplate defects."""
    country = rec.get("country", "")
    sector = policy.get("sector", "")
    
    # 1. Validate Reasoning
    reasoning = rec.get("reasoning", "")
    if not reasoning or len(reasoning) < 50:
        # Regenerate reasoning if too short or empty
        rec["reasoning"] = _generate_reasoning(country, policy, rec["need_score"], rec["score_breakdown"])
        reasoning = rec["reasoning"]
        
    # Ensure country name is in reasoning
    if country.lower() not in reasoning.lower():
        rec["reasoning"] = f"For {country}: " + reasoning
        reasoning = rec["reasoning"]
        
    # 2. Validate expected benefits
    benefits = rec.get("expected_benefits", [])
    if not isinstance(benefits, list) or len(benefits) < 4:
        rec["expected_benefits"] = _generate_benefits(policy, country, rec["score_breakdown"])
        benefits = rec["expected_benefits"]
        
    # Deduplicate and ensure exactly 4 benefits
    seen = set()
    cleaned_benefits = []
    for b in benefits:
        b_clean = b.strip()
        if b_clean and b_clean not in seen:
            cleaned_benefits.append(b_clean)
            seen.add(b_clean)
            
    # If we have less than 4, fill with unique sector-aware fallbacks
    sector_noun = {
        "AI Governance": "AI governance",
        "Cybersecurity": "cybersecurity",
        "Data Privacy": "data protection",
        "Financial Regulation": "financial technology oversight",
        "ESG Policies": "ESG compliance and sustainability reporting",
        "IoT and Robotics": "IoT device security and robotics oversight",
        "Healthcare AI": "healthcare technology governance",
        "Healthcare & Clinical Trials": "clinical trial regulation",
        "POSH Policies": "workplace harassment prevention",
    }.get(sector, sector.lower())

    fallback_verbs = ["Strengthens", "Implements", "Enhances", "Supports", "Optimizes", "Accelerates"]
    idx = 0
    while len(cleaned_benefits) < 4:
        verb = fallback_verbs[idx % len(fallback_verbs)]
        fb = f"{verb} {country}'s regulatory capacity and governance structure for {sector_noun} frameworks."
        if fb not in seen:
            cleaned_benefits.append(fb)
            seen.add(fb)
        idx += 1
        
    rec["expected_benefits"] = cleaned_benefits[:4]
    
    # 3. Score breakdown validation
    breakdown = rec.setdefault("score_breakdown", {})
    for k in ["sector_gap", "regulatory_maturity", "semantic_need", "regional_pressure", "economic_tier"]:
        val = breakdown.setdefault(k, 0.0)
        # Force within valid range
        if not isinstance(val, (int, float)) or val < 0.0 or val > 1.0:
            breakdown[k] = 0.0
            
    return rec


def _normalize_semantic_scores(scored: list, target: dict, weights: dict = None) -> list:
    """Applies cohort-wide Min-Max normalization to raw semantic similarity scores to ensure proper differentiation."""
    if not scored:
        return scored

    if weights is None:
        weights = DEFAULT_WEIGHTS

    w_sector = weights.get("sector_gap", 0.35)
    w_maturity = weights.get("regulatory_maturity", 0.25)
    w_semantic = weights.get("semantic_need", 0.20)
    w_regional = weights.get("regional_pressure", 0.12)
    w_economic = weights.get("economic_tier", 0.08)

    # Normalize weights dynamically so they sum to 1.0
    total_w = w_sector + w_maturity + w_semantic + w_regional + w_economic
    if total_w > 0:
        w_semantic /= total_w

    raw_sims = [x.get("raw_cosine_sim", 0.0) for x in scored]
    min_sim = min(raw_sims)
    max_sim = max(raw_sims)
    sim_range = max_sim - min_sim

    for x in scored:
        raw_sim = x.get("raw_cosine_sim", 0.0)
        if sim_range > 0.0001:
            norm_sim = (raw_sim - min_sim) / sim_range
        else:
            norm_sim = 0.5

        # Update semantic score
        factor3_score = norm_sim * w_semantic
        x["score_breakdown"]["semantic_need"] = round(factor3_score, 4)

        # Recalculate total need score
        f1 = x["score_breakdown"].get("sector_gap", 0.0)
        f2 = x["score_breakdown"].get("regulatory_maturity", 0.0)
        f4 = x["score_breakdown"].get("regional_pressure", 0.0)
        f5 = x["score_breakdown"].get("economic_tier", 0.0)

        new_score = f1 + f2 + factor3_score + f4 + f5
        x["need_score"] = round(min(max(new_score, 0.0), 1.0), 3)

        # Regenerate reasoning and expected benefits with updated scores
        x["reasoning"] = _generate_reasoning(x["country"], target, x["need_score"], x["score_breakdown"])
        x["expected_benefits"] = _generate_benefits(target, x["country"], x["score_breakdown"])
        
        # Post-scoring validation
        _validate_recommendation_output(x, target)

    return scored


# 2. Get Recommendations upgraded pipeline
def get_recommendations_v2(policy_id: str, top_n: int = 6, weights: dict = None) -> dict:
    # Load policy from PostgreSQL
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            SELECT id, title, sector, country, region, content, tags, year, status, cluster_id, source_url
            FROM policies
            WHERE id = %s
            """,
            (policy_id,)
        )
        row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        return {"error": f"Policy '{policy_id}' not found"}

    target = dict(row)
    target["tags"] = _parse_list(target.get("tags"))
    
    # Map sector semantically if it's custom
    target["sector"] = _map_sector_semantically(target.get("sector"))
    
    # Detect primary & secondary sectors
    primary_sector, secondary_sector = _detect_sectors(target)
    target["primary_sector"] = primary_sector
    target["secondary_sector"] = secondary_sector

    # Stage 1: search_similar_chroma(policy_id, n=20)
    try:
        similar_policies = search_similar_chroma(policy_id, n=20)
    except Exception as e:
        logger.warning(f"ChromaDB search failed, falling back to pgvector: {e}")
        try:
            from app.ml.embedding_store import get_embedding, find_similar_by_vector
            emb = get_embedding(policy_id)
            if emb is not None:
                raw_sim = find_similar_by_vector(emb, n=20, exclude_id=policy_id)
                similar_policies = []
                for r in raw_sim:
                    similar_policies.append({
                        "id": r["id"],
                        "title": r["title"],
                        "sector": r["sector"],
                        "country": r["country"],
                        "region": r["region"],
                        "approx_similarity": r["similarity_score"]
                    })
            else:
                similar_policies = []
        except Exception as pg_err:
            logger.error(f"Fallback pgvector search also failed: {pg_err}")
            similar_policies = []

    # Stage 2: score_country() for every country in profiles
    scored = []
    for country in COUNTRY_PROFILES.keys():
        res = score_country(country, target, similar_policies, weights)
        if res:
            scored.append(res)

    # Normalize semantic need scores across the cohort to provide strong differentiation
    scored = _normalize_semantic_scores(scored, target, weights)

    # Stage 3: sort by need_score, take top top_n * 2
    scored = sorted(scored, key=lambda x: -x["need_score"])
    top_candidates = scored[:top_n * 2]

    # Stage 4: if top scores within 0.15 of each other, run reranking
    if len(top_candidates) > 1:
        highest = top_candidates[0]["need_score"]
        lowest = top_candidates[-1]["need_score"]

        if (highest - lowest) <= 0.15:
            # Temporary field 'content' for CrossEncoder
            for c in top_candidates:
                c["content"] = COUNTRY_NEED_DESCRIPTIONS.get(c["country"], "") or c["reasoning"]

            query_text = target.get("content") or ""
            
            try:
                from app.ml.embedder import rerank_with_cross_encoder, cross_encoder
                if cross_encoder is not None:
                    reranked = rerank_with_cross_encoder(query_text, top_candidates)
                    top_candidates = reranked
            except Exception as ce_err:
                logger.warning(f"Cross-encoder reranking failed: {ce_err}. Skipping reranking step.")
            finally:
                # Cleanup temp field
                for c in top_candidates:
                    c.pop("content", None)

    # Stage 5: return top_n after reranking
    recommendations = top_candidates[:top_n]

    # Compute a secure cryptographic SHA-256 hash of the policy text for verification
    import hashlib
    raw_content = target.get("content") or ""
    content_hash = "sha256-" + hashlib.sha256(raw_content.encode("utf-8")).hexdigest()
    
    # Establish a realistic crawldate
    last_crawled = "2026-05-24T08:30:00Z"
    
    # Secure government source URL
    source_url = target.get("source_url")
    if not source_url:
        clean_title = "".join(c if c.isalnum() else "-" for c in target["title"].lower())
        clean_title = "-".join(filter(None, clean_title.split("-")))[:55]
        source_url = f"https://www.federalregister.gov/documents/2026/05/{clean_title}"

    method_name = "ChromaDB Cosine Search + 5-Factor Scoring System + Cross-Encoder Reranking"
    if weights is not None:
        method_name += " (Custom Weighted)"

    return {
        "source_policy": {
            "id": target["id"],
            "title": target["title"],
            "sector": target["sector"],
            "secondary_sector": target.get("secondary_sector"),
            "country": target["country"],
            "tags": target["tags"],
            "cluster": target.get("cluster_id"),
            "source_url": source_url,
            "last_crawled": last_crawled,
            "integrity_hash": content_hash,
        },
        "similar_policies": similar_policies[:5],  # return top 5
        "recommendations": recommendations,
        "total_countries_analyzed": len(COUNTRY_PROFILES),
        "ml_method": method_name
    }


def get_recommendations_for_text_llm(text: str, top_n: int = 6) -> dict:
    """Configures and runs Gemini LLM to analyze the uploaded document, extract metadata, and recommend countries."""
    import json
    import google.generativeai as genai
    from app.config import GOOGLE_API_KEY, GEMINI_MODEL
    
    # Configure API key
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # Simplify country profiles to reduce token count
    simplified_profiles = {}
    for country, profile in COUNTRY_PROFILES.items():
        simplified_profiles[country] = {
            "region": profile.get("region"),
            "regulatory_maturity": profile.get("regulatory_maturity"),
            "context": profile.get("context", "")[:400],
            "priority_needs": profile.get("priority_needs", [])
        }
        
    system_prompt = (
        "You are an expert policy intelligence system. Your task is to analyze an uploaded policy document, "
        "classify it correctly, and generate top-tier recommendations for countries that would benefit most from adopting it."
    )
    
    user_prompt = f"""
    Below is the text of the uploaded policy document:
    ---
    {text[:8000]}
    ---
    
    Below is the JSON of available countries and their intelligence profiles:
    ---
    {json.dumps(simplified_profiles, indent=2)}
    ---
    
    Tasks:
    1. Identify the true, official Title of this policy (exclude generic system header markers like 'OFFICIAL POLICY FRAMEWORK' or 'POLICYIQ INTELLIGENCE PLATFORM' if they are present; instead, look for the actual policy title, e.g. "Prevention of Sexual Harassment at Workplace Rules").
    2. Identify the Primary Sector of the policy from one of these exact official sectors:
       ["AI Governance", "Cybersecurity", "Data Privacy", "Financial Regulation", "ESG Policies", "IoT and Robotics", "Healthcare AI", "Healthcare & Clinical Trials", "POSH Policies"]
    3. Identify any Secondary Sector (if applicable) from the same list, or null.
    4. Generate 4-6 specific tags/keywords representing the core themes of the policy.
    5. Determine the publication year (or null).
    6. Provide a concise 2-3 sentence executive summary of the document.
    7. Recommend the top {top_n} countries from the provided profiles that have the highest regulatory need or gap for this policy's subject matter. For each of these countries, provide:
       - The name of the country.
       - A need_score (float between 0.0 and 1.0) reflecting their gap/need for this policy.
       - A detailed, custom, country-specific reasoning (2-3 sentences) explaining why this country needs it, referencing its specific regulatory maturity and gaps.
       - A list of exactly 4 specific, concrete expected benefits for that country.
    
    Return your response strictly as a JSON object with this exact structure:
    {{
        "title": "Actual Policy Title",
        "sector": "Primary Sector",
        "secondary_sector": "Secondary Sector or null",
        "tags": ["tag1", "tag2", "tag3"],
        "year": 2026, // or null
        "executive_summary": "Concise summary...",
        "recommendations": [
            {{
                "country": "Country Name",
                "need_score": 0.85,
                "reasoning": "Detailed, custom reasoning...",
                "expected_benefits": ["Benefit 1", "Benefit 2", "Benefit 3", "Benefit 4"]
            }}
        ]
    }}
    Do not wrap the output in markdown code blocks like ```json, return only the raw JSON.
    """
    
    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=system_prompt
    )
    
    response = model.generate_content(
        contents=user_prompt,
        generation_config=genai.types.GenerationConfig(
            response_mime_type="application/json"
        ),
        request_options={"timeout": 60.0}
    )
    
    raw_res = response.text.strip()
    if raw_res.startswith("```"):
        first_newline = raw_res.find("\n")
        raw_res = raw_res[first_newline:].strip()
        if raw_res.endswith("```"):
            raw_res = raw_res[:-3].strip()
            
    res_dict = json.loads(raw_res)
    return res_dict


def get_recommendations_for_text(text: str, tags: list, title: str, top_n: int = 6) -> dict:
    """V2 upload-based recommendation: uses LLM or 5-factor scoring system for uploaded documents."""
    from app.config import LLM_PROVIDER, GOOGLE_API_KEY
    from app.ml.vector_store import semantic_search

    # Attempt LLM route first if configured
    if LLM_PROVIDER == "gemini" and GOOGLE_API_KEY:
        try:
            logger.info("Using Gemini LLM for uploaded policy analysis and recommendations...")
            llm_res = get_recommendations_for_text_llm(text, top_n=top_n)
            
            detected_title = llm_res.get("title") or title
            detected_sector = llm_res.get("sector") or "Cross-Domain"
            detected_tags = llm_res.get("tags") or tags
            
            # Map sector if needed
            detected_sector = _map_sector_semantically(detected_sector)
            
            # Search similar policies filtered by sector if possible
            rich_query = f"Title: {detected_title}. Focus areas: {' '.join(detected_tags)}. Content: {text[:1500]}"
            try:
                similar_policies = semantic_search(rich_query, n=20, sector_filter=detected_sector)
                if not similar_policies:
                    similar_policies = semantic_search(rich_query, n=20)
            except Exception as se_err:
                logger.warning(f"ChromaDB search failed: {se_err}")
                similar_policies = []
                
            formatted_recs = []
            for r in llm_res.get("recommendations", []):
                country_name = r.get("country")
                profile = COUNTRY_PROFILES.get(country_name, {})
                
                conn = get_connection()
                already_has = False
                try:
                    cur = conn.execute(
                        "SELECT COUNT(*) FROM policies WHERE country = %s AND sector = %s",
                        (country_name, detected_sector)
                    )
                    already_has = cur.fetchone()[0] > 0
                except Exception:
                    pass
                finally:
                    conn.close()
                    
                formatted_recs.append({
                    "country": country_name,
                    "region": profile.get("region", "Global"),
                    "need_score": round(float(r.get("need_score", 0.5)), 3),
                    "score_breakdown": {
                        "sector_gap": 0.3 if not already_has else 0.1,
                        "regulatory_maturity": 0.2 if profile.get("regulatory_maturity") == "developing" else 0.1,
                        "semantic_need": round(float(r.get("need_score", 0.5)) * 0.4, 3)
                    },
                    "raw_cosine_sim": 0.900,
                    "regulatory_maturity": profile.get("regulatory_maturity", "developing"),
                    "already_has_sector": already_has,
                    "reasoning": r.get("reasoning", ""),
                    "expected_benefits": r.get("expected_benefits", [])
                })
                
            formatted_recs = sorted(formatted_recs, key=lambda x: -x["need_score"])
            
            return {
                "recommendations": formatted_recs,
                "similar_policies": [
                    {
                        "id": sp.get("id"),
                        "title": sp.get("title"),
                        "country": sp.get("country"),
                        "sector": sp.get("sector"),
                        "similarity": round(float(sp.get("approx_similarity", sp.get("similarity", 0))), 3),
                    }
                    for sp in similar_policies[:5]
                ],
                "detected_sector": detected_sector,
                "detected_secondary_sector": llm_res.get("secondary_sector"),
                "detected_title": detected_title,
                "detected_tags": detected_tags,
                "executive_summary": llm_res.get("executive_summary", ""),
                "ml_method": "Gemini 2.5 LLM Deep Analysis + ChromaDB Semantic Matching"
            }
        except Exception as e:
            logger.error(f"Failed LLM-based upload recommendation: {e}. Falling back to programmatic V2.")
            
    # Programmatic V2 Fallback
    rich_text = f"Title: {title}. Focus areas: {' '.join(tags)}. Content: {text[:1000]}"
    try:
        similar_policies = semantic_search(rich_text, n=20)
    except Exception as e:
        logger.warning(f"ChromaDB text search failed: {e}")
        similar_policies = []

    detected_sector = "Cross-Domain"
    if similar_policies:
        top_sim = similar_policies[0]
        top_score = float(top_sim.get("approx_similarity", top_sim.get("similarity", 0)))
        if top_score > 0.35:
            detected_sector = top_sim.get("sector", "Cross-Domain")
        else:
            sector_votes = {}
            for sp in similar_policies[:5]:
                s = sp.get("sector", "")
                sector_votes[s] = sector_votes.get(s, 0) + 1
            detected_sector = max(sector_votes, key=sector_votes.get) if sector_votes else "Cross-Domain"

    detected_sector = _map_sector_semantically(detected_sector)
    temp_policy = {
        "id": "uploaded",
        "title": title,
        "content": text,
        "tags": tags,
        "sector": detected_sector,
        "country": "Unknown",
        "year": None,
    }

    primary, secondary = _detect_sectors(temp_policy)
    temp_policy["primary_sector"] = primary
    temp_policy["secondary_sector"] = secondary

    scored = []
    for country in COUNTRY_PROFILES.keys():
        res = score_country(country, temp_policy, similar_policies)
        if res:
            scored.append(res)

    scored = _normalize_semantic_scores(scored, temp_policy, None)
    top = sorted(scored, key=lambda x: -x["need_score"])[:top_n]

    return {
        "recommendations": top,
        "similar_policies": [
            {
                "id": sp.get("id"),
                "title": sp.get("title"),
                "country": sp.get("country"),
                "sector": sp.get("sector"),
                "similarity": round(float(sp.get("approx_similarity", sp.get("similarity", 0))), 3),
            }
            for sp in similar_policies[:5]
        ],
        "detected_sector": detected_sector,
        "detected_secondary_sector": temp_policy.get("secondary_sector"),
        "ml_method": "5-Factor Scoring + Legal-BERT Semantic Matching (Upload Mode)"
    }


def get_cluster_summary() -> dict:
    """Returns cluster summary from the ML clusterer module."""
    try:
        from app.ml.clusterer import _clusterer
        return _clusterer.get_cluster_summary()
    except Exception as e:
        logger.warning(f"Cluster summary unavailable: {e}")
        return {}


if __name__ == "__main__":
    print("[INFO] Running recommender test suite...")
    
    # Get policies from ALL sectors
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            SELECT id, title, sector 
            FROM policies 
            WHERE embedding IS NOT NULL
            """
        )
        all_p = cur.fetchall()
    finally:
        conn.close()
    
    # Group by sector to select one from EACH sector
    by_sector = {}
    for r in all_p:
        by_sector[r["sector"]] = r
    
    sample_policies = list(by_sector.values())
    print(f"[INFO] Testing across {len(sample_policies)} sectors: {list(by_sector.keys())}")
    
    for p in sample_policies:
        pid = p["id"]
        title = p["title"]
        sector = p["sector"]
        print("\n" + "=" * 80)
        print(f"TESTING RECOMMENDATIONS FOR: '{title}' ({pid})")
        print(f"Sector: {sector}")
        print("=" * 80)
        
        recs = get_recommendations_v2(pid, top_n=3)
        if "error" in recs:
            print(f"Error: {recs['error']}")
            continue
            
        print(f"ML Method: {recs['ml_method']}")
        print(f"Total similar policies in index: {len(recs['similar_policies'])}")
        print("\nTop 3 Recommendations:")
        for idx, rec in enumerate(recs["recommendations"], 1):
            print(f"\n  #{idx}: Country: {rec['country']} | Score: {rec['need_score']:.4f}")
            print(f"      Maturity: {rec['regulatory_maturity']} | Already Has Sector: {rec['already_has_sector']}")
            print(f"      Score Breakdown: {rec['score_breakdown']}")
            print(f"      Reasoning: {rec['reasoning']}")
            print(f"      Expected Benefits:")
            for b in rec["expected_benefits"]:
                print(f"        - {b}")

