import sys
import os
import numpy as np
sys.path.insert(0, '.')
from app.ml.recommender_v2 import (
    _detect_sectors,
    _map_sector_semantically,
    DynamicCountryProfiles,
    load_country_profiles_from_db,
    get_recommendations_v2,
    embed_text
)

# 1. Test sector detection
def test_sector_classification():
    print("Testing _detect_sectors...")
    # Test case: privacy act
    policy1 = {
        "title": "Privacy Protection Act of 2026",
        "content": "This bill protects consumer privacy and data rights. It regulates how personal data is processed by financial institutions and fintech banks during payment transactions.",
        "tags": ["privacy", "data-protection", "fintech"]
    }
    pri, sec = _detect_sectors(policy1)
    print(f"policy1 results: primary={pri}, secondary={sec}")
    assert pri == "Data Privacy", f"Expected Data Privacy, got {pri}"
    assert sec == "Financial Regulation", f"Expected Financial Regulation as secondary, got {sec}"
    
    # Test case: cyber security and infrastructure
    policy2 = {
        "title": "Cybersecurity Incident Reporting Act",
        "content": "This bill establishes mandatory cyber incident reporting requirements for critical infrastructure operators, including energy grid, financial networks, and healthcare sectors.",
        "tags": ["cybersecurity", "infrastructure"]
    }
    pri2, sec2 = _detect_sectors(policy2)
    print(f"policy2 results: primary={pri2}, secondary={sec2}")
    assert pri2 == "Cybersecurity", f"Expected Cybersecurity, got {pri2}"
    print("PASS: _detect_sectors passed!")

# 2. Test semantic sector similarities
def test_semantic_sector_mapping():
    print("\nTesting _map_sector_semantically...")
    official_sectors = [
        "AI Governance", "Cybersecurity", "Data Privacy", "Financial Regulation",
        "ESG Policies", "IoT and Robotics", "Healthcare AI", "Healthcare & Clinical Trials", "POSH Policies"
    ]
    
    # Test case 1: Medical and health AI systems
    custom_sector1 = "Medical health and clinical diagnostic technology"
    custom_vec = embed_text(custom_sector1)
    print(f"Similarities for '{custom_sector1}':")
    for s in official_sectors:
        v = embed_text(s)
        sim = np.dot(custom_vec, v) / (np.linalg.norm(custom_vec) * np.linalg.norm(v))
        print(f"  {s}: {sim:.4f}")
        
    mapped1 = _map_sector_semantically(custom_sector1)
    print(f"Mapped to: {mapped1}")
    assert mapped1 in ["Healthcare AI", "Healthcare & Clinical Trials"], f"Expected Healthcare AI or Clinical Trials, got {mapped1}"
    
    # Test case 2: Workplace harassment rules
    custom_sector2 = "Workplace harassment prevention rules"
    custom_vec2 = embed_text(custom_sector2)
    print(f"Similarities for '{custom_sector2}':")
    for s in official_sectors:
        v = embed_text(s)
        sim = np.dot(custom_vec2, v) / (np.linalg.norm(custom_vec2) * np.linalg.norm(v))
        print(f"  {s}: {sim:.4f}")
        
    mapped2 = _map_sector_semantically(custom_sector2)
    print(f"Mapped to: {mapped2}")
    assert mapped2 == "POSH Policies", f"Expected POSH Policies, got {mapped2}"
    print("PASS: _map_sector_semantically passed!")

# 3. Test dynamic country profiles database-backed loader
def test_dynamic_profiles():
    print("\nTesting DynamicCountryProfiles and database-backed lookup...")
    profiles = load_country_profiles_from_db()
    assert isinstance(profiles, dict)
    assert len(profiles) > 0
    print(f"Loaded {len(profiles)} country profiles from database.")
    
    # Check key structure
    sample_country = list(profiles.keys())[0]
    sample_profile = profiles[sample_country]
    print(f"Sample country: {sample_country}")
    print(f"Sample profile data: {sample_profile}")
    assert "region" in sample_profile
    assert "gdp_tier" in sample_profile
    assert "regulatory_maturity" in sample_profile
    assert "context" in sample_profile
    assert "priority_needs" in sample_profile
    assert "existing_sectors" in sample_profile
    assert isinstance(sample_profile["priority_needs"], list)
    assert isinstance(sample_profile["existing_sectors"], list)
    print("PASS: load_country_profiles_from_db passed!")

if __name__ == "__main__":
    test_sector_classification()
    test_semantic_sector_mapping()
    test_dynamic_profiles()
    print("\nAll tests completed successfully!")
