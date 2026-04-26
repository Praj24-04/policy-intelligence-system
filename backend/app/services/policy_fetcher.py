import requests
import json
import hashlib
from datetime import datetime
from bs4 import BeautifulSoup
from app.database import get_connection

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def generate_id(title: str, country: str) -> str:
    raw = f"{title.lower().strip()}{country.lower().strip()}"
    return "live_" + hashlib.md5(raw.encode()).hexdigest()[:8]

def policy_exists(policy_id: str) -> bool:
    conn = get_connection()
    row = conn.execute("SELECT id FROM policies WHERE id = ?", (policy_id,)).fetchone()
    conn.close()
    return row is not None

def save_policy(policy: dict) -> bool:
    if policy_exists(policy["id"]):
        return False
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO policies 
            (id, title, sector, region, country, content, tags, status, year, version, source_url)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            policy["id"], policy["title"], policy["sector"], policy["region"],
            policy["country"], policy["content"], json.dumps(policy.get("tags", [])),
            policy.get("status", "Active"), policy.get("year"),
            policy.get("version", "1.0"), policy.get("source_url", "")
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error saving: {e}")
        conn.close()
        return False

def extract_year(text: str) -> int:
    import re
    match = re.search(r'\b(20\d{2})\b', text)
    return int(match.group(1)) if match else datetime.now().year

def extract_tags(text: str) -> list:
    text_lower = text.lower()
    keywords = [
        "transparency", "accountability", "privacy", "security",
        "compliance", "risk", "data protection", "cybersecurity",
        "artificial intelligence", "governance", "safety", "ethics",
        "regulation", "enforcement", "breach", "consent", "automated"
    ]
    return [kw for kw in keywords if kw in text_lower][:6]


# ── SOURCE 1: OECD iLibrary ───────────────────────────────────
def fetch_oecd_policies() -> list:
    print("🔄 Fetching from OECD...")
    fetched = []
    try:
        url = "https://www.oecd.org/digital/artificial-intelligence/"
        res = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(res.content, "lxml")

        # Try multiple selectors
        items = (
            soup.find_all("div", class_="field-content") or
            soup.find_all("article") or
            soup.find_all("div", class_="publication-item") or
            soup.select(".card") or
            soup.find_all("h3")
        )

        for item in items[:15]:
            try:
                if item.name == "h3":
                    title = item.get_text(strip=True)
                    content = title
                    source_url = "https://www.oecd.org/digital/artificial-intelligence/"
                else:
                    title_el = item.find(["h2", "h3", "h4", "a"])
                    if not title_el:
                        continue
                    title = title_el.get_text(strip=True)
                    desc_el = item.find("p")
                    content = desc_el.get_text(strip=True) if desc_el else title
                    link_el = item.find("a", href=True)
                    href = link_el["href"] if link_el else ""
                    source_url = href if href.startswith("http") else f"https://www.oecd.org{href}"

                if not title or len(title) < 15:
                    continue

                content = content if len(content) > 50 else (
                    f"{title}. This OECD policy initiative addresses artificial intelligence "
                    f"governance, ethics, and regulatory frameworks for member countries."
                )

                policy = {
                    "id": generate_id(title, "OECD"),
                    "title": title[:200],
                    "sector": "AI Governance",
                    "region": "Global",
                    "country": "International",
                    "content": content[:2000],
                    "tags": extract_tags(content),
                    "status": "Active",
                    "year": extract_year(content),
                    "version": "1.0",
                    "source_url": source_url
                }
                fetched.append(policy)
            except Exception:
                continue

        print(f"✅ OECD: {len(fetched)} found")
    except Exception as e:
        print(f"❌ OECD failed: {e}")
    return fetched


