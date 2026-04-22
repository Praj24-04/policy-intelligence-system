POLICIES = [

    # ─────────────────────────────────────────
    # SECTOR 1: AI GOVERNANCE (10 policies)
    # ─────────────────────────────────────────
    {
        "id": "aig_001",
        "title": "EU AI Act — Risk-Based AI Regulation",
        "sector": "AI Governance",
        "region": "Europe",
        "country": "European Union",
        "content": (
            "The European Union AI Act establishes a comprehensive risk-based framework "
            "for regulating artificial intelligence across all EU member states. "
            "High-risk AI systems used in critical infrastructure, education, employment, "
            "healthcare, and law enforcement must meet strict requirements for transparency, "
            "accuracy, and human oversight before market placement. "
            "Providers of general-purpose AI models must conduct adversarial testing and "
            "publish technical documentation. Non-compliance carries fines up to 35 million "
            "euros or 7 percent of global annual turnover."
        ),
        "tags": ["risk-based", "compliance", "transparency", "high-risk AI"],
        "status": "Active",
        "year": 2024,
        "version": "1.0",
        "source_url": "https://artificialintelligenceact.eu/the-act/"
    },
    {
        "id": "aig_002",
        "title": "US Executive Order on Safe and Trustworthy AI",
        "sector": "AI Governance",
        "region": "North America",
        "country": "United States",
        "content": (
            "The United States Executive Order on Artificial Intelligence directs federal "
            "agencies to evaluate and manage AI safety risks across government operations. "
            "Developers of the most powerful foundation models must share safety test results "
            "with the federal government before public deployment. "
            "The National Institute of Standards and Technology leads AI safety benchmarking, "
            "and the Department of Homeland Security assesses AI risks to critical infrastructure. "
            "The order also addresses AI-generated content watermarking and privacy protections."
        ),
        "tags": ["safety", "federal", "foundation models", "watermarking"],
        "status": "Active",
        "year": 2023,
        "version": "1.0",
        "source_url": "https://www.whitehouse.gov/briefing-room/presidential-actions/2023/10/30/executive-order-on-the-safe-secure-and-trustworthy-development-and-use-of-artificial-intelligence/"
    },
    {
        "id": "aig_003",
        "title": "India National AI Strategy — Responsible AI for All",
        "sector": "AI Governance",
        "region": "Asia",
        "country": "India",
        "content": (
            "India's National AI Strategy developed by NITI Aayog emphasizes responsible AI "
            "development with social inclusion as a core principle. "
            "Priority sectors include agriculture, healthcare, education, smart cities, and "
            "financial services. The strategy mandates fairness, accountability, and "
            "transparency in government AI deployments. "
            "India's Digital Personal Data Protection Act 2023 complements this by regulating "
            "personal data used in AI training. The government targets making India a global "
            "AI hub with significant investment in AI research infrastructure."
        ),
        "tags": ["responsible AI", "social inclusion", "DPDP", "national strategy"],
        "status": "Active",
        "year": 2023,
        "version": "2.1",
        "source_url": "https://www.niti.gov.in/sites/default/files/2023-03/National-Strategy-for-Artificial-Intelligence.pdf"
    },
    {
        "id": "aig_004",
        "title": "China AI Governance — Generative AI Interim Measures",
        "sector": "AI Governance",
        "region": "Asia",
        "country": "China",
        "content": (
            "China's Interim Measures for the Management of Generative Artificial Intelligence "
            "Services require providers to conduct security assessments before launching "
            "generative AI products to the public. "
            "AI-generated content must be clearly watermarked to prevent misinformation. "
            "The Cyberspace Administration of China oversees compliance and mandates that "
            "training data must not violate intellectual property rights. "
            "Algorithmic recommendation systems must be transparent and allow users to opt out. "
            "Providers must prevent AI-generated content that subverts state power."
        ),
        "tags": ["generative AI", "watermarking", "security assessment", "algorithmic transparency"],
        "status": "Active",
        "year": 2023,
        "version": "1.2",
        "source_url": "https://www.cac.gov.cn/2023-07/13/c_1690898327029107.htm"
    },
    {
        "id": "aig_005",
        "title": "UK Pro-Innovation AI Regulatory Framework",
        "sector": "AI Governance",
        "region": "Europe",
        "country": "United Kingdom",
        "content": (
            "The United Kingdom adopts a principles-based, pro-innovation approach to AI "
            "regulation rather than prescriptive legislation. "
            "Existing sector regulators including the FCA for financial services, "
            "CMA for competition, and ICO for data protection apply their frameworks to AI. "
            "Core principles include safety, security, fairness, transparency, accountability, "
            "and contestability. The UK AI Safety Institute was established to evaluate "
            "frontier AI models. The framework positions the UK as a global AI hub "
            "while managing systemic risks."
        ),
        "tags": ["pro-innovation", "principles-based", "AI Safety Institute", "sector-specific"],
        "status": "Active",
        "year": 2023,
        "version": "1.0",
        "source_url": "https://www.gov.uk/government/publications/ai-regulation-a-pro-innovation-approach"
    },
    {
        "id": "aig_006",
        "title": "Canada Directive on Automated Decision Making",
        "sector": "AI Governance",
        "region": "North America",
        "country": "Canada",
        "content": (
            "Canada's Directive on Automated Decision-Making applies to all federal government "
            "institutions using automated systems to make or support administrative decisions. "
            "A four-level impact assessment determines the degree of human oversight required. "
            "Level three and four impact decisions require human review before any action is taken. "
            "Citizens must be notified when automated systems significantly affect their rights. "
            "The directive mandates peer reviews, algorithm audits, and bias testing for high-impact "
            "AI systems used in immigration, benefits, and law enforcement contexts."
        ),
        "tags": ["automated decisions", "human oversight", "impact assessment", "federal"],
        "status": "Active",
        "year": 2023,
        "version": "2.0",
        "source_url": "https://www.tbs-sct.canada.ca/pol/doc-eng.aspx?id=32592"
    },
    {
        "id": "aig_007",
        "title": "Singapore Model AI Governance Framework",
        "sector": "AI Governance",
        "region": "Asia",
        "country": "Singapore",
        "content": (
            "Singapore's Model AI Governance Framework provides detailed, practical guidance "
            "for private sector organizations deploying AI. "
            "The framework focuses on human-centric AI with emphasis on explainable decision-making. "
            "It covers internal governance structures, risk management, operations management, "
            "and stakeholder interaction. "
            "Singapore's AI Verify testing toolkit allows organizations to validate AI systems "
            "against governance principles. The PDPC oversees data governance aspects while "
            "the IMDA leads broader AI governance initiatives including AI sandboxes."
        ),
        "tags": ["private sector", "human-centric", "AI Verify", "explainability"],
        "status": "Active",
        "year": 2022,
        "version": "2.0",
        "source_url": "https://www.pdpc.gov.sg/help-and-resources/2020/01/model-ai-governance-framework"
    },
    {
        "id": "aig_008",
        "title": "UNESCO Recommendation on the Ethics of AI",
        "sector": "AI Governance",
        "region": "Global",
        "country": "International",
        "content": (
            "The UNESCO Recommendation on the Ethics of Artificial Intelligence is the first "
            "global normative instrument on AI ethics adopted by 193 member states. "
            "It establishes core values including human rights, human dignity, living in "
            "peaceful societies, and environmental protection. "
            "The recommendation calls for member states to conduct ethical impact assessments "
            "before deploying AI, protect privacy, ensure inclusiveness, and prevent AI from "
            "being used for mass surveillance. It also mandates gender-responsive AI policies "
            "and AI literacy programs in education."
        ),
        "tags": ["ethics", "human rights", "global standards", "UNESCO", "inclusiveness"],
        "status": "Active",
        "year": 2021,
        "version": "1.0",
        "source_url": "https://www.unesco.org/en/artificial-intelligence/recommendation-ethics"
    },
    {
        "id": "aig_009",
        "title": "Australia AI Ethics Framework",
        "sector": "AI Governance",
        "region": "Oceania",
        "country": "Australia",
        "content": (
            "Australia's AI Ethics Framework defines eight voluntary principles for responsible "
            "AI development applicable to both government and private organizations. "
            "Principles include human-centered values, fairness, privacy protection, "
            "reliability and safety, transparency and explainability, contestability, "
            "and accountability. "
            "Federal government agencies must adopt the framework mandatorily while "
            "private organizations are encouraged to self-assess and publish AI ethics statements. "
            "Australia's National AI Centre coordinates adoption and provides tools for "
            "AI ethics implementation across sectors."
        ),
        "tags": ["ethics", "voluntary", "eight principles", "government mandate"],
        "status": "Active",
        "year": 2022,
        "version": "1.5",
        "source_url": "https://www.industry.gov.au/publications/australias-artificial-intelligence-ethics-framework"
    },
    {
        "id": "aig_010",
        "title": "OECD AI Principles — Intergovernmental Standard",
        "sector": "AI Governance",
        "region": "Global",
        "country": "International",
        "content": (
            "The OECD Principles on Artificial Intelligence provide an intergovernmental "
            "standard adopted by over 40 countries including all G20 members. "
            "The principles cover inclusive growth, sustainable development, human-centered "
            "values, transparency, explainability, robustness, security, and accountability. "
            "The OECD AI Policy Observatory tracks national AI policies and their alignment "
            "with these principles. Countries must report on implementation progress and share "
            "best practices. The framework serves as the foundation for many national AI "
            "governance strategies worldwide."
        ),
        "tags": ["OECD", "intergovernmental", "G20", "policy observatory", "global standard"],
        "status": "Active",
        "year": 2019,
        "version": "2.0",
        "source_url": "https://oecd.ai/en/ai-principles"
    },

    # ─────────────────────────────────────────
    # SECTOR 2: CYBERSECURITY (10 policies)
    # ─────────────────────────────────────────
    {
        "id": "cyb_001",
        "title": "NIST Cybersecurity Framework 2.0",
        "sector": "Cybersecurity",
        "region": "North America",
        "country": "United States",
        "content": (
            "The NIST Cybersecurity Framework 2.0 provides a comprehensive voluntary framework "
            "for managing cybersecurity risks across critical infrastructure and private sector. "
            "The framework is organized around six core functions: Govern, Identify, Protect, "
            "Detect, Respond, and Recover. "
            "Version 2.0 adds Govern as a new function emphasizing organizational cybersecurity "
            "strategy and supply chain risk management. "
            "Organizations use the framework to assess current cybersecurity posture, set target "
            "states, and communicate risk to executives and regulators. Over 50 countries have "
            "adopted or adapted the NIST CSF for national use."
        ),
        "tags": ["NIST", "CSF", "risk management", "critical infrastructure", "voluntary"],
        "status": "Active",
        "year": 2024,
        "version": "2.0",
        "source_url": "https://www.nist.gov/cyberframework"
    },
    {
        "id": "cyb_002",
        "title": "EU NIS2 Directive — Network and Information Security",
        "sector": "Cybersecurity",
        "region": "Europe",
        "country": "European Union",
        "content": (
            "The European Union NIS2 Directive significantly expands the scope of cybersecurity "
            "obligations across member states, replacing the original NIS Directive. "
            "Essential entities including energy, transport, banking, healthcare, and digital "
            "infrastructure must implement technical and organizational security measures. "
            "Important entities in manufacturing, postal services, and food production face "
            "lighter but still significant obligations. "
            "Organizations must report significant incidents within 24 hours to national authorities. "
            "Senior management can be held personally liable for cybersecurity failures. "
            "Fines reach up to 10 million euros or 2 percent of global annual turnover."
        ),
        "tags": ["NIS2", "essential entities", "incident reporting", "management liability"],
        "status": "Active",
        "year": 2023,
        "version": "2.0",
        "source_url": "https://www.enisa.europa.eu/topics/cybersecurity-policy/nis-directive-new"
    },
    {
        "id": "cyb_003",
        "title": "India CERT-In Cybersecurity Directions",
        "sector": "Cybersecurity",
        "region": "Asia",
        "country": "India",
        "content": (
            "India's CERT-In Cybersecurity Directions mandate that all government and private "
            "organizations operating in India report cybersecurity incidents within six hours "
            "of detection. "
            "Organizations must maintain logs of ICT systems for 180 days and provide them "
            "to CERT-In on demand. "
            "Virtual private network providers, cloud service providers, and cryptocurrency "
            "exchanges must register user data and maintain it for five years. "
            "Data centers must synchronize ICT systems with government-provided NTP servers. "
            "Non-compliance results in imprisonment up to one year or fine under the "
            "Information Technology Act 2000."
        ),
        "tags": ["CERT-In", "incident reporting", "log retention", "VPN", "India"],
        "status": "Active",
        "year": 2022,
        "version": "1.0",
        "source_url": "https://www.cert-in.org.in/PDF/CERT-In_Directions_70B_28.04.2022.pdf"
    },
    {
        "id": "cyb_004",
        "title": "UK National Cybersecurity Strategy 2022",
        "sector": "Cybersecurity",
        "region": "Europe",
        "country": "United Kingdom",
        "content": (
            "The United Kingdom National Cyber Strategy 2022 outlines a five-year roadmap "
            "to make the UK a leading responsible and democratic cyber power. "
            "Five pillars cover strengthening the cyber ecosystem, building resilient digital "
            "infrastructure, taking leadership in technologies critical to cybersecurity, "
            "advancing global influence, and detecting and disrupting adversaries. "
            "The National Cyber Security Centre provides technical guidance and manages "
            "Active Cyber Defence services that block malicious domains. "
            "The strategy invests 2.6 billion pounds in cyber defense capabilities."
        ),
        "tags": ["national strategy", "NCSC", "cyber power", "Active Cyber Defence"],
        "status": "Active",
        "year": 2022,
        "version": "1.0",
        "source_url": "https://www.gov.uk/government/publications/national-cyber-strategy-2022"
    },
    {
        "id": "cyb_005",
        "title": "ISO/IEC 27001 — Information Security Management",
        "sector": "Cybersecurity",
        "region": "Global",
        "country": "International",
        "content": (
            "ISO/IEC 27001 is the internationally recognized standard for establishing, "
            "implementing, maintaining, and continually improving information security "
            "management systems. "
            "Organizations seeking certification must conduct systematic risk assessments, "
            "implement 93 controls across organizational, people, physical, and technological "
            "domains, and undergo third-party audits. "
            "The 2022 update reorganized controls and introduced new controls covering "
            "cloud security, threat intelligence, and physical security monitoring. "
            "Over 70,000 organizations worldwide hold ISO 27001 certification across "
            "financial services, healthcare, government, and technology sectors."
        ),
        "tags": ["ISO 27001", "ISMS", "certification", "risk assessment", "global standard"],
        "status": "Active",
        "year": 2022,
        "version": "2022",
        "source_url": "https://www.iso.org/standard/27001"
    },
    {
        "id": "cyb_006",
        "title": "Australia Cybersecurity Strategy 2023-2030",
        "sector": "Cybersecurity",
        "region": "Oceania",
        "country": "Australia",
        "content": (
            "Australia's Cybersecurity Strategy 2023-2030 sets a vision for Australia to become "
            "the world's most cyber-secure nation by 2030. "
            "The strategy introduces a cyber shield concept with six shields covering strong "
            "cyber citizens, safe technology products, world-class threat sharing, protected "
            "critical infrastructure, sovereign capabilities, and resilient region and global "
            "leadership. "
            "Mandatory cybersecurity standards are established for smart devices sold in Australia. "
            "Critical infrastructure owners face mandatory incident reporting obligations and "
            "government assistance powers during significant cyber attacks."
        ),
        "tags": ["cyber shield", "smart devices", "critical infrastructure", "2030 vision"],
        "status": "Active",
        "year": 2023,
        "version": "1.0",
        "source_url": "https://www.homeaffairs.gov.au/cyber-security-subsite/files/2023-cyber-security-strategy.pdf"
    },
    {
        "id": "cyb_007",
        "title": "Singapore Cybersecurity Act",
        "sector": "Cybersecurity",
        "region": "Asia",
        "country": "Singapore",
        "content": (
            "Singapore's Cybersecurity Act provides a legal framework for the oversight and "
            "maintenance of national cybersecurity in Singapore. "
            "The Cyber Security Agency of Singapore oversees 11 critical information "
            "infrastructure sectors including energy, water, banking, healthcare, and transport. "
            "Owners of critical information infrastructure must conduct annual cybersecurity "
            "audits, submit incident reports within two hours, and participate in government "
            "cybersecurity exercises. "
            "The 2024 amendment extends obligations to major operators of digital infrastructure "
            "and foundational digital services such as cloud providers and data centers."
        ),
        "tags": ["Cybersecurity Act", "CII", "CSA", "incident reporting", "audit"],
        "status": "Active",
        "year": 2024,
        "version": "2.0",
        "source_url": "https://www.csa.gov.sg/our-programmes/legislation-and-licensing/cybersecurity-act"
    },
    {
        "id": "cyb_008",
        "title": "China Cybersecurity Law",
        "sector": "Cybersecurity",
        "region": "Asia",
        "country": "China",
        "content": (
            "China's Cybersecurity Law establishes a comprehensive legal framework for "
            "network security across all organizations operating in China. "
            "Network operators must implement tiered cybersecurity protection based on "
            "the multi-level protection scheme. "
            "Critical information infrastructure operators face additional obligations including "
            "data localization, security reviews for technology purchases, and annual security "
            "assessments. "
            "The law requires real-name registration for internet users and mandates cooperation "
            "with government authorities during national security investigations. "
            "Cross-border data transfers require government security assessments."
        ),
        "tags": ["data localization", "MLPS", "real-name registration", "critical infrastructure"],
        "status": "Active",
        "year": 2017,
        "version": "1.0",
        "source_url": "http://www.cac.gov.cn/2016-11/07/c_1119867116.htm"
    },
    {
        "id": "cyb_009",
        "title": "US CISA National Cyber Incident Response Plan",
        "sector": "Cybersecurity",
        "region": "North America",
        "country": "United States",
        "content": (
            "The CISA National Cyber Incident Response Plan establishes a framework for "
            "coordinating the nation's response to significant cybersecurity incidents. "
            "The plan defines roles across federal agencies, state and local governments, "
            "private sector, and international partners during major cyber events. "
            "Four lines of effort cover asset response, threat response, intelligence support, "
            "and affected entity support. "
            "CISA leads coordination for critical infrastructure sectors while the FBI leads "
            "threat response and law enforcement activities. "
            "The plan is activated during cyber incidents with significant national consequences."
        ),
        "tags": ["CISA", "incident response", "federal coordination", "critical infrastructure"],
        "status": "Active",
        "year": 2024,
        "version": "2.0",
        "source_url": "https://www.cisa.gov/national-cyber-incident-response-plan"
    },
    {
        "id": "cyb_010",
        "title": "Germany IT Security Act 2.0",
        "sector": "Cybersecurity",
        "region": "Europe",
        "country": "Germany",
        "content": (
            "Germany's IT Security Act 2.0 significantly strengthens cybersecurity obligations "
            "for critical infrastructure operators and expands the authority of BSI, "
            "Germany's federal information security office. "
            "BSI gains powers to actively monitor the internet for cybersecurity threats "
            "and can order removal of malicious systems. "
            "Critical infrastructure operators must deploy attack detection systems and "
            "report security incidents within 24 hours. "
            "Consumer product manufacturers selling in Germany must publish IT security "
            "information including update timelines. "
            "Operators of public telecommunications networks face mandatory security assessments "
            "for critical components."
        ),
        "tags": ["BSI", "attack detection", "critical infrastructure", "consumer products"],
        "status": "Active",
        "year": 2021,
        "version": "2.0",
        "source_url": "https://www.bsi.bund.de/EN/Topics/KRITIS/IT-SiG_2_0/it-sig-2-0_node.html"
    },

    # ─────────────────────────────────────────
    # SECTOR 3: DATA PRIVACY (10 policies)
    # ─────────────────────────────────────────
    {
        "id": "prv_001",
        "title": "GDPR — General Data Protection Regulation",
        "sector": "Data Privacy",
        "region": "Europe",
        "country": "European Union",
        "content": (
            "The European Union General Data Protection Regulation is the world's most "
            "comprehensive data protection law, applying to all organizations processing "
            "personal data of EU residents regardless of where the organization is located. "
            "Individuals have rights including access, rectification, erasure, portability, "
            "and objection to automated decision-making. "
            "Organizations must appoint Data Protection Officers for large-scale processing "
            "and conduct Data Protection Impact Assessments for high-risk activities. "
            "Personal data breaches must be reported to supervisory authorities within 72 hours. "
            "Maximum fines reach 20 million euros or 4 percent of global annual turnover."
        ),
        "tags": ["GDPR", "data rights", "DPO", "DPIA", "breach notification"],
        "status": "Active",
        "year": 2018,
        "version": "3.0",
        "source_url": "https://gdpr.eu/"
    },
    {
        "id": "prv_002",
        "title": "India DPDP Act — Digital Personal Data Protection",
        "sector": "Data Privacy",
        "region": "Asia",
        "country": "India",
        "content": (
            "India's Digital Personal Data Protection Act 2023 establishes the first "
            "comprehensive federal data protection law for India. "
            "Data fiduciaries must process personal data only for lawful purposes with "
            "consent or for legitimate use cases specified in the act. "
            "Data principals have rights to access information, correct inaccurate data, "
            "and erase personal data. "
            "The Data Protection Board of India adjudicates complaints and can impose "
            "penalties up to 250 crore rupees for breaches. "
            "Significant data fiduciaries processing large volumes of sensitive data face "
            "additional obligations including data localization requirements."
        ),
        "tags": ["DPDP", "Data Protection Board", "consent", "data principals", "India"],
        "status": "Active",
        "year": 2023,
        "version": "1.0",
        "source_url": "https://www.meity.gov.in/writereaddata/files/Digital%20Personal%20Data%20Protection%20Act%202023.pdf"
    },
    {
        "id": "prv_003",
        "title": "CCPA — California Consumer Privacy Act",
        "sector": "Data Privacy",
        "region": "North America",
        "country": "United States",
        "content": (
            "California's Consumer Privacy Act grants California residents extensive rights "
            "over their personal information collected by businesses. "
            "Consumers have rights to know what personal data is collected, delete personal "
            "data, opt out of sale of personal data, and non-discrimination for exercising rights. "
            "The California Privacy Rights Act 2020 expanded CCPA by adding rights to correct "
            "inaccurate data and limit use of sensitive personal information. "
            "The California Privacy Protection Agency enforces the law with fines up to 7500 "
            "dollars per intentional violation. "
            "Businesses must respond to consumer requests within 45 days."
        ),
        "tags": ["CCPA", "CPRA", "consumer rights", "opt-out", "California"],
        "status": "Active",
        "year": 2020,
        "version": "2.0",
        "source_url": "https://oag.ca.gov/privacy/ccpa"
    },
    {
        "id": "prv_004",
        "title": "Brazil LGPD — Lei Geral de Proteção de Dados",
        "sector": "Data Privacy",
        "region": "South America",
        "country": "Brazil",
        "content": (
            "Brazil's General Data Protection Law modeled on GDPR regulates the processing "
            "of personal data of individuals located in Brazil regardless of where the "
            "processing occurs. "
            "Ten legal bases permit data processing including consent, legitimate interest, "
            "legal obligation, and public policy. "
            "Data subjects have rights to access, correction, anonymization, portability, "
            "and deletion of their data. "
            "The National Data Protection Authority enforces the law and can impose fines "
            "up to 2 percent of a company's revenue in Brazil capped at 50 million reais "
            "per violation. "
            "Sensitive data including health, biometric, and political data requires explicit consent."
        ),
        "tags": ["LGPD", "ANPD", "consent", "sensitive data", "Brazil"],
        "status": "Active",
        "year": 2020,
        "version": "2.0",
        "source_url": "https://www.gov.br/cidadania/pt-br/acesso-a-informacao/lgpd"
    },
    {
        "id": "prv_005",
        "title": "China PIPL — Personal Information Protection Law",
        "sector": "Data Privacy",
        "region": "Asia",
        "country": "China",
        "content": (
            "China's Personal Information Protection Law is the country's first comprehensive "
            "federal personal data protection law with extraterritorial application to overseas "
            "entities processing data of individuals in China. "
            "Processing requires one of seven legal bases with consent as the primary basis. "
            "Separate consent is required for sensitive personal information including biometrics, "
            "medical records, financial accounts, and precise location. "
            "Critical information infrastructure operators and processors above government "
            "thresholds must store personal information within China. "
            "Cross-border transfers require security assessments, standard contracts, or "
            "certification by designated institutions."
        ),
        "tags": ["PIPL", "data localization", "sensitive data", "cross-border transfer", "China"],
        "status": "Active",
        "year": 2021,
        "version": "1.0",
        "source_url": "https://www.cac.gov.cn/2021-08/20/c_1631049984897667.htm"
    },
    {
        "id": "prv_006",
        "title": "Singapore PDPA — Personal Data Protection Act",
        "sector": "Data Privacy",
        "region": "Asia",
        "country": "Singapore",
        "content": (
            "Singapore's Personal Data Protection Act governs the collection, use, disclosure, "
            "and care of personal data by private organizations in Singapore. "
            "Organizations must obtain consent before collecting personal data and use it "
            "only for the purposes notified to individuals. "
            "The 2020 amendments introduced mandatory data breach notification within three days, "
            "increased financial penalties up to 1 million Singapore dollars, and introduced "
            "criminal liability for egregious mishandling of data. "
            "The PDPC can require organizations to implement remedial measures and publicly "
            "disclose breaches affecting large numbers of individuals."
        ),
        "tags": ["PDPA", "PDPC", "consent", "breach notification", "Singapore"],
        "status": "Active",
        "year": 2021,
        "version": "3.0",
        "source_url": "https://www.pdpc.gov.sg/Overview-of-PDPA/The-Legislation/Personal-Data-Protection-Act"
    },
    {
        "id": "prv_007",
        "title": "Canada PIPEDA — Personal Information Protection Act",
        "sector": "Data Privacy",
        "region": "North America",
        "country": "Canada",
        "content": (
            "Canada's Personal Information Protection and Electronic Documents Act governs "
            "how private sector organizations collect, use, and disclose personal information "
            "in commercial activities across Canada. "
            "Organizations must identify the purpose of data collection, obtain meaningful "
            "consent, and limit collection to what is necessary. "
            "The Privacy Commissioner investigates complaints and can make recommendations "
            "but lacks direct order-making powers. "
            "Mandatory breach reporting to the Privacy Commissioner applies when breaches "
            "pose a real risk of significant harm. "
            "Bill C-27 proposing a new Consumer Privacy Protection Act to replace PIPEDA "
            "was introduced in 2022 and is under parliamentary review."
        ),
        "tags": ["PIPEDA", "Privacy Commissioner", "consent", "breach reporting", "Canada"],
        "status": "Active",
        "year": 2019,
        "version": "2.0",
        "source_url": "https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/"
    },
    {
        "id": "prv_008",
        "title": "Japan APPI — Act on Protection of Personal Information",
        "sector": "Data Privacy",
        "region": "Asia",
        "country": "Japan",
        "content": (
            "Japan's Act on Protection of Personal Information is the primary data protection "
            "law covering all businesses that handle personal information in Japan. "
            "The Personal Information Protection Commission enforces the law and received "
            "expanded powers in the 2022 amendment. "
            "Businesses must notify data subjects and the PPC within 30 days of a data breach "
            "affecting 1000 or more individuals. "
            "Pseudonymously processed information can be used freely within organizations "
            "while anonymously processed information can be shared externally. "
            "Cross-border transfers require either government whitelisting of the destination "
            "country or individual consent from data subjects."
        ),
        "tags": ["APPI", "PPC", "breach notification", "pseudonymous data", "Japan"],
        "status": "Active",
        "year": 2022,
        "version": "3.0",
        "source_url": "https://www.ppc.go.jp/en/legal/policy/houdou/"
    },
    {
        "id": "prv_009",
        "title": "Australia Privacy Act Reform — Privacy Rights",
        "sector": "Data Privacy",
        "region": "Oceania",
        "country": "Australia",
        "content": (
            "Australia's Privacy Act Review Report 2022 proposes significant reforms to "
            "modernize the Privacy Act 1988 to align with global standards. "
            "Key proposals include a statutory tort for serious invasions of privacy, "
            "a direct right of action for individuals, and expanded definition of personal "
            "information to include technical data. "
            "The Australian Privacy Principles apply to government agencies and organizations "
            "with turnover above 3 million Australian dollars. "
            "The proposed reforms would require privacy impact assessments for high-risk "
            "activities and introduce a children's data protection code. "
            "The Office of the Australian Information Commissioner enforces current obligations."
        ),
        "tags": ["Privacy Act", "OAIC", "privacy tort", "reform", "children's data"],
        "status": "Under Review",
        "year": 2022,
        "version": "Reform 2022",
        "source_url": "https://www.ag.gov.au/rights-and-protections/privacy/privacy-act-review"
    },
    {
        "id": "prv_010",
        "title": "South Africa POPIA — Protection of Personal Information Act",
        "sector": "Data Privacy",
        "region": "Africa",
        "country": "South Africa",
        "content": (
            "South Africa's Protection of Personal Information Act governs the processing "
            "of personal information by public and private bodies in South Africa. "
            "POPIA establishes eight conditions for lawful processing including accountability, "
            "processing limitation, purpose specification, further processing limitation, "
            "information quality, openness, security safeguards, and data subject participation. "
            "The Information Regulator of South Africa investigates complaints and can impose "
            "fines up to 10 million South African rand or imprisonment up to 10 years. "
            "Cross-border transfer of personal information is prohibited unless the destination "
            "country has adequate protection or the data subject consents."
        ),
        "tags": ["POPIA", "Information Regulator", "eight conditions", "cross-border", "Africa"],
        "status": "Active",
        "year": 2021,
        "version": "1.0",
        "source_url": "https://www.justice.gov.za/inforeg/docs/InfoRegSA-POPIA-act2013-004.pdf"
    },
]