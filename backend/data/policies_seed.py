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
    {
        "id": "aig_011",
        "title": "Japan AI Strategy 2022 — Society 5.0 Integration",
        "sector": "AI Governance",
        "region": "Asia",
        "country": "Japan",
        "content": (
            "Japan's AI Strategy 2022 advances the Society 5.0 vision by integrating "
            "artificial intelligence across healthcare, mobility, infrastructure, and "
            "financial services. The Ministry of Economy Trade and Industry oversees "
            "AI deployment guidelines emphasizing human-centered values. Japan maintains "
            "a voluntary governance approach with industry self-regulation while investing "
            "heavily in AI research infrastructure. The strategy mandates AI literacy "
            "programs in education and promotes international AI governance cooperation "
            "through G7 and OECD frameworks. Japanese regulators focus on trustworthy AI "
            "with particular emphasis on elderly care robotics and autonomous vehicles."
        ),
        "tags": ["Society 5.0", "voluntary", "human-centered", "international cooperation"],
        "status": "Active",
        "year": 2022,
        "version": "2.0",
        "source_url": "https://www.cas.go.jp/jp/seisaku/jinkou_chinou/index.html"
    },
    {
        "id": "aig_012",
        "title": "South Korea National AI Ethics Standards",
        "sector": "AI Governance",
        "region": "Asia",
        "country": "South Korea",
        "content": (
            "South Korea's National AI Ethics Standards establish three core values: "
            "human dignity, social benefits, and technological adaptability. "
            "The Ministry of Science and ICT enforces these standards across public "
            "and private AI systems. Korea mandates algorithmic impact assessments "
            "for government AI procurement decisions affecting citizens. "
            "The framework addresses AI bias in hiring, credit scoring, and criminal "
            "justice applications. South Korea invests significantly in AI semiconductor "
            "research and requires domestic AI systems to undergo ethics certification "
            "before government deployment. International AI governance alignment with "
            "EU and US frameworks is prioritized."
        ),
        "tags": ["ethics", "human dignity", "impact assessment", "algorithmic bias"],
        "status": "Active",
        "year": 2022,
        "version": "1.0",
        "source_url": "https://www.msit.go.kr/eng/bbs/view.do?sCode=eng&mId=4&mPid=2&pageIndex=&bbsSeqNo=42&nttSeqNo=2"
    },
    {
        "id": "aig_013",
        "title": "UAE National AI Strategy 2031",
        "sector": "AI Governance",
        "region": "Middle East",
        "country": "United Arab Emirates",
        "content": (
            "The United Arab Emirates National AI Strategy 2031 aims to position UAE "
            "as a global AI hub and add 96 billion dollars to the economy by 2031. "
            "The strategy focuses on government service automation, healthcare diagnostics, "
            "smart city infrastructure, and renewable energy optimization. "
            "UAE established the world's first Ministry of Artificial Intelligence "
            "and mandates AI adoption across all federal entities. "
            "The framework includes AI ethics guidelines, data governance standards, "
            "and talent development programs. UAE's AI regulatory sandbox allows "
            "companies to test AI solutions under regulatory supervision before "
            "full market deployment."
        ),
        "tags": ["national strategy", "smart city", "government automation", "sandbox"],
        "status": "Active",
        "year": 2022,
        "version": "2.0",
        "source_url": "https://ai.gov.ae/wp-content/uploads/2021/07/UAE-National-Strategy-for-Artificial-Intelligence-2031.pdf"
    },
    {
        "id": "aig_014",
        "title": "Germany AI Strategy — Künstliche Intelligenz Made in Germany",
        "sector": "AI Governance",
        "region": "Europe",
        "country": "Germany",
        "content": (
            "Germany's AI Strategy emphasizes trustworthy AI development with strong "
            "focus on industrial applications and Mittelstand SME adoption. "
            "The Federal Government invests 5 billion euros in AI research centers "
            "and international AI partnerships. German AI governance prioritizes "
            "explainability and auditability of AI systems in manufacturing, "
            "healthcare, and mobility sectors. The strategy mandates human oversight "
            "for high-stakes AI decisions and requires documentation of AI system "
            "limitations. Germany leads European AI standardization through DIN "
            "standards bodies and actively shapes EU AI Act implementation guidelines "
            "for industrial AI applications."
        ),
        "tags": ["industrial AI", "explainability", "SME", "standardization"],
        "status": "Active",
        "year": 2023,
        "version": "2.0",
        "source_url": "https://www.bmwk.de/Redaktion/EN/Publikationen/Technologie/ki-strategie-der-bundesregierung.html"
    },
    {
        "id": "aig_015",
        "title": "France National AI Strategy — AI for Humanity",
        "sector": "AI Governance",
        "region": "Europe",
        "country": "France",
        "content": (
            "France's AI for Humanity strategy positions France as Europe's leading "
            "AI nation through massive investment in research, talent, and infrastructure. "
            "The strategy emphasizes open and trustworthy AI with particular focus on "
            "healthcare, defense, environment, and mobility sectors. "
            "French regulators at CNIL enforce algorithmic accountability for public "
            "services and ban discriminatory AI in hiring and credit decisions. "
            "France promotes European AI sovereignty through strategic autonomy "
            "frameworks and supports development of European alternatives to US and "
            "Chinese AI platforms. AI ethics education is mandatory in French universities "
            "under the national digital strategy."
        ),
        "tags": ["AI sovereignty", "trustworthy AI", "anti-discrimination", "research"],
        "status": "Active",
        "year": 2021,
        "version": "1.5",
        "source_url": "https://www.economie.gouv.fr/files/files/PDF/2021/Strategie-Nationale-Intelligence-Artificielle.pdf"
    },
    {
        "id": "aig_016",
        "title": "China National AI Standardization Roadmap",
        "sector": "AI Governance",
        "region": "Asia",
        "country": "China",
        "content": (
            "China's National AI Standardization Roadmap establishes comprehensive "
            "technical standards for AI systems across safety, ethics, and performance "
            "dimensions. The Standardization Administration of China coordinates "
            "with international bodies including ISO and IEEE to align Chinese AI "
            "standards with global frameworks while maintaining regulatory sovereignty. "
            "The roadmap covers AI terminology, data quality, algorithmic bias testing, "
            "and AI product certification requirements. Chinese AI systems must undergo "
            "government security assessments before deployment in critical sectors. "
            "The framework mandates AI traceability and audit trail requirements for "
            "government AI procurement decisions."
        ),
        "tags": ["standardization", "security assessment", "traceability", "certification"],
        "status": "Active",
        "year": 2021,
        "version": "1.0",
        "source_url": "https://www.sac.gov.cn/sac/xw/xwzx/202108/t20210801_350473.htm"
    },
    {
        "id": "aig_017",
        "title": "Brazil AI Strategy — Brazilian Artificial Intelligence Plan",
        "sector": "AI Governance",
        "region": "South America",
        "country": "Brazil",
        "content": (
            "Brazil's Artificial Intelligence Plan EBIA establishes national priorities "
            "for AI development emphasizing social inclusion and digital transformation. "
            "The Ministry of Science Technology and Innovation coordinates AI governance "
            "across federal agencies with focus on agriculture, health, public security, "
            "and smart cities. Brazil's AI ethics principles require transparency, "
            "non-discrimination, privacy protection, and human oversight for automated "
            "government decisions. The plan invests in AI education and digital skills "
            "development for underserved communities. Brazilian AI regulation builds on "
            "LGPD data protection foundations with specific provisions for automated "
            "decision-making affecting citizen rights."
        ),
        "tags": ["social inclusion", "digital transformation", "ethics", "automated decisions"],
        "status": "Active",
        "year": 2021,
        "version": "1.0",
        "source_url": "https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/transformacaodigital/arquivosdigital/ebia.pdf"
    },
    {
        "id": "aig_018",
        "title": "India NITI Aayog Responsible AI Framework",
        "sector": "AI Governance",
        "region": "Asia",
        "country": "India",
        "content": (
            "India's NITI Aayog Responsible AI for All framework establishes principles "
            "and practical guidelines for AI governance across government and private "
            "sectors. The framework addresses AI safety, equality, inclusivity, "
            "non-discrimination, privacy, transparency, and accountability. "
            "Special provisions cover AI deployment in high-stakes domains including "
            "healthcare, agriculture, education, and financial services serving rural "
            "and underserved populations. The framework mandates algorithmic audits "
            "for government AI systems and requires explainable AI for citizen-facing "
            "applications. India positions responsible AI as central to achieving "
            "Sustainable Development Goals and digital public infrastructure goals."
        ),
        "tags": ["responsible AI", "inclusivity", "algorithmic audit", "SDGs"],
        "status": "Active",
        "year": 2021,
        "version": "2.0",
        "source_url": "https://www.niti.gov.in/sites/default/files/2021-02/Responsible-AI-22022021.pdf"
    },
    {
        "id": "aig_019",
        "title": "Council of Europe AI Convention — Framework Convention",
        "sector": "AI Governance",
        "region": "Europe",
        "country": "International",
        "content": (
            "The Council of Europe Framework Convention on Artificial Intelligence "
            "is the first binding international treaty on AI governance signed by "
            "European states and non-European observers including the United States "
            "and United Kingdom. The convention establishes legally binding obligations "
            "for protecting human rights, democracy, and rule of law in AI development "
            "and deployment. Signatories must implement measures ensuring AI systems "
            "respect fundamental rights and provide effective remedies for violations. "
            "The convention covers public sector AI use and extends to private sector "
            "activities affecting public interests. National supervisory bodies must "
            "be established to monitor compliance and handle complaints."
        ),
        "tags": ["binding treaty", "human rights", "democracy", "international law"],
        "status": "Active",
        "year": 2024,
        "version": "1.0",
        "source_url": "https://www.coe.int/en/web/artificial-intelligence/the-framework-convention-on-artificial-intelligence"
    },
    {
        "id": "aig_020",
        "title": "G7 Hiroshima AI Process — International Guiding Principles",
        "sector": "AI Governance",
        "region": "Global",
        "country": "International",
        "content": (
            "The G7 Hiroshima AI Process establishes international guiding principles "
            "and a code of conduct for advanced AI systems including foundation models "
            "and generative AI. The eleven principles cover transparency, safety testing, "
            "cybersecurity, intellectual property, privacy protection, and responsible "
            "disclosure of AI capabilities and limitations. G7 members commit to "
            "implementing these principles domestically and promoting them globally "
            "through international forums. The process establishes voluntary commitments "
            "for AI developers while work continues on binding international frameworks. "
            "Interoperability between different national AI governance frameworks is "
            "a central objective of the Hiroshima process."
        ),
        "tags": ["G7", "foundation models", "generative AI", "international principles"],
        "status": "Active",
        "year": 2023,
        "version": "1.0",
        "source_url": "https://www.meti.go.jp/press/2023/10/20231030002/20231030002-1.pdf"
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
 {
        "id": "cyb_011",
        "title": "EU Cyber Resilience Act — Product Security Requirements",
        "sector": "Cybersecurity",
        "region": "Europe",
        "country": "European Union",
        "content": (
            "The European Union Cyber Resilience Act establishes mandatory cybersecurity "
            "requirements for all digital products sold in the EU market. "
            "Manufacturers must ensure products with digital elements are designed "
            "with security by default and by design principles. "
            "Products must receive security updates throughout their support lifecycle "
            "and manufacturers must report actively exploited vulnerabilities within "
            "24 hours to ENISA. "
            "The regulation covers IoT devices, software, operating systems, and "
            "connected hardware with fines up to 15 million euros or 2.5 percent "
            "of global turnover for non-compliance. CE marking will require "
            "cybersecurity conformity assessment for high-risk product categories."
        ),
        "tags": ["product security", "IoT", "security by design", "CE marking"],
        "status": "Active",
        "year": 2024,
        "version": "1.0",
        "source_url": "https://www.enisa.europa.eu/topics/cybersecurity-policy/cyber-resilience-act"
    },
    {
        "id": "cyb_012",
        "title": "Japan Cybersecurity Strategy 2022",
        "sector": "Cybersecurity",
        "region": "Asia",
        "country": "Japan",
        "content": (
            "Japan's Cybersecurity Strategy 2022 establishes a free open and secure "
            "cyberspace vision with emphasis on protecting critical infrastructure "
            "and supply chain security. The National center of Incident readiness "
            "and Strategy for Cybersecurity coordinates national cyber defense. "
            "Japanese organizations in 14 critical infrastructure sectors must "
            "implement baseline cybersecurity measures and participate in government "
            "information sharing programs. The strategy prioritizes semiconductor "
            "supply chain security and protection of sensitive technology from "
            "foreign adversaries. Japan strengthens cybersecurity cooperation with "
            "the United States, Australia, UK, and NATO allies through bilateral "
            "and multilateral agreements."
        ),
        "tags": ["critical infrastructure", "supply chain", "information sharing", "alliances"],
        "status": "Active",
        "year": 2022,
        "version": "1.0",
        "source_url": "https://www.nisc.go.jp/eng/pdf/cs-strategy202209_en.pdf"
    },
    {
        "id": "cyb_013",
        "title": "India Information Technology Amendment Rules — Cybersecurity",
        "sector": "Cybersecurity",
        "region": "Asia",
        "country": "India",
        "content": (
            "India's Information Technology Amendment Rules strengthen cybersecurity "
            "obligations for intermediaries and digital platforms operating in India. "
            "Significant social media intermediaries must appoint resident grievance "
            "officers and chief compliance officers accountable to Indian authorities. "
            "Platforms must enable traceability of message origins for law enforcement "
            "purposes while maintaining end-to-end encryption where technically feasible. "
            "Government cybersecurity directions require organizations to maintain "
            "synchronized clocks, preserve logs, and report incidents within defined "
            "timelines. The rules create a three-tier grievance redressal mechanism "
            "for cybersecurity and content-related complaints."
        ),
        "tags": ["intermediary liability", "traceability", "grievance redressal", "compliance"],
        "status": "Active",
        "year": 2023,
        "version": "2.0",
        "source_url": "https://www.meity.gov.in/content/information-technology-intermediary-guidelines-and-digital-media-ethics-code-rules-2021"
    },
    {
        "id": "cyb_014",
        "title": "Canada Cyber Security Strategy",
        "sector": "Cybersecurity",
        "region": "North America",
        "country": "Canada",
        "content": (
            "Canada's National Cyber Security Strategy establishes a resilient and "
            "secure Canadian cyberspace through three strategic goals: security and "
            "resilience, cyber innovation, and leadership and collaboration. "
            "The Canadian Centre for Cyber Security provides authoritative advice "
            "and guidance to government and critical infrastructure operators. "
            "Critical infrastructure owners in ten designated sectors receive "
            "government threat intelligence and must implement minimum cybersecurity "
            "standards. Canada's cybersecurity legislation enables information sharing "
            "between private sector and government without liability concerns. "
            "International cybersecurity cooperation with Five Eyes partners and NATO "
            "allies forms a cornerstone of the Canadian cyber strategy."
        ),
        "tags": ["national strategy", "critical infrastructure", "Five Eyes", "information sharing"],
        "status": "Active",
        "year": 2022,
        "version": "2.0",
        "source_url": "https://www.cyber.gc.ca/en/guidance/national-cyber-security-strategy-canadas-vision-security-and-prosperity-digital-age"
    },
    {
        "id": "cyb_015",
        "title": "South Africa Cybersecurity Policy Framework",
        "sector": "Cybersecurity",
        "region": "Africa",
        "country": "South Africa",
        "content": (
            "South Africa's Cybersecurity Policy Framework establishes a comprehensive "
            "approach to securing cyberspace and protecting critical information "
            "infrastructure. The Department of Justice and Constitutional Development "
            "coordinates cybersecurity across government while the Cybersecurity Hub "
            "serves as national coordination point for incident response. "
            "The Cybercrimes Act criminalizes unauthorized access, data interception, "
            "and cyberterrorism with significant penalties. "
            "Critical information infrastructure operators must implement prescribed "
            "minimum security measures and report significant incidents to authorities. "
            "South Africa participates in African Union cybersecurity cooperation "
            "frameworks and bilateral agreements with major partners."
        ),
        "tags": ["critical infrastructure", "Cybercrimes Act", "incident response", "African Union"],
        "status": "Active",
        "year": 2022,
        "version": "1.0",
        "source_url": "https://www.justice.gov.za/cybersecurity/docs/2021-CybersecurityPolicyFramework.pdf"
    },
    {
        "id": "cyb_016",
        "title": "Brazil Cybersecurity Strategy — ENCD",
        "sector": "Cybersecurity",
        "region": "South America",
        "country": "Brazil",
        "content": (
            "Brazil's National Cybersecurity Strategy ENCD establishes objectives and "
            "actions to strengthen the protection of Brazilian cyberspace and digital "
            "infrastructure. The Institutional Security Office coordinates national "
            "cybersecurity governance across military and civilian agencies. "
            "The strategy emphasizes development of domestic cybersecurity capabilities "
            "and reduction of dependency on foreign technology. "
            "Critical infrastructure sectors including energy, finance, telecommunications, "
            "and transportation must implement sector-specific security requirements. "
            "Brazil's Computer Emergency Response Team CERT.br coordinates incident "
            "response and maintains national vulnerability databases. "
            "International cybersecurity cooperation with South American neighbors "
            "and major bilateral partners is prioritized."
        ),
        "tags": ["national strategy", "CERT.br", "critical infrastructure", "digital sovereignty"],
        "status": "Active",
        "year": 2020,
        "version": "1.0",
        "source_url": "https://www.gov.br/gsi/pt-br/assuntos/dsi/estrategia-nacional-de-seguranca-cibernetica"
    },
    {
        "id": "cyb_017",
        "title": "France Cyber Strategy — ANSSI Framework",
        "sector": "Cybersecurity",
        "region": "Europe",
        "country": "France",
        "content": (
            "France's cybersecurity strategy led by ANSSI the National Agency for "
            "Information Systems Security establishes comprehensive protection for "
            "French critical infrastructure and government systems. "
            "ANSSI certifies cybersecurity products and services for government use "
            "and operates the national CERT for government entities. "
            "French operators of vital importance in twelve critical sectors must "
            "comply with mandatory security rules and report incidents within 24 hours. "
            "The strategy promotes development of French and European cybersecurity "
            "industry as part of digital sovereignty agenda. "
            "ANSSI provides free cybersecurity diagnostic services to local governments "
            "and healthcare institutions to strengthen resilience across all sectors."
        ),
        "tags": ["ANSSI", "digital sovereignty", "certification", "vital operators"],
        "status": "Active",
        "year": 2021,
        "version": "1.0",
        "source_url": "https://www.ssi.gouv.fr/en/cybersecurity-in-france/cybersecurity-strategy/"
    },
    {
        "id": "cyb_018",
        "title": "New Zealand Cyber Security Strategy 2019",
        "sector": "Cybersecurity",
        "region": "Oceania",
        "country": "New Zealand",
        "content": (
            "New Zealand's Cyber Security Strategy establishes a secure resilient "
            "and prosperous online New Zealand through four goals: cyber resilience, "
            "cyber capability, addressing cybercrime, and international engagement. "
            "The National Cyber Security Centre within the Government Communications "
            "Security Bureau protects nationally significant organizations including "
            "critical infrastructure and key government agencies. "
            "New Zealand's Computer Emergency Response Team CERT NZ provides free "
            "cybersecurity advice and incident response support to businesses and "
            "individuals. The strategy emphasizes Five Eyes intelligence sharing "
            "and active participation in international cybersecurity norm development "
            "through the United Nations."
        ),
        "tags": ["Five Eyes", "CERT NZ", "resilience", "international norms"],
        "status": "Active",
        "year": 2019,
        "version": "1.0",
        "source_url": "https://www.dpmc.govt.nz/our-programmes/cyber-security/new-zealands-cyber-security-strategy"
    },
    {
        "id": "cyb_019",
        "title": "Israel National Cyber Directorate — Cyber Defense Doctrine",
        "sector": "Cybersecurity",
        "region": "Middle East",
        "country": "Israel",
        "content": (
            "Israel's National Cyber Directorate establishes a comprehensive cyber "
            "defense doctrine protecting national infrastructure and positioning Israel "
            "as a global cybersecurity leader. The directorate coordinates cyber defense "
            "across government civilian infrastructure while military cyber operations "
            "remain under IDF authority. Israeli critical infrastructure operators "
            "must implement directorate-approved security frameworks and participate "
            "in regular cyber exercises. Israel's cybersecurity ecosystem produces "
            "significant private sector innovation with mandatory technology transfer "
            "arrangements for government-funded research. "
            "The doctrine emphasizes offensive cyber capabilities as deterrence while "
            "maintaining robust defensive posture for critical national infrastructure."
        ),
        "tags": ["cyber defense", "critical infrastructure", "deterrence", "innovation ecosystem"],
        "status": "Active",
        "year": 2021,
        "version": "2.0",
        "source_url": "https://www.gov.il/en/departments/israel_national_cyber_directorate"
    },
    {
        "id": "cyb_020",
        "title": "ASEAN Cybersecurity Cooperation Strategy",
        "sector": "Cybersecurity",
        "region": "Asia",
        "country": "International",
        "content": (
            "The ASEAN Cybersecurity Cooperation Strategy establishes a framework "
            "for collective cybersecurity resilience across the ten ASEAN member states. "
            "The strategy focuses on capacity building, information sharing, CERT "
            "cooperation, and harmonization of cybersecurity policies across the region. "
            "ASEAN members commit to developing national cybersecurity frameworks "
            "aligned with international standards and sharing threat intelligence "
            "through established channels. "
            "The strategy establishes the ASEAN Network Security Action Council "
            "to coordinate regional cyber incident response. "
            "Particular focus is placed on protecting ASEAN digital economic "
            "infrastructure and cross-border data flows supporting regional integration."
        ),
        "tags": ["ASEAN", "regional cooperation", "capacity building", "information sharing"],
        "status": "Active",
        "year": 2021,
        "version": "2.0",
        "source_url": "https://asean.org/asean-cybersecurity-cooperation-strategy-2021-2025/"
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
      {
        "id": "prv_011",
        "title": "Thailand Personal Data Protection Act — PDPA",
        "sector": "Data Privacy",
        "region": "Asia",
        "country": "Thailand",
        "content": (
            "Thailand's Personal Data Protection Act establishes comprehensive data "
            "protection rights for Thai citizens modeled on GDPR principles. "
            "Data controllers must obtain explicit consent before collecting personal "
            "data and limit processing to specified purposes. "
            "Data subjects have rights to access, correct, delete, and port their "
            "personal data and can object to automated decision-making. "
            "The Personal Data Protection Committee oversees enforcement and can "
            "impose administrative fines up to 5 million baht per violation. "
            "Cross-border data transfers require destination country adequacy assessment "
            "or appropriate safeguards. Healthcare and financial sector data receive "
            "enhanced protection as sensitive personal information categories."
        ),
        "tags": ["PDPA", "consent", "data rights", "sensitive data", "Thailand"],
        "status": "Active",
        "year": 2022,
        "version": "1.0",
        "source_url": "https://www.pdpc.or.th/en/home"
    },
    {
        "id": "prv_012",
        "title": "Indonesia Personal Data Protection Law",
        "sector": "Data Privacy",
        "region": "Asia",
        "country": "Indonesia",
        "content": (
            "Indonesia's Personal Data Protection Law establishes the first comprehensive "
            "federal data protection framework for the world's fourth most populous nation. "
            "The law applies to all personal data processing of Indonesian citizens "
            "regardless of where processing occurs. Data subjects have rights to "
            "access, correction, deletion, withdrawal of consent, and objection to "
            "automated profiling decisions. "
            "Data controllers must implement technical and organizational security "
            "measures and notify authorities of breaches within 14 days. "
            "The supervisory authority can impose fines up to 2 percent of annual "
            "revenue and criminal penalties for intentional violations. "
            "Government data processing faces additional restrictions and oversight requirements."
        ),
        "tags": ["Indonesia", "data rights", "breach notification", "government data"],
        "status": "Active",
        "year": 2022,
        "version": "1.0",
        "source_url": "https://www.dpr.go.id/doksetjen/dokumen/uu-pdp-2022"
    },
    {
        "id": "prv_013",
        "title": "Kenya Data Protection Act",
        "sector": "Data Privacy",
        "region": "Africa",
        "country": "Kenya",
        "content": (
            "Kenya's Data Protection Act establishes rights and obligations for "
            "personal data processing in Kenya and creates the Office of the Data "
            "Protection Commissioner as independent supervisory authority. "
            "Data processors must register with the Commissioner and implement "
            "data protection by design and default principles. "
            "Sensitive personal data including health, biometric, and financial "
            "information requires explicit consent and enhanced security measures. "
            "The act addresses unique African context including mobile money data, "
            "digital identity systems, and cross-border data flows within Africa. "
            "Kenya's data protection framework aligns with the African Union Convention "
            "on Cyber Security and Personal Data Protection building regional coherence."
        ),
        "tags": ["Kenya", "Commissioner", "mobile money", "African Union", "biometric"],
        "status": "Active",
        "year": 2019,
        "version": "1.0",
        "source_url": "https://www.odpc.go.ke/dpa-act/"
    },
    {
        "id": "prv_014",
        "title": "Nigeria Data Protection Regulation — NDPR",
        "sector": "Data Privacy",
        "region": "Africa",
        "country": "Nigeria",
        "content": (
            "Nigeria's Data Protection Regulation established by the National Information "
            "Technology Development Agency creates obligations for organizations "
            "processing personal data of Nigerian citizens. "
            "Data controllers must conduct Data Protection Impact Assessments for "
            "high-risk processing activities and audit data processing annually. "
            "Organizations processing data of over 1000 data subjects must file "
            "annual data protection audits with the supervisory authority. "
            "The regulation addresses fintech data processing requirements specific "
            "to Nigeria's large mobile banking sector. "
            "The Nigeria Data Protection Bureau was established in 2022 to strengthen "
            "enforcement capacity and develop comprehensive data protection legislation "
            "replacing the existing regulation."
        ),
        "tags": ["NDPR", "fintech", "audit requirement", "Nigeria", "DPIA"],
        "status": "Active",
        "year": 2019,
        "version": "2.0",
        "source_url": "https://ndpb.gov.ng/Files/Nigeria_Data_Protection_Regulation.pdf"
    },
    {
        "id": "prv_015",
        "title": "Saudi Arabia Personal Data Protection Law — PDPL",
        "sector": "Data Privacy",
        "region": "Middle East",
        "country": "Saudi Arabia",
        "content": (
            "Saudi Arabia's Personal Data Protection Law establishes comprehensive "
            "data protection obligations for organizations operating in Saudi Arabia "
            "or processing data of Saudi residents. "
            "The National Data Management Office oversees implementation and enforcement "
            "with authority to impose fines up to 5 million Saudi riyals. "
            "Cross-border data transfers require regulatory approval and destination "
            "country adequacy assessment. "
            "Sensitive personal data categories including health, financial, and "
            "biometric information receive enhanced protection requirements. "
            "The law aligns with Saudi Vision 2030 digital transformation objectives "
            "and international data protection standards enabling cross-border "
            "digital commerce with major trading partners."
        ),
        "tags": ["PDPL", "Vision 2030", "cross-border transfer", "Saudi Arabia"],
        "status": "Active",
        "year": 2021,
        "version": "1.0",
        "source_url": "https://ndmo.gov.sa/en/rules-and-regulations/rules/55"
    },
    {
        "id": "prv_016",
        "title": "New Zealand Privacy Act 2020",
        "sector": "Data Privacy",
        "region": "Oceania",
        "country": "New Zealand",
        "content": (
            "New Zealand's Privacy Act 2020 modernizes data protection with mandatory "
            "breach notification and strengthened individual rights replacing the "
            "1993 Privacy Act. Organizations must notify the Privacy Commissioner "
            "and affected individuals when a privacy breach causes serious harm. "
            "Thirteen information privacy principles govern data collection, use, "
            "storage, security, and access rights. "
            "The Privacy Commissioner gains expanded investigation powers and ability "
            "to issue compliance notices. "
            "The act strengthens cross-border data transfer protections requiring "
            "recipients to provide comparable privacy protection. "
            "New Zealand maintains adequacy status with the European Union enabling "
            "unrestricted data flows between jurisdictions."
        ),
        "tags": ["breach notification", "adequacy", "information principles", "New Zealand"],
        "status": "Active",
        "year": 2020,
        "version": "1.0",
        "source_url": "https://www.privacy.org.nz/privacy-act-2020/"
    },
    {
        "id": "prv_017",
        "title": "Mexico Federal Law on Protection of Personal Data",
        "sector": "Data Privacy",
        "region": "South America",
        "country": "Mexico",
        "content": (
            "Mexico's Federal Law on Protection of Personal Data Held by Private Parties "
            "establishes data protection obligations for private sector organizations "
            "in Mexico. The National Institute for Transparency Access to Information "
            "and Personal Data Protection enforces the law. "
            "Data subjects have ARCO rights — access, rectification, cancellation, "
            "and opposition — with defined response timelines. "
            "Privacy notices must be provided before data collection and organizations "
            "must implement security measures proportional to data sensitivity. "
            "The law addresses consent requirements for marketing communications "
            "and cross-border data transfer restrictions. "
            "Mexico is working on comprehensive privacy law reform to align with "
            "international standards and USMCA digital trade commitments."
        ),
        "tags": ["ARCO rights", "privacy notice", "INAI", "Mexico", "reform"],
        "status": "Active",
        "year": 2010,
        "version": "2.0",
        "source_url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf"
    },
    {
        "id": "prv_018",
        "title": "Argentina Personal Data Protection Law — LPDP",
        "sector": "Data Privacy",
        "region": "South America",
        "country": "Argentina",
        "content": (
            "Argentina's Personal Data Protection Law establishes rights and protections "
            "for personal data of Argentine citizens processed by public and private "
            "entities. Argentina holds European Union adequacy status making it one "
            "of few non-European countries with unrestricted EU data transfers. "
            "The National Directorate for Personal Data Protection enforces the law "
            "and maintains public register of databases. "
            "Data subjects have habeas data constitutional right to access and correct "
            "their personal information in any database. "
            "Argentina is reforming its data protection law to align with GDPR standards "
            "and maintain EU adequacy status while addressing new technologies including "
            "AI and biometric data processing."
        ),
        "tags": ["adequacy", "habeas data", "reform", "Argentina", "EU alignment"],
        "status": "Active",
        "year": 2000,
        "version": "3.0",
        "source_url": "https://www.argentina.gob.ar/aaip/datospersonales/normativa/ley25326"
    },
    {
        "id": "prv_019",
        "title": "UAE Federal Decree Law on Personal Data Protection",
        "sector": "Data Privacy",
        "region": "Middle East",
        "country": "United Arab Emirates",
        "content": (
            "UAE's Federal Decree Law on Personal Data Protection establishes the "
            "first federal data protection framework for the United Arab Emirates. "
            "The UAE Data Office oversees implementation and enforcement across "
            "all emirates with authority to impose fines up to 20 million dirhams. "
            "Data controllers must obtain consent or establish alternative lawful "
            "basis for processing and implement appropriate technical safeguards. "
            "The law covers sensitive personal data categories including health, "
            "biometric, financial, and children's data with enhanced protections. "
            "Cross-border data transfers require approval from the UAE Data Office "
            "or implementation of approved transfer mechanisms. "
            "Free zones including DIFC and ADGM maintain separate data protection "
            "regimes aligned with international standards."
        ),
        "tags": ["UAE Data Office", "free zones", "DIFC", "consent", "sensitive data"],
        "status": "Active",
        "year": 2021,
        "version": "1.0",
        "source_url": "https://uaelegislation.gov.ae/en/legislations/1826"
    },
    {
        "id": "prv_020",
        "title": "Turkey Personal Data Protection Law — KVKK",
        "sector": "Data Privacy",
        "region": "Europe",
        "country": "Turkey",
        "content": (
            "Turkey's Personal Data Protection Law KVKK establishes data protection "
            "obligations modeled on European Union GDPR principles for Turkey's "
            "large digital economy. The Personal Data Protection Authority enforces "
            "the law and maintains register of data controllers. "
            "Data subjects have rights to information, access, correction, deletion, "
            "and objection to automated decisions affecting their rights. "
            "Sensitive personal data including health, biometric, political, and "
            "religious information requires explicit consent and enhanced security. "
            "Cross-border data transfers require either adequacy decision or explicit "
            "consent from data subjects. Turkey seeks EU adequacy status as part "
            "of broader EU accession process aligning domestic law with European standards."
        ),
        "tags": ["KVKK", "Turkey", "EU alignment", "adequacy", "sensitive data"],
        "status": "Active",
        "year": 2016,
        "version": "2.0",
        "source_url": "https://www.kvkk.gov.tr/SharedFolderServer/CMSFiles/aedf06a6-b313-42b5-b4f9-76629cf539e1.pdf"
    },
     # ─────────────────────────────────────────
    # HEALTHCARE AI — NEW SECTOR (hlt_001 to hlt_010)
    # ─────────────────────────────────────────
    {
        "id": "hlt_001",
        "title": "EU Medical Device Regulation — AI in Healthcare",
        "sector": "Healthcare AI",
        "region": "Europe",
        "country": "European Union",
        "content": (
            "The European Union Medical Device Regulation establishes safety and "
            "performance requirements for AI-powered medical devices and software "
            "as medical devices across EU member states. "
            "AI diagnostic tools, clinical decision support systems, and treatment "
            "planning software must undergo conformity assessment based on risk class. "
            "High-risk AI medical devices require Notified Body certification and "
            "post-market surveillance with mandatory incident reporting. "
            "The regulation requires AI medical devices to be transparent about "
            "their training data, limitations, and intended use populations. "
            "Explainability requirements ensure clinicians can understand and "
            "appropriately rely on AI recommendations in patient care decisions."
        ),
        "tags": ["medical devices", "AI diagnostics", "conformity assessment", "explainability"],
        "status": "Active",
        "year": 2021,
        "version": "1.0",
        "source_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32017R0745"
    },
    {
        "id": "hlt_002",
        "title": "US FDA Artificial Intelligence Medical Device Framework",
        "sector": "Healthcare AI",
        "region": "North America",
        "country": "United States",
        "content": (
            "The US Food and Drug Administration framework for AI and machine learning "
            "based software as medical devices establishes a risk-based regulatory "
            "approach for AI healthcare applications. "
            "The predetermined change control plan allows AI systems to learn and "
            "adapt after market authorization within pre-specified boundaries. "
            "FDA requires clinical validation studies demonstrating AI performance "
            "across diverse patient populations including underrepresented groups. "
            "AI medical devices must provide transparency about algorithm training "
            "data and performance metrics to clinicians. "
            "The framework addresses algorithmic bias concerns requiring evaluation "
            "of AI performance across race, gender, and age subgroups."
        ),
        "tags": ["FDA", "medical AI", "algorithmic bias", "clinical validation", "SaMD"],
        "status": "Active",
        "year": 2021,
        "version": "2.0",
        "source_url": "https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-and-machine-learning-aiml-enabled-medical-devices"
    },
    {
        "id": "hlt_003",
        "title": "UK MHRA AI as Medical Device Regulatory Position",
        "sector": "Healthcare AI",
        "region": "Europe",
        "country": "United Kingdom",
        "content": (
            "The UK Medicines and Healthcare products Regulatory Agency establishes "
            "regulatory requirements for AI software functioning as medical devices "
            "in the United Kingdom post-Brexit. "
            "AI medical devices must demonstrate safety and performance through "
            "clinical evidence appropriate to their intended use and risk level. "
            "The MHRA requires AI developers to implement continuous performance "
            "monitoring and post-market surveillance programs. "
            "Real world performance data must be collected and analyzed to detect "
            "model drift and performance degradation over time. "
            "The UK framework adopts a flexible approach allowing AI systems to "
            "evolve while maintaining patient safety through change management protocols."
        ),
        "tags": ["MHRA", "post-market surveillance", "model drift", "UK", "medical AI"],
        "status": "Active",
        "year": 2021,
        "version": "1.0",
        "source_url": "https://www.gov.uk/government/publications/software-and-ai-as-a-medical-device-change-programme"
    },
    {
        "id": "hlt_004",
        "title": "WHO Ethics and Governance of AI for Health",
        "sector": "Healthcare AI",
        "region": "Global",
        "country": "International",
        "content": (
            "The World Health Organization guidance on ethics and governance of "
            "artificial intelligence for health establishes six core principles for "
            "AI deployment in healthcare globally. "
            "Principles cover protecting human autonomy, promoting well-being, "
            "ensuring transparency, fostering accountability, ensuring equity, "
            "and promoting sustainable AI ecosystems. "
            "WHO specifically addresses AI risks in low and middle income countries "
            "including algorithmic bias, data colonialism, and technology dependency. "
            "The guidance calls for health AI systems to be designed with diverse "
            "training datasets representing global populations. "
            "WHO recommends establishing national AI for health governance frameworks "
            "and international cooperation mechanisms for AI safety monitoring."
        ),
        "tags": ["WHO", "global health", "equity", "low-income countries", "ethics"],
        "status": "Active",
        "year": 2021,
        "version": "1.0",
        "source_url": "https://www.who.int/publications/i/item/9789240029200"
    },
    {
        "id": "hlt_005",
        "title": "Singapore AI in Healthcare Framework",
        "sector": "Healthcare AI",
        "region": "Asia",
        "country": "Singapore",
        "content": (
            "Singapore's Ministry of Health establishes a national framework for "
            "responsible AI deployment in healthcare settings. "
            "The framework covers AI-assisted diagnosis, treatment planning, drug "
            "discovery, hospital operations, and patient monitoring applications. "
            "Healthcare AI systems must undergo clinical validation and receive "
            "regulatory approval from the Health Sciences Authority before deployment. "
            "Clinician education requirements ensure healthcare professionals understand "
            "AI capabilities and limitations before relying on AI recommendations. "
            "The framework addresses equity concerns requiring AI systems to perform "
            "consistently across Singapore's diverse multiracial population. "
            "Post-deployment monitoring programs track AI performance and adverse events."
        ),
        "tags": ["healthcare AI", "clinical validation", "HSA", "equity", "monitoring"],
        "status": "Active",
        "year": 2022,
        "version": "1.0",
        "source_url": "https://www.moh.gov.sg/policies-and-licensing/licensing-and-regulation/regulatory-regime-for-software-medical-devices"
    },
    {
        "id": "hlt_006",
        "title": "Canada Health AI Framework — Health Canada Guidelines",
        "sector": "Healthcare AI",
        "region": "North America",
        "country": "Canada",
        "content": (
            "Health Canada's regulatory framework for AI medical devices addresses "
            "the unique challenges of adaptive AI systems in healthcare. "
            "AI software meeting medical device definition requires pre-market review "
            "proportionate to patient risk level with Class III and IV devices "
            "requiring most rigorous evaluation. "
            "Canadian framework specifically addresses locked versus adaptive AI "
            "algorithms with different regulatory pathways for each category. "
            "Manufacturers must demonstrate clinical benefit using Canadian patient "
            "population data where differences from other populations are clinically relevant. "
            "Post-market obligations include mandatory reporting of AI-related adverse "
            "events and annual performance summaries for high-risk AI medical devices."
        ),
        "tags": ["Health Canada", "adaptive AI", "pre-market review", "adverse events"],
        "status": "Active",
        "year": 2023,
        "version": "1.0",
        "source_url": "https://www.canada.ca/en/health-canada/services/drugs-health-products/medical-devices/application-information/guidance-documents/software.html"
    },
    {
        "id": "hlt_007",
        "title": "Australia Therapeutic Goods Administration — AI Medical Devices",
        "sector": "Healthcare AI",
        "region": "Oceania",
        "country": "Australia",
        "content": (
            "The Australian Therapeutic Goods Administration regulatory framework "
            "for software including AI as medical devices applies risk-based "
            "classification to healthcare AI applications. "
            "AI diagnostic and treatment software must be included in the Australian "
            "Register of Therapeutic Goods before being supplied. "
            "The TGA participates in international regulatory harmonization through "
            "the International Medical Device Regulators Forum enabling reliance on "
            "overseas regulatory decisions for AI medical devices. "
            "Australian framework specifically addresses AI systems used in aged care "
            "and disability services reflecting national demographic priorities. "
            "Post-market vigilance requirements mandate reporting of AI-related "
            "incidents that could impact patient safety."
        ),
        "tags": ["TGA", "therapeutic goods", "aged care", "regulatory reliance", "Australia"],
        "status": "Active",
        "year": 2021,
        "version": "1.0",
        "source_url": "https://www.tga.gov.au/resources/resource/guidance/software-medical-device-samd-australian-regulatory-guidelines"
    },
    {
        "id": "hlt_008",
        "title": "India Digital Health Mission — AI Healthcare Standards",
        "sector": "Healthcare AI",
        "region": "Asia",
        "country": "India",
        "content": (
            "India's Ayushman Bharat Digital Health Mission establishes standards "
            "for AI integration in the national digital health ecosystem. "
            "AI diagnostic tools used in government healthcare programs must meet "
            "performance standards validated on Indian patient populations. "
            "The mission addresses AI deployment for disease surveillance, outbreak "
            "detection, telemedicine support, and drug quality monitoring. "
            "Special provisions address AI equity in rural healthcare delivery "
            "where connectivity and device limitations affect AI system performance. "
            "India's Central Drugs Standard Control Organisation reviews AI medical "
            "devices with clinical functions while the Ministry of Health coordinates "
            "national AI healthcare governance standards."
        ),
        "tags": ["digital health", "telemedicine", "rural healthcare", "ABDM", "equity"],
        "status": "Active",
        "year": 2021,
        "version": "1.0",
        "source_url": "https://abdm.gov.in/publications"
    },
    {
        "id": "hlt_009",
        "title": "Japan AI Hospital Guidelines — Ministry of Health",
        "sector": "Healthcare AI",
        "region": "Asia",
        "country": "Japan",
        "content": (
            "Japan's Ministry of Health Labour and Welfare establishes guidelines "
            "for AI deployment in hospital settings covering diagnostic imaging, "
            "electronic health records, and clinical decision support. "
            "AI diagnostic imaging systems receive expedited regulatory review "
            "under Japan's progressive approval pathway for breakthrough medical devices. "
            "Guidelines require clear disclosure to patients when AI systems are "
            "involved in their diagnosis or treatment decisions. "
            "Physician responsibility frameworks ensure human accountability is "
            "maintained when AI recommendations are followed or rejected. "
            "Japan's AI hospital initiative integrates AI tools with the national "
            "electronic health record infrastructure serving Japan's aging population."
        ),
        "tags": ["diagnostic imaging", "physician accountability", "aging population", "EHR"],
        "status": "Active",
        "year": 2022,
        "version": "1.0",
        "source_url": "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/iryou/shinryo/index.html"
    },
    {
        "id": "hlt_010",
        "title": "South Korea Digital Healthcare Act — AI Provisions",
        "sector": "Healthcare AI",
        "region": "Asia",
        "country": "South Korea",
        "content": (
            "South Korea's Digital Healthcare Special Act establishes a regulatory "
            "sandbox for innovative digital health including AI medical applications. "
            "The sandbox allows AI healthcare companies to test products with real "
            "patients under regulatory supervision before full market approval. "
            "AI diagnostic software receives fast-track review through the Ministry "
            "of Food and Drug Safety with 100-day review commitment for breakthrough "
            "AI medical devices. "
            "Korean AI healthcare standards address interoperability with the national "
            "health information exchange and electronic health record systems. "
            "The act specifically promotes AI development for rare diseases and "
            "conditions where South Korean medical expertise is internationally recognized."
        ),
        "tags": ["digital healthcare", "sandbox", "fast-track", "rare diseases", "Korea"],
        "status": "Active",
        "year": 2023,
        "version": "1.0",
        "source_url": "https://www.mfds.go.kr/eng/brd/m_62/view.do?seq=75668"
    },

    # ─────────────────────────────────────────
    # FINANCIAL REGULATION — NEW SECTOR (fin_001 to fin_010)
    # ─────────────────────────────────────────
    {
        "id": "fin_001",
        "title": "EU AI in Financial Services — EBA Guidelines",
        "sector": "Financial Regulation",
        "region": "Europe",
        "country": "European Union",
        "content": (
            "The European Banking Authority guidelines on AI in financial services "
            "address internal governance, risk management, and consumer protection "
            "for AI systems used by banks and financial institutions. "
            "Credit scoring, fraud detection, anti-money laundering, and algorithmic "
            "trading AI systems must meet explainability and fairness requirements. "
            "Financial institutions must demonstrate AI models do not produce "
            "discriminatory outcomes for protected characteristics in credit decisions. "
            "Model risk management frameworks must cover AI-specific risks including "
            "data quality, model drift, and adversarial attacks. "
            "EBA coordinates with European Insurance and Occupational Pensions "
            "Authority and European Securities and Markets Authority on cross-sector "
            "AI governance for the entire European financial system."
        ),
        "tags": ["EBA", "credit scoring", "model risk", "anti-discrimination", "financial AI"],
        "status": "Active",
        "year": 2023,
        "version": "1.0",
        "source_url": "https://www.eba.europa.eu/regulation-and-policy/innovation-and-fintech/artificial-intelligence"
    },
    {
        "id": "fin_002",
        "title": "US Federal Reserve — Model Risk Management SR 11-7",
        "sector": "Financial Regulation",
        "region": "North America",
        "country": "United States",
        "content": (
            "The US Federal Reserve and OCC Supervisory Guidance on Model Risk "
            "Management establishes comprehensive requirements for financial models "
            "including AI and machine learning systems at regulated institutions. "
            "Banks must maintain model inventories, conduct independent validation, "
            "and implement ongoing monitoring for all material AI models. "
            "Model risk governance requires board-level oversight and clear policies "
            "for model approval, use, and retirement. "
            "AI models used for credit underwriting, stress testing, and capital "
            "planning receive highest scrutiny given systemic risk implications. "
            "Guidance addresses explainability requirements for consumer-facing AI "
            "decisions under fair lending laws including Equal Credit Opportunity Act."
        ),
        "tags": ["model risk", "validation", "Federal Reserve", "fair lending", "stress testing"],
        "status": "Active",
        "year": 2011,
        "version": "3.0",
        "source_url": "https://www.federalreserve.gov/supervisionreg/srletters/sr1107.htm"
    },
    {
        "id": "fin_003",
        "title": "UK FCA AI and Machine Learning in Financial Services",
        "sector": "Financial Regulation",
        "region": "Europe",
        "country": "United Kingdom",
        "content": (
            "The UK Financial Conduct Authority guidance on AI and machine learning "
            "in financial services establishes expectations for fair explainable and "
            "accountable AI use across regulated financial firms. "
            "FCA requires firms to ensure AI systems treat customers fairly and "
            "provide explanations for automated decisions affecting consumer rights. "
            "Senior manager accountability regime extends to AI governance requiring "
            "named individuals responsible for AI model risk at each institution. "
            "The FCA Digital Sandbox provides testing environment for innovative "
            "AI financial services before regulatory authorization. "
            "Anti-money laundering AI systems must be validated for effectiveness "
            "and reviewed for potential discrimination against ethnic minority communities."
        ),
        "tags": ["FCA", "consumer protection", "accountability", "AML", "Digital Sandbox"],
        "status": "Active",
        "year": 2022,
        "version": "1.0",
        "source_url": "https://www.fca.org.uk/publications/discussion-papers/dp22-4-artificial-intelligence-and-machine-learning"
    },
    {
        "id": "fin_004",
        "title": "Monetary Authority of Singapore — FEAT Principles",
        "sector": "Financial Regulation",
        "region": "Asia",
        "country": "Singapore",
        "content": (
            "The Monetary Authority of Singapore Fairness Ethics Accountability and "
            "Transparency principles establish voluntary governance standards for AI "
            "use in Singapore's financial sector. "
            "Financial institutions are encouraged to implement FEAT principles for "
            "customer-facing AI applications including credit assessment, insurance "
            "underwriting, and investment advisory services. "
            "The MAS Veritas initiative provides open-source assessment methodology "
            "allowing financial institutions to evaluate their AI systems against "
            "FEAT principles with standardized metrics. "
            "Singapore's AI governance approach emphasizes industry self-regulation "
            "with MAS providing guidance and monitoring rather than prescriptive rules. "
            "The framework positions Singapore as leading global financial center "
            "for responsible AI adoption in financial services."
        ),
        "tags": ["FEAT", "MAS", "Veritas", "fairness", "financial AI", "self-regulation"],
        "status": "Active",
        "year": 2019,
        "version": "2.0",
        "source_url": "https://www.mas.gov.sg/development/fintech/veritas"
    },
    {
        "id": "fin_005",
        "title": "Basel Committee — Principles for Operational Resilience and AI",
        "sector": "Financial Regulation",
        "region": "Global",
        "country": "International",
        "content": (
            "The Basel Committee on Banking Supervision principles address operational "
            "resilience risks from AI and machine learning systems at globally "
            "systemically important financial institutions. "
            "Banks must identify critical AI systems supporting core business services "
            "and ensure continuity through disruptions including AI model failures. "
            "Third-party AI provider risk management requires enhanced due diligence "
            "and exit strategies for critical AI dependencies. "
            "Concentration risk from shared AI providers across multiple systemically "
            "important banks creates systemic risk requiring macroprudential oversight. "
            "International coordination through the Financial Stability Board addresses "
            "cross-border AI risks in globally interconnected financial markets."
        ),
        "tags": ["Basel", "operational resilience", "systemic risk", "third-party risk", "FSB"],
        "status": "Active",
        "year": 2022,
        "version": "1.0",
        "source_url": "https://www.bis.org/bcbs/publ/d516.htm"
    },
    {
        "id": "fin_006",
        "title": "India RBI Framework for Digital Lending and AI",
        "sector": "Financial Regulation",
        "region": "Asia",
        "country": "India",
        "content": (
            "The Reserve Bank of India framework for digital lending addresses AI "
            "use in credit assessment, collections, and customer service for India's "
            "rapidly growing digital lending sector. "
            "Regulated lenders must ensure AI credit models comply with fair practices "
            "code and do not discriminate based on constitutionally protected characteristics. "
            "Loan service providers using AI must maintain human oversight for "
            "significant credit decisions and provide borrowers with reasons for rejection. "
            "The framework mandates data privacy protections for borrower information "
            "collected through mobile applications and digital platforms. "
            "RBI's regulatory sandbox allows testing of innovative AI lending products "
            "under regulatory supervision before full market launch."
        ),
        "tags": ["RBI", "digital lending", "credit AI", "fair practices", "regulatory sandbox"],
        "status": "Active",
        "year": 2022,
        "version": "1.0",
        "source_url": "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=54085"
    },
    {
        "id": "fin_007",
        "title": "China PBOC — Fintech Development Plan and AI Governance",
        "sector": "Financial Regulation",
        "region": "Asia",
        "country": "China",
        "content": (
            "China's People's Bank Fintech Development Plan establishes governance "
            "requirements for AI applications in Chinese financial services including "
            "central bank digital currency, payment systems, and credit markets. "
            "Financial AI systems must undergo regulatory review and obtain People's "
            "Bank approval before deployment at systemically important financial institutions. "
            "Algorithmic trading systems face specific circuit breakers and monitoring "
            "requirements to prevent flash crashes and market manipulation. "
            "The plan mandates AI explainability for consumer credit decisions and "
            "prohibits use of prohibited data categories including social scores in "
            "financial AI models. "
            "PBOC coordinates AI governance with banking, securities, and insurance "
            "regulators through the Financial Stability and Development Committee."
        ),
        "tags": ["PBOC", "fintech", "CBDC", "algorithmic trading", "credit AI"],
        "status": "Active",
        "year": 2022,
        "version": "2.0",
        "source_url": "http://www.pbc.gov.cn/en/3688110/3688172/4157443/4399780/index.html"
    },
    {
        "id": "fin_008",
        "title": "Australia APRA Prudential Practice Guide — AI and Model Risk",
        "sector": "Financial Regulation",
        "region": "Oceania",
        "country": "Australia",
        "content": (
            "The Australian Prudential Regulation Authority guidance on model risk "
            "management addresses AI and machine learning models at banks, insurers, "
            "and superannuation funds under APRA supervision. "
            "Regulated entities must maintain comprehensive model inventories and "
            "implement risk-proportionate validation and ongoing monitoring processes. "
            "AI models driving material business decisions require independent validation "
            "by qualified personnel with no involvement in model development. "
            "APRA's prudential standard CPS 230 on operational risk management "
            "extends to AI-related operational risks including model failure and "
            "third-party AI provider dependencies. "
            "Climate risk AI models used for stress testing face additional scrutiny "
            "given data limitations and model uncertainty in long-term projections."
        ),
        "tags": ["APRA", "model risk", "prudential", "operational risk", "climate risk"],
        "status": "Active",
        "year": 2023,
        "version": "1.0",
        "source_url": "https://www.apra.gov.au/model-risk-management-guidance-for-financial-institutions"
    },
    {
        "id": "fin_009",
        "title": "South Africa FSCA — Guidance on AI in Financial Services",
        "sector": "Financial Regulation",
        "region": "Africa",
        "country": "South Africa",
        "content": (
            "The South African Financial Sector Conduct Authority guidance addresses "
            "AI use in financial services with focus on treating customers fairly "
            "and preventing algorithmic discrimination. "
            "Financial service providers must ensure AI systems used for insurance "
            "underwriting and credit assessment do not unfairly discriminate based "
            "on race, gender, or disability in violation of equality legislation. "
            "Robo-advisory and automated investment services must meet suitability "
            "requirements ensuring AI recommendations match client risk profiles. "
            "The guidance addresses unique South African context including financial "
            "exclusion of historically disadvantaged communities and AI systems "
            "potentially perpetuating apartheid-era economic inequalities."
        ),
        "tags": ["FSCA", "discrimination", "financial exclusion", "robo-advisory", "South Africa"],
        "status": "Active",
        "year": 2022,
        "version": "1.0",
        "source_url": "https://www.fsca.co.za/Regulatory%20Frameworks/Pages/Fintech.aspx"
    },
    {
        "id": "fin_010",
        "title": "Kenya Central Bank — Digital Finance and AI Framework",
        "sector": "Financial Regulation",
        "region": "Africa",
        "country": "Kenya",
        "content": (
            "The Central Bank of Kenya framework for digital financial services "
            "establishes governance requirements for AI systems in mobile money, "
            "digital lending, and payment services serving Kenya's large unbanked population. "
            "Mobile money AI systems must implement transaction monitoring for "
            "fraud prevention while avoiding false positives that exclude legitimate users. "
            "Digital lending AI must comply with fair lending principles and provide "
            "credit assessment explanations to borrowers in accessible language. "
            "The framework addresses AI risks in agent banking networks where "
            "automated decisions affect financial access for rural communities. "
            "Kenya's M-Pesa ecosystem generates unique AI governance challenges "
            "as world's most advanced mobile money infrastructure serving millions."
        ),
        "tags": ["CBK", "mobile money", "M-Pesa", "financial inclusion", "digital lending"],
        "status": "Active",
        "year": 2022,
        "version": "1.0",
        "source_url": "https://www.centralbank.go.ke/digital-financial-services/"
    },
]