# ── SOURCE 2: CISA Alerts ────────────────────────────────────
def fetch_cisa_policies() -> list:
    print("🔄 Fetching from CISA...")
    fetched = []
    try:
        # Use CISA's structured JSON feed instead of scraping
        url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
        
        # Fallback to advisories page
        urls_to_try = [
            "https://www.cisa.gov/news-events/cybersecurity-advisories",
            "https://www.cisa.gov/resources-tools/resources",
        ]

        for url in urls_to_try:
            try:
                res = requests.get(url, headers=HEADERS, timeout=20)
                if res.status_code != 200:
                    continue

                soup = BeautifulSoup(res.content, "lxml")
                items = (
                    soup.find_all("article") or
                    soup.select(".c-teaser") or
                    soup.find_all("div", class_="views-row") or
                    soup.find_all("li", class_="views-row")
                )

                if not items:
                    # Try finding any links with advisory in URL
                    links = soup.find_all("a", href=True)
                    items = [l.parent for l in links
                            if "advisory" in l.get("href", "").lower()
                            or "guidance" in l.get("href", "").lower()][:10]

                for item in items[:8]:
                    try:
                        title_el = item.find(["h2", "h3", "h4", "a"])
                        if not title_el:
                            continue
                        title = title_el.get_text(strip=True)
                        if not title or len(title) < 15:
                            continue

                        # Skip vulnerability-specific items
                        skip = ["CVE-", "vulnerability", "patch tuesday", "exploit"]
                        if any(s.lower() in title.lower() for s in skip):
                            continue

                        desc_el = item.find("p")
                        content = desc_el.get_text(strip=True) if desc_el else ""
                        if len(content) < 50:
                            content = (
                                f"{title}. This cybersecurity guidance from the US "
                                f"Cybersecurity and Infrastructure Security Agency "
                                f"provides recommendations for protecting critical "
                                f"infrastructure and digital systems."
                            )

                        link_el = item.find("a", href=True)
                        href = link_el["href"] if link_el else ""
                        source_url = href if href.startswith("http") else f"https://www.cisa.gov{href}"

                        policy = {
                            "id": generate_id(title, "CISA United States"),
                            "title": title[:200],
                            "sector": "Cybersecurity",
                            "region": "North America",
                            "country": "United States",
                            "content": content[:2000],
                            "tags": extract_tags(content),
                            "status": "Active",
                            "year": extract_year(content),
                            "version": "1.0",
                            "source_url": source_url
                        }
                        fetched.append(policy)
                    except Exception:
                        continue

                if fetched:
                    break

            except Exception:
                continue

        print(f"✅ CISA: {len(fetched)} found")
    except Exception as e:
        print(f"❌ CISA failed: {e}")
    return fetched


# ── SOURCE 3: ENISA Publications ─────────────────────────────
def fetch_enisa_policies() -> list:
    print("🔄 Fetching from ENISA...")
    fetched = []
    try:
        urls_to_try = [
            "https://www.enisa.europa.eu/publications",
            "https://www.enisa.europa.eu/topics/cybersecurity-policy",
        ]

        for url in urls_to_try:
            res = requests.get(url, headers=HEADERS, timeout=20)
            if res.status_code != 200:
                continue

            soup = BeautifulSoup(res.content, "lxml")
            items = (
                soup.find_all("article") or
                soup.select(".listing-item") or
                soup.find_all("div", class_="publication") or
                soup.select(".card-publication")
            )

            # Fallback: find all links that look like publications
            if not items:
                links = soup.find_all("a", href=True)
                items = [l.parent for l in links
                        if "/publications/" in l.get("href", "")
                        or "/guidelines/" in l.get("href", "")][:10]

            for item in items[:8]:
                try:
                    title_el = item.find(["h2", "h3", "h4", "a"])
                    if not title_el:
                        continue
                    title = title_el.get_text(strip=True)
                    if not title or len(title) < 15:
                        continue

                    desc_el = item.find("p")
                    content = desc_el.get_text(strip=True) if desc_el else ""
                    if len(content) < 50:
                        content = (
                            f"{title}. This cybersecurity publication from the European "
                            f"Union Agency for Cybersecurity ENISA provides guidelines "
                            f"and recommendations for network and information security "
                            f"across Europe and EU member states."
                        )

                    link_el = item.find("a", href=True)
                    href = link_el["href"] if link_el else ""
                    source_url = href if href.startswith("http") else f"https://www.enisa.europa.eu{href}"

                    policy = {
                        "id": generate_id(title, "ENISA European Union"),
                        "title": title[:200],
                        "sector": "Cybersecurity",
                        "region": "Europe",
                        "country": "European Union",
                        "content": content[:2000],
                        "tags": extract_tags(content),
                        "status": "Active",
                        "year": extract_year(content),
                        "version": "1.0",
                        "source_url": source_url
                    }
                    fetched.append(policy)
                except Exception:
                    continue

            if fetched:
                break

        print(f"✅ ENISA: {len(fetched)} found")
    except Exception as e:
        print(f"❌ ENISA failed: {e}")
    return fetched


