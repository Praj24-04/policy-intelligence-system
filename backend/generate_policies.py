import json
import random
import os

sectors = [
    'POSH Policies', 'Healthcare AI', 'Cybersecurity', 'AI Governance',
    'Financial Regulation', 'IoT and Robotics', 'Data Privacy', 'ESG Policies'
]

regions_countries = [
    ('North America', 'United States'), ('North America', 'Canada'), ('North America', 'Mexico'),
    ('Europe', 'European Union'), ('Europe', 'United Kingdom'), ('Europe', 'Germany'), ('Europe', 'France'), ('Europe', 'Italy'), ('Europe', 'Russia'),
    ('Asia', 'India'), ('Asia', 'Singapore'), ('Asia', 'Japan'), ('Asia', 'South Korea'), ('Asia', 'China'),
    ('Oceania', 'Australia'), ('Oceania', 'New Zealand'),
    ('South America', 'Brazil'), ('South America', 'Argentina'),
    ('Africa', 'South Africa'), ('Africa', 'Nigeria'),
    ('Global', 'International')
]

templates = {
    'POSH Policies': {
        'titles': ['{country} Workplace Anti-Harassment Directive', '{country} Equality and Inclusion Act', '{country} POSH Compliance Framework', 'National Guidelines on Workplace Safety in {country}', '{country} Sexual Harassment Prevention Bill'],
        'contents': ['Mandates the constitution of an internal committee for harassment prevention.', 'Provides comprehensive guidelines for employer liability regarding workplace inclusion.', 'Requires regular training for all employees on anti-harassment protocols.', 'Establishes a legal framework for reporting and resolving workplace misconduct.', 'Sets mandatory compliance standards for organizations operating in {country} regarding employee safety.'],
        'tags': ['Workplace Safety', 'Compliance', 'Harassment Prevention', 'Equality', 'HR Policy']
    },
    'Healthcare AI': {
        'titles': ['{country} Medical Device AI Regulation', '{country} SaMD Safety Framework', 'Healthcare Algorithm Guidelines - {country}', '{country} Digital Health Act', 'Clinical AI Evaluation Standard for {country}'],
        'contents': ['Regulatory requirements for AI systems classified as medical devices.', 'Ensures continuous learning algorithms meet safety and effectiveness standards.', 'Guidelines for ethical AI use in diagnostics and patient care.', 'Establishes a sandbox for testing AI technologies in the national healthcare system.', 'Mandates rigorous clinical evaluation for any AI deployment in hospitals.'],
        'tags': ['SaMD', 'Algorithm Safety', 'Medical Device', 'Digital Health', 'Ethics']
    },
    'Cybersecurity': {
        'titles': ['{country} Cybersecurity Resilience Act', '{country} Critical Infrastructure Protection Bill', 'National Cyber Incident Reporting Directive ({country})', '{country} Zero Trust Architecture Mandate', 'Information Security Standards of {country}'],
        'contents': ['Mandates cyber incident reporting within 24 hours for critical infrastructure.', 'Guidelines to assist agencies in implementing Zero Trust architecture.', 'Requires mandatory security audits for all medium and large enterprises.', 'Establishes a national framework for defending against ransomware and cyber threats.', 'Imposes strict supply chain security requirements for software vendors.'],
        'tags': ['Resilience', 'Incident Reporting', 'Zero Trust', 'Information Security', 'Critical Infrastructure']
    },
    'AI Governance': {
        'titles': ['{country} Artificial Intelligence Act', '{country} Trustworthy AI Blueprint', 'Generative AI Regulatory Measures in {country}', '{country} Algorithmic Accountability Act', 'National AI Strategy and Governance ({country})'],
        'contents': ['A comprehensive legal framework categorizing AI systems by risk level.', 'Principles guiding the design and deployment of automated systems to protect civil rights.', 'Requires algorithm registration and security assessments for generative AI models.', 'Focuses on bias mitigation, transparency, and human oversight in AI deployments.', 'Promotes innovative but trustworthy AI that respects democratic values.'],
        'tags': ['AI Act', 'Trustworthy AI', 'Bias Mitigation', 'Transparency', 'Algorithmic Accountability']
    },
    'Financial Regulation': {
        'titles': ['{country} Financial Services and Markets Act', '{country} Digital Asset Regulation Framework', 'Banking Resilience and Capital Act - {country}', '{country} FinTech and Payments Directive', 'Market Transparency Guidelines ({country})'],
        'contents': ['Regulates financial markets to improve transparency and protect investors.', 'Overhauls national financial regulation, bringing crypto-assets into the perimeter.', 'Global regulatory standard on bank capital adequacy and stress testing.', 'Consolidated framework for the regulation of payment systems and digital tokens.', 'Imposes strict capital requirements and systemic risk mitigation strategies.'],
        'tags': ['Market Transparency', 'Digital Assets', 'Capital Adequacy', 'Investor Protection', 'FinTech']
    },
    'IoT and Robotics': {
        'titles': ['{country} IoT Security Standard', '{country} Product Security and Telecom Act', 'Connected Devices Safety Mandate ({country})', '{country} Industrial Robotics Compliance Code', 'Smart Home Device Regulation in {country}'],
        'contents': ['Requires manufacturers of connectable products to comply with minimum security standards.', 'Mandates that connected devices are equipped with unique passwords and reasonable security.', 'Introduces mandatory cybersecurity requirements for hardware with digital elements.', 'Guidelines to promote security by design in IoT systems across national infrastructure.', 'International standard detailing safety requirements for industrial robot integration.'],
        'tags': ['IoT Security', 'Connected Devices', 'Hardware Security', 'Robotics', 'Security by Design']
    },
    'Data Privacy': {
        'titles': ['{country} General Data Protection Act', '{country} Consumer Privacy Rights Bill', 'Digital Personal Data Protection Framework ({country})', '{country} Privacy and Electronic Communications Directive', 'National Data Sovereignty Law - {country}'],
        'contents': ['Comprehensive data privacy law giving citizens control over their personal data.', 'Enhances privacy rights, providing the right to know, delete, and opt-out of data sales.', 'Regulates the processing of personal data and establishes a national data protection authority.', 'Tightens rules on cross-border data transfers and mandates data breach reporting.', 'Balances individual rights with lawful data processing requirements for businesses.'],
        'tags': ['Data Privacy', 'Consumer Rights', 'Cross-Border Transfers', 'Consent', 'Data Protection Authority']
    },
    'ESG Policies': {
        'titles': ['{country} Corporate Sustainability Reporting Directive', '{country} Climate-Related Disclosure Rules', 'National Green Transition Plan ({country})', '{country} Energy and Carbon Reporting Mandate', 'Sustainable Finance Framework - {country}'],
        'contents': ['Mandates comprehensive sustainability reporting for large public companies.', 'Requires disclosure of climate-related risks and greenhouse gas emissions in annual filings.', 'National sustainability movement charting ambitious targets for sustainable development.', 'Obligates companies to disclose their energy efficiency and carbon emissions data.', 'Framework for voluntary and consistent climate-related financial risk disclosures.'],
        'tags': ['Sustainability', 'Climate Risk', 'GHG Emissions', 'Green Transition', 'ESG Reporting']
    }
}

generated_policies = []

for sector in sectors:
    for i in range(80):
        region, country = random.choice(regions_countries)
        title_template = random.choice(templates[sector]['titles'])
        content_template = random.choice(templates[sector]['contents'])
        
        year = random.randint(2015, 2024)
        title = title_template.format(country=country)
        if random.random() > 0.5:
            title += f' {year}'
            
        content = content_template.format(country=country)
        tags = random.sample(templates[sector]['tags'], k=3)
        
        policy = {
            'title': title,
            'sector': sector,
            'region': region,
            'country': country,
            'content': content,
            'tags': tags,
            'year': year,
            'source_url': 'https://www.google.com/search?q=' + title.replace(' ', '+')
        }
        generated_policies.append(policy)

with open('data/global_policies_stream.json', 'w') as f:
    json.dump({'policies': generated_policies}, f, indent=4)

print(f'Generated {len(generated_policies)} policies.')