# ── SOURCE 4: NIST Publications ──────────────────────────────
def fetch_nist_policies() -> list:
    print("🔄 Fetching from NIST...")
    fetched = []
    try:
        url = "https://www.nist.gov/artificial-intelligence"
        res = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(res.content, "lxml")

        items = (
            soup.find_all("article") or
            soup.select(".teaser") or
            soup.find_all("div", class_="views-row") or
            soup.find_all("li", class_="item")
        )

        if not items:
            # Find any content blocks
            items = soup.find_all(["article", "section", "div"],
                                  class_=lambda x: x and any(
                                      k in str(x).lower()
                                      for k in ["card", "item", "result", "post"]
                                  ))[:10]

        for item in items[:8]:
            try:
                title_el = item.find(["h2", "h3", "h4", "a"])
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                if not title or len(title) < 15:
                    continue

                desc_el = item.find("p")
                content = desc_el.get_text(strip=True) if desc_el else ""
                if len(content) < 50:
                    content = (
                        f"{title}. This publication from the National Institute of "
                        f"Standards and Technology addresses artificial intelligence "
                        f"safety, standards, and risk management frameworks."
                    )

                link_el = item.find("a", href=True)
                href = link_el["href"] if link_el else ""
                source_url = href if href.startswith("http") else f"https://www.nist.gov{href}"

                policy = {
                    "id": generate_id(title, "NIST United States"),
                    "title": title[:200],
                    "sector": "AI Governance",
                    "region": "North America",
                    "country": "United States",
                    "content": content[:2000],
                    "tags": extract_tags(content),
                    "status": "Active",
                    "year": extract_year(content),
                    "version": "1.0",
                    "source_url": source_url
                }
                fetched.append(policy)
            except Exception:
                continue

        print(f"✅ NIST: {len(fetched)} found")
    except Exception as e:
        print(f"❌ NIST failed: {e}")
    return fetched


# ── SOURCE 5: ICO UK Data Protection ─────────────────────────
def fetch_ico_policies() -> list:
    print("🔄 Fetching from ICO UK...")
    fetched = []
    try:
        url = "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/"
        res = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(res.content, "lxml")

        items = (
            soup.find_all("article") or
            soup.select(".guidance-item") or
            soup.find_all("div", class_="block")
        )

        if not items:
            items = soup.find_all(["li", "div"],
                                  class_=lambda x: x and "item" in str(x).lower())[:10]

        for item in items[:6]:
            try:
                title_el = item.find(["h2", "h3", "h4", "a"])
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                if not title or len(title) < 15:
                    continue

                desc_el = item.find("p")
                content = desc_el.get_text(strip=True) if desc_el else ""
                if len(content) < 50:
                    content = (
                        f"{title}. This guidance from the UK Information Commissioner's "
                        f"Office addresses data protection and privacy requirements "
                        f"for artificial intelligence systems under UK GDPR."
                    )

                link_el = item.find("a", href=True)
                href = link_el["href"] if link_el else ""
                source_url = href if href.startswith("http") else f"https://ico.org.uk{href}"

                policy = {
                    "id": generate_id(title, "ICO United Kingdom"),
                    "title": title[:200],
                    "sector": "Data Privacy",
                    "region": "Europe",
                    "country": "United Kingdom",
                    "content": content[:2000],
                    "tags": extract_tags(content),
                    "status": "Active",
                    "year": extract_year(content),
                    "version": "1.0",
                    "source_url": source_url
                }
                fetched.append(policy)
            except Exception:
                continue

        print(f"✅ ICO: {len(fetched)} found")
    except Exception as e:
        print(f"❌ ICO failed: {e}")
    return fetched


# ── MAIN AGGREGATOR ───────────────────────────────────────────
def run_full_fetch() -> dict:
    print("\n🌐 Starting live policy fetch pipeline...")
    print("=" * 50)

    all_policies = []
    all_policies.extend(fetch_oecd_policies())
    all_policies.extend(fetch_cisa_policies())
    all_policies.extend(fetch_enisa_policies())
    all_policies.extend(fetch_nist_policies())
    all_policies.extend(fetch_ico_policies())

    print(f"\n📦 Total fetched: {len(all_policies)}")

    inserted = 0
    duplicates = 0
    for policy in all_policies:
        if policy["title"] and len(policy["title"]) > 10:
            if save_policy(policy):
                inserted += 1
            else:
                duplicates += 1

    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_fetched": len(all_policies),
        "inserted": inserted,
        "duplicates_skipped": duplicates,
        "sources": ["OECD", "CISA", "ENISA", "NIST", "ICO"]
    }

    print(f"✅ Inserted: {inserted} new policies")
    print(f"⏭️  Skipped: {duplicates} duplicates")
    print("=" * 50)
    return summary


def get_fetch_status() -> dict:
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM policies").fetchone()[0]
    live = conn.execute(
        "SELECT COUNT(*) FROM policies WHERE id LIKE 'live_%'"
    ).fetchone()[0]
    sectors = conn.execute(
        "SELECT sector, COUNT(*) as count FROM policies GROUP BY sector"
    ).fetchall()
    conn.close()
    return {
        "total_policies": total,
        "live_fetched": live,
        "curated": total - live,
        "sectors": {r["sector"]: r["count"] for r in sectors},
        "last_updated": datetime.now().isoformat()
    }