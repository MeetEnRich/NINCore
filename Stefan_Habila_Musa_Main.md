# NINCORE: DESIGN AND IMPLEMENTATION OF A NIN-CENTRIC IDENTITY GOVERNANCE AND RISK ENGINE WITH MACHINE LEARNING

**BY**

**STEFAN, Habila Musa**

**(2021/CP/CSC/0296)**

A PROJECT REPORT SUBMITTED TO THE DEPARTMENT OF COMPUTER SCIENCE, FACULTY OF COMPUTING, IN PARTIAL FULFILLMENT OF THE REQUIREMENTS FOR THE AWARD OF BACHELOR OF SCIENCE (BSc) DEGREE IN COMPUTER SCIENCE OF FEDERAL UNIVERSITY OF LAFIA.

**MARCH, 2026**

---

## CHAPTER ONE: INTRODUCTION

### 1.1 Background of the Study

The digital identity landscape in Nigeria is currently undergoing an unprecedented shift toward a centralized, NIN-centric governance ecosystem. At the heart of this transformation is the National Identification Number (NIN), mandated by the Federal Government to serve as the primary key for accessing social services, financial systems, and telecommunications infrastructure. Despite reaching over 126 million enrollments by late 2025, the utilization of this consolidated data for real-time risk assessment and cross-sectoral governance remains a critical, unresolved challenge (Onanuga, 2025).

Historically, Nigerian public administration has relied on traditional, often paper-based administrative methods that were slow, opaque, and fostered a profound lack of trust in government institutions (Monye & Koker, 2022). The emergence of the NIN was intended to harmonize these disparate records. However, as digital interactions scale exponentially, the existing implementation remains fundamentally deterministic — it merely validates that a NIN exists and that it matches a stored name. This 'static' validation is no longer sufficient to protect against sophisticated threats including identity theft, synthetic identity fraud, and account takeovers.

Modern identity management requires a paradigm shift toward Identity Governance (IG), which refers to the policy-based, continuous management of digital identities and access rights. By integrating Machine Learning (ML), NINCore introduces a Probabilistic Risk Engine that monitors how an identity is being used across multiple sectors, including Banking, Health, Education, Transport, and Telecommunications, to detect behavioral anomalies in real-time. This project aligns with the Nigeria Data Protection Act (NDPA 2023), ensuring that identity linkage is secure, transparent, and risk-aware.

### 1.2 Statement of the Problem

Despite the formal mandate of the National Identity Management Commission (NIMC) to unify Nigerian identity systems, the current ecosystem remains critically fragmented across multiple autonomous databases that do not effectively communicate with each other (National Security Adviser, 2024). This lack of coordination has created exploitable blind spots in Nigeria's national security architecture, allowing criminal elements and state-level threat actors to operate across different sectoral credentials undetected.

The existing Nigerian Identity Management System (NIMS) faces three specific, interlocking challenges that NINCore is designed to address:

**First, Identity Silos and Lack of Interoperability:** Despite the government's push for NIN linkage, various government agencies — including the Central Bank of Nigeria (CBN), the National Health Insurance Authority (NHIA), and the Federal Road Safety Corps (FRSC) — still maintain disconnected databases. This lack of a unified governance layer makes it practically impossible to track a citizen's overall 'risk profile' across different service platforms (Eyikorogha & Chigozie, 2025).

**Second, Absence of Real-Time Behavioral Risk Assessment:** Traditional systems operate on deterministic, rule-based logic (e.g., 'Is the NIN valid? Yes/No'). They cannot detect complex fraudulent behavioral patterns, such as a single NIN being used simultaneously in two geographically distant locations — a pattern known as 'Impossible Travel' — or a sudden, unexplained surge in linked account requests across multiple sectors (Rodriguez et al., 2025).

**Third, Governance Deficit in Data Privacy and Audit:** There is a significant absence of automated governance engines capable of enforcing the principle of 'Least Privilege' access across Nigeria's digital identity infrastructure. Currently, once a sector is granted access to a NIN record, there is very limited automated oversight on how that data is subsequently governed, who accessed it, when, and whether that access poses an ongoing security risk. This leaves a critical transparency gap that undermines public trust in the NIN system (Philips, 2026).

### 1.3 Aim and Objectives of the Study

The primary aim of this project is to design and implement NINCore, an ML-powered Identity Governance and Risk Engine that provides a centralized, secure, and intelligent framework for managing NIN-centric identities across Nigeria's five key sectors.

The specific objectives are to:

- Architect an interoperable linkage layer that connects disparate sector records (Banking, Health, Education, Transport, and Telecommunications) using the NIN as a primary key, without compromising the data decentralization of individual agencies.
- Develop a high-fidelity synthetic dataset representing multi-sector Nigerian identity behaviors to train and rigorously test a predictive risk model, in compliance with the Nigeria Data Protection Regulation (NDPR).
- Implement a Random Forest Machine Learning algorithm to calculate dynamic 'Identity Confidence Scores' based on a rich set of behavioral and transactional features.
- Design a governance dashboard for system administrators to visualize national identity risk trends, investigate flagged entities, and manage sector-specific access logs.
- Evaluate the overall performance of the risk engine using standard ML metrics, including Accuracy, Precision, Recall (Sensitivity), and the F1-Score, with particular emphasis on Recall as the primary performance indicator for a security-critical system.

### 1.4 Scope and Limitation of the Study

#### 1.4.1 Scope

This project focuses on the governance of identities across five key sectors of the Nigerian economy: Financial/Banking (using Bank Verification Number - BVN), Health (National Health Insurance Authority - NHIA), Education (JAMB/WAEC Examination Numbers), Transport (Federal Road Safety Corps - FRSC License), and Telecommunications (SIM Card Registry). The system will simulate the linkage of these sector records to a central NIN using synthetic data. The Machine Learning component is scoped to the Random Forest Classifier algorithm, chosen for its high interpretability in governance auditing contexts and its demonstrated strength in handling tabular, multi-feature identity datasets.

#### 1.4.2 Limitation

Due to the sensitive and restricted nature of the National Identity Management Commission (NIMC) database and the explicit restrictions imposed by the Nigeria Data Protection Regulation (NDPR) on the use of live citizen data in research, this project will not utilize real, live, private citizen data. Instead, a robust, high-fidelity synthetic dataset will be algorithmically generated using Python libraries to mimic Nigerian demographic and sectoral behavioral patterns. The system further assumes that all five participating sector databases are technically capable of exposing a secure Application Programming Interface (API) for linkage purposes. The deployment of physical biometric hardware and live integration with NIMC's production servers are explicitly outside the scope of this prototype.

### 1.5 Significance of the Study

The development and demonstration of NINCore provides several critical, multi-layered benefits to Nigeria's national digital governance framework:

- **National Security:** The unified risk engine provides a cross-sectoral intelligence capability, enabling security agencies to identify and trace suspicious behavioral patterns across institutional boundaries — a capability that is entirely absent from the current NIMS model (National Security Adviser, 2024).
- **Institutional Accountability and Transparency:** By logging all data access events in a tamper-evident audit trail, the system ensures full transparency and regulatory accountability, which is critical for building public and institutional trust in the NIN system (NIMC, 2025).
- **Operational Efficiency:** By automating identity risk assessment using machine learning, the system drastically reduces the administrative burden of manual governance reviews, mitigating 'review fatigue' — a documented failure mode in human-led identity management (Philips, 2026).
- **Privacy-Preserving Architecture:** The NINCore model demonstrates that it is technically feasible and architecturally sound to link cross-sectoral records for governance purposes without the significant technical and political risks associated with physically merging sensitive, large-scale national databases (Eyikorogha & Chigozie, 2025).

### 1.6 Definition of Operational Terms

- **Identity Governance (IG):** The sub-field of identity management that provides policy-based visibility into who has access to what, ensures that access is appropriate for a given role, and continuously monitors for deviations from established behavioral baselines.
- **Risk Engine:** A computational module that uses a combination of deterministic heuristic rules and probabilistic machine learning algorithms to assign a numerical 'Identity Confidence Score' to an entity or transaction based on its historical and real-time behavioral data.
- **NIN-Centricity:** An architectural philosophy where the National Identification Number serves as the 'Parent Identity' anchor — the singular, canonical reference point to which all other functional sector identities (BVN, Passport Number, Voter's Card, etc.) are mapped and from which all risk assessments are derived.
- **Synthetic Data:** Algorithmically generated data that statistically mimics the distributional properties of real-world Nigerian identity data while containing absolutely no personally identifiable information (PII), ensuring full compliance with data privacy regulations.
- **Identity Confidence Score:** A probabilistic score, ranging from 0% to 100%, generated by the Random Forest model to indicate the degree of confidence that an identity transaction is legitimate. A low score indicates a high-risk, potentially fraudulent interaction.
- **Interoperable Linkage Layer:** A middleware architectural component that serves as a secure bridge between disparate sector databases, enabling them to contribute telemetry data for risk assessment without physically sharing or merging their underlying data stores.

### 1.7 Organization of the Work

This project report is structured into five distinct chapters, each serving a specific academic and technical function:

**Chapter One** provides the foundational context for the research, encompassing the background of Nigeria's identity governance crisis, the specific statement of the problem, the aims and objectives of the NINCore system, and the scope and significance of the study.

**Chapter Two** presents a comprehensive literature review, critically analyzing existing works and seminal research on AI-driven identity governance, the evolution of the Nigerian NIN ecosystem, ML frameworks for risk and compliance, and the specific research gaps that this project seeks to fill.

**Chapter Three** details the system analysis and methodology, covering the analysis of the existing NIMS model and its weaknesses, a full description of the proposed NINCore architecture, the methodology adopted (Prototyping Model), the technical specifications including the synthetic dataset design and evaluation metrics, and the complete system design encompassing the database schema, UML diagrams, API specification, and system flowchart.

**Chapter Four** documents the system implementation and testing, presenting the development environment, the implementation of core modules, the testing strategy, and the quantitative results obtained from evaluating the Random Forest risk engine against the synthetic dataset.

**Chapter Five** provides the conclusion of the research, summarizing key findings, stating recommendations for the practical deployment of NIN-centric governance systems, and identifying avenues for future work.

---

## CHAPTER TWO: LITERATURE REVIEW

### 2.1 Introduction

The governance of digital identities has transitioned from a mere administrative requirement to a foundational pillar of national security and economic resilience. In the Nigerian context, this evolution is increasingly centered on the National Identification Number (NIN), which serves as the unique anchor for verifying the identities of over 200 million citizens (Eyikorogha & Chigozie, 2025). Identity Governance and Administration (IGA) refers to the strategic framework used to manage user identities and access rights, ensuring that only authorized individuals can access specific resources for legitimate, verifiable reasons (Omada, 2026).

As digital ecosystems expand in complexity and scale, traditional rule-based identity systems are demonstrably failing to detect sophisticated, multi-vector fraud patterns, including synthetic identity theft and cross-platform credential abuse (Rodriguez et al., 2025). This critical failure has necessitated the integration of Artificial Intelligence (AI) and Machine Learning (ML) to provide real-time behavioral monitoring and predictive risk scoring capabilities (Philips, 2026). This chapter examines the current state of identity management in Nigeria, explores the technical methodologies underpinning ML-driven risk engines, and critically analyzes the global shift toward 'continuous governance' drawing from a research window spanning 2018 to 2026.

### 2.2 Conceptual Framework

#### 2.2.1 Identity Governance and Administration (IGA)

Identity Governance (IG) represents the policy-based management of digital identities, a discipline that has evolved significantly from its predecessor, traditional Identity Management (IdM). While IdM focuses primarily on the technical mechanics of authentication (e.g., password management and biometric verification), IGA focuses on the higher-order governance questions: 'Who should have access to what?' and 'How is that access actually being used, and does it comply with established policy?' In the Nigerian context, this distinction is critically important because the National Identification Number (NIN) serves as the 'Parent Identity' anchor for all other sectoral records, making its governance a matter of national consequence.

The core components of a modern IGA framework include Role-Based Access Control (RBAC), which restricts system access based on predefined roles; Audit and Compliance Logging, which creates a tamper-evident record of all data access events; Access Certification, which involves periodic reviews to verify that access rights remain appropriate; and Lifecycle Management, which governs the creation, modification, and revocation of identity records throughout their operational lifespan.

#### 2.2.2 Risk-Based Authentication (RBA) and Continuous Governance

The shift from 'static' to 'risk-based' governance represents the central theoretical contribution of the NINCore project. Traditional static systems grant or deny access based on a single, binary 'Yes/No' check of credentials at the point of login. Risk-Based Authentication (RBA), however, uses a continuously operating 'Risk Engine' to analyze a rich stream of behavioral telemetry — including login frequency, geographic velocity, device reputation, and access time patterns — to calculate a real-time Identity Confidence Score. This enables 'continuous governance,' a model where the system monitors and re-evaluates the trustworthiness of a user's identity not just at login, but throughout an entire session and across all subsequent interactions.

This paradigm is particularly well-suited to Nigeria's multi-sectoral NIN linkage challenge. When a citizen's NIN is used to access a Banking portal in Lagos and, simultaneously, a Health Insurance portal in Kano, a continuous governance engine can immediately flag this as a potential 'Impossible Travel' anomaly and request secondary verification — a response that a static system is architecturally incapable of generating.

#### 2.2.3 Supervised Machine Learning in Fraud Detection

Supervised Machine Learning represents the technical backbone of the NINCore risk engine. In a supervised learning framework, a model is trained on a labeled dataset — in this context, a synthetic dataset containing identity records labeled as either 'Legitimate' (0) or 'Suspicious' (1). The model learns to identify the combination of features that distinguish these two classes and can then apply this learned knowledge to classify new, previously unseen identity events.

The Random Forest Classifier, the algorithm selected for NINCore, is an ensemble learning method that constructs a large number of individual Decision Trees during the training process. Each tree votes on the classification of a new data point, and the majority vote determines the final prediction. This ensemble approach confers two critical advantages for a governance application: robustness against overfitting; and Feature Importance — the ability to quantify the relative contribution of each input feature to the final risk prediction. This latter property is directly linked to the emerging field of Explainable AI (XAI), which is crucial for building institutional trust in automated governance systems.

### 2.3 Review of Empirical Studies

#### 2.3.1 AI-Driven Joint National Identity Databases and Security

Research presented at the 2024 Cyber Secure Nigeria Conference represents the most directly relevant strategic work to this project (National Security Adviser, 2024). The study argues compellingly that the fragmentation of Nigerian identity systems across uncoordinated silos — maintained by agencies like NIMC, INEC, and the FRSC — constitutes a primary, existential threat to national security. The paper documents specific threat scenarios in which criminal elements actively exploit the disconnection between these databases to operate across multiple sectors undetected.

The study's proposed solution is an AI-driven joint database domiciled in the Office of the National Security Adviser, which would utilize machine learning for threat prediction and real-time alerting. This work is significant because it provides the high-level strategic and policy justification for the 'NIN-centric linkage' architecture that NINCore implements at the prototype level. However, the study is primarily conceptual and lacks the detailed algorithmic implementation that NINCore provides.

#### 2.3.2 AI-Powered Risk Assessment for Data Governance Compliance

A landmark 2025 study on AI-powered risk assessment frameworks documented the technical shift from reactive post-audit governance to preventive, real-time governance (ResearchGate, 2025). The researchers constructed an ensemble architecture combining Random Forest Classifiers (RFC) for initial, broad-spectrum risk prediction and Gradient Boosted Trees (XGBoost) to refine precision in identifying high-severity risks within large-scale compliance datasets.

The framework achieved an AUC-ROC score of 0.97, a remarkable result that significantly outperformed traditional rule-based governance methods. The study concluded that ensemble methods are demonstrably superior for identity risk tasks because they can model the complex, non-linear feature interactions that characterize real-world fraud patterns — interactions that simple rule-based systems cannot capture. This result provides the algorithmic justification for NINCore's selection of the Random Forest Classifier.

#### 2.3.3 ML Frameworks for Governance, Risk, and Compliance (GRC)

Dr. Upakar Bhatta's 2025 research explored the practical application of machine learning pipelines to evaluate GRC risks at scale (Bhatta, 2025). The study's most technically significant contribution for this project is its rigorous treatment of the class imbalance problem — a fundamental challenge in any fraud detection system. By definition, fraudulent or suspicious identity events represent a small minority of all identity interactions. If left unaddressed, this imbalance causes ML models to become overwhelmingly biased toward predicting the majority 'Legitimate' class, effectively ignoring the rare but critically important 'Suspicious' events the system was built to detect.

Bhatta's work applied the Synthetic Minority Oversampling Technique (SMOTE), which addresses this by algorithmically generating new, synthetic samples of the minority 'Suspicious' class to rebalance the training dataset. This technical blueprint is directly adopted in the NINCore methodology. The study also employed Azure service logs to extract nine key behavioral features, a feature engineering approach that directly informed NINCore's own feature selection process, particularly the use of behavioral telemetry such as access frequency and geographic velocity.

#### 2.3.4 The Impact of AI on Identity Governance and Administration

Alex Philips' 2026 study provides the most compelling quantitative evidence for the operational benefits of AI-enabled IGA systems (Philips, 2026). Through a comparative analysis of organizations that adopted AI-enabled IGA versus those relying on traditional manual governance, the research found that AI-enabled systems reduced the average time required for access certifications by 52%. More strikingly, the identification of high-risk access outliers increased by over 300%.

The research introduces a critical concept directly relevant to NINCore: the 'Explainability Gap.' The study found that the adoption of AI governance systems was significantly hindered when administrators could not understand the reasoning behind a risk flag. This finding strongly validates NINCore's design decision to use the Random Forest algorithm, which provides native Feature Importance scores, over more opaque 'black box' deep learning models.

#### 2.3.5 Identity Technologies in the Nigerian Fintech Ecosystem

A 2025 review of AI's role in Nigeria's fintech sector highlighted its transformative potential for making authentication more efficient and accessible (Magna Scientia, 2025). The study introduced the 'Fraudaeck-AI' model, which leverages neural networks to monitor network interactions and mitigate cyber fraud within Nigeria's banking sector, achieving a promising 93% accuracy rate. The research notes that while AI-driven identity verification has demonstrated clear efficacy, its implementation in Nigeria is still in an early stage due to challenges related to high infrastructure costs, regulatory uncertainty, and the need for large, clean training datasets.

This 'infant stage' characterization is directly addressed by NINCore's use of synthetic data. By demonstrating that a high-performing risk engine can be trained on algorithmically generated, privacy-compliant synthetic data rather than sensitive live data, this project lowers the most significant barrier to adoption in the Nigerian context.

#### 2.3.6 User-Centric Analysis of Nigeria's National Identification Number System

A 2024 doctoral study from Loughborough University conducted a critical user-centric evaluation of the NIN system's real-world impact (Loughborough University, 2024). The research identified a significant 'Paradox of Intention and Outcome': while the NIN system was designed to strengthen security and facilitate financial inclusion, its implementation has produced unintended negative consequences, including heightened privacy concerns among citizens, digital exclusion in rural communities, and what the researcher terms 'governance opacity.'

This finding directly informs NINCore's design philosophy. The system's Audit Log Dashboard is specifically designed to address governance opacity by providing administrators with a transparent, comprehensible record of every data access event. The research also reinforces the importance of the project's privacy-by-design approach.

### 2.4 Summary of Related Works

**Table 2.1: Summary of Related Works**

| S/N | Author (Year) | Focus Area | Methodology | Key Findings / Limitation | NINCore Gap |
|-----|---------------|------------|-------------|--------------------------|-------------|
| 1 | NSA (2024) | National Identity Security | Proposed AI-driven joint database; real-time alert systems | Fragmentation is a primary security threat. Lacks specific algorithmic implementation | Fills with RFC algorithm and prototype implementation |
| 2 | ResearchGate (2025) | AI Risk Assessment | RFC & XGBoost ensemble; BERT for clause extraction | AUC-ROC of 0.97. Requires high-quality foundational data | Addresses with high-fidelity synthetic data generation |
| 3 | Bhatta, U. (2025) | GRC Risks | Azure Logs, SMOTE oversampling, Random Forest | ML effectively evaluates GRC risks. Limited to cloud GRC environments | Applies SMOTE methodology to NIN identity context |
| 4 | Philips, A. (2026) | AI-Enabled IGA | Predictive analytics and clustering for role mining | 52% reduction in review time; 300% increase in risk outlier detection. Explainability gap remains | Uses RFC Feature Importance to close the explainability gap |
| 5 | Omada (2026) | State of IGA | Primary survey research of enterprise IGA leaders | Non-human identities are the fastest-growing governance risk. Focused on large enterprise only | Extends governance concepts to Nigerian national identity context |
| 6 | Eyikorogha & Chigozie (2025) | NIMS Performance | Qualitative system review; infrastructure gap analysis | Silo fragmentation and manual processes are core failures. No software-based solution provided | Provides the software prototype that addresses identified gaps |
| 7 | Loughborough Univ. (2024) | NIN User-Centric Analysis | Qualitative user-centric analysis; ethnographic research | Governance opacity and digital exclusion undermine NIN trust. No technical solution provided | Dashboard design directly addresses governance opacity |

### 2.5 Research Gaps and Project Contributions

A critical synthesis of the reviewed literature reveals four persistent gaps that NINCore is specifically positioned to address:

**The 'Merger vs. Linkage' Gap:** While the literature consistently identifies database fragmentation as a primary security risk (NSA, 2024; Eyikorogha & Chigozie, 2025), proposed solutions predominantly suggest physically 'merging' national databases. NINCore makes a distinct architectural contribution by implementing a privacy-preserving interoperable linkage layer that connects sectors for risk intelligence without requiring the physical co-location of their underlying data.

**The 'Nigerian Context' Gap:** The majority of empirical ML research cited was conducted using Western or generic datasets that do not reflect the specific behavioral patterns of Nigerian citizens interacting with the BVN, NHIA, JAMB, and FRSC systems. NINCore directly addresses this by generating a synthetic NIN-centric dataset specifically calibrated to mimic Nigerian sectoral behaviors.

**The 'Explainability and Governance Transparency' Gap:** A recurring limitation across multiple studies is the 'Explainability Gap' (Philips, 2026; Loughborough University, 2024). NINCore specifically selects the Random Forest algorithm, over higher-accuracy but less interpretable alternatives, precisely because its native Feature Importance output allows administrators to understand and justify every risk flag — a legal and ethical requirement under the NDPA 2023.

**The 'Real-Time Synthetic Data Feasibility' Gap:** Research on Nigerian identity systems consistently cites the inaccessibility of live NIMC data as a barrier to R&D. NINCore demonstrates a practical, replicable methodology for using Python-based synthetic data generation to create research-grade identity datasets that faithfully reproduce the statistical properties of real-world Nigerian identity data while maintaining absolute data privacy compliance.

### 2.6 Conclusion

The literature review establishes a clear and urgent imperative: while Nigeria has built a foundational identity platform through the NIN, the system is currently crippled by siloed databases, deterministic validation logic, and manual governance processes that are fundamentally inadequate for the scale and sophistication of modern identity threats. Modern machine learning techniques, particularly ensemble methods like the Random Forest Classifier, augmented with SMOTE for class balancing, offer a technically robust and operationally proven alternative for automating risk assessment. By implementing a NIN-centric prototype that links sectoral data through a machine learning risk engine, the NINCore project aligns with and advances the global shift toward continuous, intelligent, and explainable identity governance.

---

## CHAPTER THREE: SYSTEM ANALYSIS, DESIGN AND METHODOLOGY

### 3.1 Description of the Existing Model

The existing identity management model in Nigeria is the National Identity Management System (NIMS), operated by the National Identity Management Commission (NIMC). This model functions primarily as a centralized biometric repository where the National Identification Number (NIN) serves as the primary key for citizen records. The current verification workflow relies on the Mobile Web Services (MWS) and Verification Service Providers (VSP) framework, which allows authorized third-party institutions to query the National Identity Database (NIDB) for basic demographic record retrieval and simple 'Yes/No' biometric match responses.

The fundamental operational logic of this model is deterministic and rule-based: authentication is granted if and only if the presented credentials match the stored record. It does not include a cross-sectoral 'Risk Engine' capable of monitoring behavioral patterns across different government agencies in real-time. Identity lifecycle management tasks are largely manual, slow, and critically lack a unified 'Parent Identity' governance oversight layer.

#### 3.1.1 Strengths of the Existing Model

- **Centralized Data Repository:** The NIMC database provides a single, authoritative source of truth for foundational identity data in Nigeria, establishing the NIN as the canonical citizen identifier.
- **Biometric Uniqueness:** The mandatory capture of ten-fingerprint and facial image data ensures that each NIN is unique, with a robust de-duplication process preventing duplicate registrations.
- **Widespread Enrollment:** With over 126 million enrollments, the system has achieved significant scale, representing the largest identity database on the African continent.
- **Baseline Security Protocols:** Data transmission between the NIMC portal and authorized Verification Service Providers relies on encrypted communications protocols (TLS/SSL) to maintain basic data confidentiality during transit.

#### 3.1.2 Weaknesses of the Existing Model

- **Database Fragmentation (Identity Silos):** While NIMC holds the core biographic data, all other sectors — Banking, Health, Education, Transport, and Telecommunications — maintain entirely autonomous databases that do not communicate with each other or with NIMC in real-time, creating critical security blind spots.
- **Absence of Behavioral Risk Analysis:** The existing system is structurally incapable of detecting behavioral anomalies such as 'Impossible Travel' because it relies exclusively on static credential matching.
- **Manual and Bureaucratic Governance:** Identity lifecycle management events are processed manually, creating dangerous delays and systemic governance latency.
- **Elevated False Positive Rates:** The existing deterministic rule-based mechanisms have demonstrated a significant and growing inability to adapt to modern, evolving fraud patterns such as synthetic identity creation (Rodriguez et al., 2025).

### 3.2 Description of the Improved Model (NINCore)

The improved model, NINCore, is an intelligent, NIN-centric Identity Governance and Risk Engine. Unlike the existing NIMS model, NINCore introduces a 'Parent Identity' framework that establishes the NIN as the universal anchor for a federated, interoperable identity ecosystem. It connects records across five independent sectors — Banking, Health, Education, Transport, and Telecommunications — without physically merging their underlying databases, thereby preserving institutional data autonomy while enabling cross-sectoral risk intelligence.

The core of the system is a Machine Learning Risk Engine that assigns a real-time 'Identity Confidence Score' to every identity verification request based on a rich combination of behavioral telemetry and historical interaction patterns. The system integrates a suite of automated Governance, Risk, and Compliance (GRC) modules to manage the complete identity lifecycle, enforce role-based access control, and maintain a transparent, tamper-evident audit log.

*Figure 1: NINCore Conceptual Diagram*

#### 3.2.1 Justification for the Improved Model

The transition from NIMS to NINCore is justified on three distinct grounds:

1. **Velocity of Modern Identity Fraud:** Contemporary identity theft operates at machine speed — milliseconds — while human auditors and manual governance processes operate on timescales of days or weeks. An automated, continuously operating risk engine is a fundamental operational necessity.

2. **Pattern Recognition Superiority:** Deterministic rule-based systems can only detect fraud patterns that have been explicitly anticipated and programmed. The Random Forest model can detect novel, complex, non-linear fraud patterns — such as the correlation between an unusual device reputation, elevated login frequency, and a geographic velocity anomaly — that no human analyst could enumerate in advance.

3. **Governance Scalability:** As millions of additional Nigerians link their NINs to an expanding portfolio of services, manual governance processes become mathematically unsustainable. A centralized ML risk engine provides a uniform, consistent security standard across all agencies simultaneously.

*Figure 2: NINCore System Architecture*

### 3.3 Methodology Adopted

#### 3.3.1 Choice of Methodology: The Prototyping Model

This project adopts the Prototyping Software Development Model as its overarching methodology. The Prototyping Model is the most appropriate choice for NINCore because the system occupies the intersection of two rapidly evolving technical domains — Software Engineering and Machine Learning — where requirements cannot be fully specified upfront and where iterative refinement based on empirical feedback is essential.

Unlike a traditional Waterfall methodology, the Prototyping Model allows for continuous iteration and refinement. This is a critical requirement for ML-based governance systems because the performance of the Random Forest model cannot be known until it is trained and evaluated on real data. The project follows four distinct prototyping phases:

1. **Requirements Gathering and Analysis:** Identifying the five sector data fields (NIN, BVN, NHIA, JAMB, FRSC License), the specific behavioral risk parameters (Geographic Velocity, Login Frequency, Device Reputation), and the governance reporting requirements for the dashboard.
2. **Quick Design and Architecture:** Creating the architectural linkage blueprint between the sector databases and the API structure, and designing the relational database schema with the NIN as the primary key.
3. **Prototype Building and Model Training:** Algorithmically generating the 50,000-record synthetic dataset, applying SMOTE balancing, training the initial Random Forest model, and building the Streamlit dashboard prototype.
4. **User and Supervisor Evaluation and Refinement:** Testing the dashboard's visualization clarity, evaluating the API's risk assessment accuracy, and iteratively refining the model's hyperparameters based on F1-Score and Recall metrics.

#### 3.3.2 Justification for Prototyping in an ML Governance Context

Unlike conventional software projects, an ML-based governance engine requires empirical validation to confirm that its risk predictions are both accurate and reliable. The core challenge — the inherent class imbalance in fraud detection datasets — means that a model evaluated only for overall Accuracy may achieve 95% Accuracy while completely failing at its primary mission of catching fraudsters. The Prototyping Model's built-in feedback and refinement loop provides the structured methodology to iteratively tune the model until it meets its defined security objectives.

### 3.4 System Analysis

#### 3.4.1 Analysis of the Existing System

The current NIMC identity verification system operates in what can be characterized as a 'Fragmented and Static' mode. When a citizen's NIN is linked to a SIM card, the system performs a single binary check but does not subsequently monitor how that linked identity is used across other platforms, nor does it correlate usage patterns across different sectors.

The key weaknesses identified for NINCore to address are:

- **Identity Silos:** Data remains isolated within individual agency servers with no cross-referencing capability.
- **No Behavioral Tracking:** A fraudster can potentially use one NIN to open multiple accounts across different state branches in a single day without triggering any automated alert.
- **Manual and Reactive Governance:** Identity misuse is typically only detected and investigated after the crime has been committed and reported.

#### 3.4.2 Analysis of the Proposed NINCore System

NINCore is architecturally conceptualized as an intelligent orchestration layer. Unlike the existing NIMS, which operates as a passive biometric repository, the NINCore system treats identity as a dynamic, continuously evolving variable. The 'NIN-Centric' approach means the NIN is the root node of a tree structure, where branches represent active sectoral identities (BVN, NHIS ID, JAMB Number, FRSC License, Voter ID).

The 'Improved' contribution lies in the Probabilistic Risk Engine, which evaluates every incoming identity access request against two data dimensions simultaneously: the citizen's historical behavioral baseline and the contextual features of the current specific access attempt. This dual-dimension evaluation produces an Identity Confidence Score that a static system is structurally incapable of generating.

### 3.5 Technical Specifications

#### 3.5.1 Dataset Description

Since real NIMC citizen data is legally restricted under the NDPR, this project utilizes a High-Fidelity Synthetic NIN-Centric Dataset. The dataset is algorithmically generated using Python libraries — specifically the Faker library for demographic attribute generation and NumPy for statistical distribution modeling — to faithfully mimic Nigerian demographic and sectoral interaction patterns.

Key specifications of the synthetic dataset:

- **Data Source:** Algorithmically generated using Python (Faker, NumPy, Scikit-Learn)
- **Dataset Size:** 50,000 records
- **Class Distribution (Pre-SMOTE):** ~95% Legitimate (0) and ~5% Suspicious (1)
- **Class Distribution (Post-SMOTE):** Balanced to a 75%/25% Legitimate/Suspicious split

**Table 2: Synthetic Dataset Feature Engineering Specification**

| Feature Name | Data Type | Description and Risk Relevance | Feature Category |
|---|---|---|---|
| NIN | BIGINT (11) | Primary Key: The unique National Identification Number | Identifier |
| Age | INT | Citizen age (18–80). Correlated with sectoral usage patterns | Demographic |
| State_of_Origin | VARCHAR (50) | One of Nigeria's 36 states; used for geographic velocity baseline | Demographic |
| Gender | CHAR (1) | M/F; used for demographic coherence validation | Demographic |
| NIN_Linkage_Count | INT | Number of active sector links (1–5). High count increases exposure surface | Behavioral |
| Login_Frequency | INT | Number of NIN-verified identity events per 24-hour period | Behavioral |
| Geographic_Velocity | FLOAT | Distance (km) between consecutive sector access events divided by time elapsed. Detects 'Impossible Travel' | Behavioral (Key) |
| Device_Reputation_Score | FLOAT (0-1) | Score representing the trustworthiness of the accessing device | Behavioral |
| Sector_Conflict_Flag | BINARY | 1 if NIN is simultaneously active in two geographically incompatible sectors | Behavioral (Key) |
| Failed_Auth_Attempts | INT | Number of failed authentication attempts in the last 24 hours | Behavioral |
| Access_Hour | INT (0–23) | Hour of the day access was requested. Unusual hours elevate risk score | Behavioral |
| BVN_Status | BINARY | 1=Linked & Active BVN, 0=Not Linked | Sectoral |
| NHIA_Status | BINARY | 1=Active NHIA record, 0=Not Registered | Sectoral |
| JAMB_Status | BINARY | 1=Valid JAMB number on record, 0=Not Registered | Sectoral |
| FRSC_Status | BINARY | 1=Active FRSC License, 0=Not Licensed | Sectoral |
| Voter_ID_Status | BINARY | 1=Active Voter Registration, 0=Not Registered | Sectoral |
| Age_Consistency_Score | FLOAT (0-1) | Cross-validates age in NIN record against age implied by Sector ID dates | Cross-Validation |
| Name_Mismatch_Flag | BINARY | 1 if name on NIN record does not match name on any linked sector record | Cross-Validation (Key) |
| Sector_Access_Frequency | INT | Total number of times any sector has queried this NIN in the past 30 days | Behavioral |
| Anomaly_Flag (Target) | BINARY | 0=Legitimate, 1=Suspicious. The class label used for model training | Target Variable |

#### 3.5.2 Evaluation Metrics Specification

To objectively evaluate the performance of the NINCore Risk Engine, the following metrics will be utilized:

**Confusion Matrix:** Tabulates the four possible outcomes of binary classification: True Positives (TP), True Negatives (TN), False Positives (FP), and False Negatives (FN).

**Accuracy:** The ratio of all correctly classified instances to the total number of instances.

> **Accuracy = (TP + TN) / (TP + TN + FP + FN)**

**Precision:** The proportion of all events flagged as 'Suspicious' that were genuinely fraudulent.

> **Precision = TP / (TP + FP)**

**Recall (Sensitivity):** The proportion of all actual fraudulent identity events that the engine successfully detected. Recall is the **PRIMARY** performance metric for NINCore. The target minimum Recall for the NINCore prototype is **85%**.

> **Recall = TP / (TP + FN)**

**F1-Score:** The harmonic mean of Precision and Recall, providing a single balanced metric.

> **F1-Score = 2 × (Precision × Recall) / (Precision + Recall)**

**ROC-AUC Score:** Measures the engine's aggregate ability to discriminate between Suspicious and Legitimate identities across all possible decision thresholds. The benchmark from comparable literature is 0.97 (ResearchGate, 2025).

### 3.6 Database Design

#### 3.6.1 Entity Relationship Diagram (ERD)

The database design for NINCore follows a Relational Schema that enforces a 'Single Version of Truth' principle: the NIN, stored in the central Citizen_Registry table, serves as the authoritative anchor for all identity-related data. The ERD consists of four primary entities:

**Citizen_Registry (NINCore_Core):** The master table containing core biographic identity data.
- NIN (BIGINT 11, PK), Full_Name (VARCHAR 100, NOT NULL), DOB (DATE, NOT NULL), Gender (CHAR 1, NOT NULL), State_of_Origin (VARCHAR 50), Biometric_Hash (VARCHAR 255, NOT NULL)

**Sector_Mapping (Linkage_Bridge):** A junction table mapping each NIN to its linked identifiers across five sectors.
- Link_ID (INT, PK, AUTO_INCREMENT), NIN (BIGINT 11, FK), Sector_Name (VARCHAR 50, NOT NULL), Sector_ID (VARCHAR 50, NOT NULL), Linkage_Date (DATE), Linkage_Status (VARCHAR 20)

**Risk_Telemetry (Behavioral_Log):** The behavioral data store feeding the ML model.
- Log_ID (INT, PK, AUTO_INCREMENT), NIN (BIGINT 11, FK), Sector_Requesting (VARCHAR 50), Timestamp (DATETIME), Location_State (VARCHAR 50), Geographic_Velocity (FLOAT), Login_Frequency_24h (INT), Device_ID_Hash (VARCHAR 255), Access_Hour (INT), Risk_Score (FLOAT), ML_Prediction (VARCHAR 10)

**System_Audit (Governance_Trail):** The tamper-evident audit log recording every administrative and agency access event.
- Audit_ID (INT, PK, AUTO_INCREMENT), NIN (BIGINT 11, FK), Agency_ID (VARCHAR 50), Admin_UserID (VARCHAR 50), Action_Taken (VARCHAR 100), Justification (TEXT), Timestamp (DATETIME)

*Figure 3: NINCore Entity Relational Diagram*

### 3.7 System Design (UML Models)

#### 3.7.1 Use Case Diagram

The Use Case Diagram identifies three primary actor types and their respective interactions:

**The Sector User (e.g., Bank Agent or Immigration Officer):**
- Submit NIN Verification Request
- Receive Risk Score Response
- View Sector-Specific Audit History

**The NINCore System (Automated ML Engine):**
- Validate API Key and Sector ID
- Retrieve Citizen Profile from Citizen_Registry
- Fetch Behavioral History from Risk_Telemetry
- Execute Feature Extraction
- Generate ML Risk Score via Random Forest
- Apply Decision Logic (High Risk: Flag and Alert; Low Risk: Clear and Log)
- Update Risk_Telemetry Log
- Update Governance Dashboard

**The System Administrator / Auditor:**
- View National Risk Heatmap
- Investigate Flagged High-Risk NIN Profiles
- Download Full Audit Reports for Regulatory Compliance
- Manage Sector Agency API Key Provisioning
- Monitor Real-Time Model Performance Metrics

*Figure 4: NINCore Use Case Diagram*

#### 3.7.2 Activity Diagram (Single Verification Workflow)

The Activity Diagram illustrates the step-by-step workflow of a single, complete identity governance check:

1. **Input and Trigger:** A Sector User enters a citizen's NIN and transaction details, which formats and submits a POST request to the NINCore API endpoint `POST /api/v1/verify-risk`.
2. **API Gateway Authentication:** The system validates the requesting institution's SectorID and API_Key. If authentication fails, the system returns an 'Unauthorized' HTTP 401 error.
3. **Data Retrieval and Profile Assembly:** The engine queries the Citizen_Registry and Risk_Telemetry tables to assemble a complete behavioral profile.
4. **Feature Extraction:** The system computes real-time risk features including Geographic_Velocity, Login_Frequency_24h, and the Sector_Conflict_Flag.
5. **ML Inference:** The assembled 20-feature vector is passed to the pre-trained Random Forest Classifier for real-time inference.
6. **Classification and Decision Logic:** If the Risk Score > 0.7 (High Risk threshold), the transaction is flagged and an alert is pushed to the Governance Dashboard. If ≤ 0.7, the transaction is classified as 'Low_Risk' and cleared.
7. **Logging and Dashboard Update:** All event data is written to both the Risk_Telemetry log and the System_Audit trail regardless of the decision.

*Figure 5: NINCore Activity Diagram*

### 3.8 System Flowchart

The System Flowchart illustrates the complete logical sequence of operations within the NINCore engine. The flowchart begins with an incoming API request, followed by API Key validation (invalid requests are immediately terminated with 'Access Denied'). Valid requests proceed to citizen profile retrieval, feature vector assembly, ML inference, and risk threshold evaluation. Scores above 0.7 route to the 'Flag and Alert' branch; scores at or below 0.7 route to 'Auto-Approve and Clear.' Both branches converge at the 'Update Audit Log' node, after which the Governance Dashboard is updated.

*Figure 6: NINCore System Flowchart*

### 3.9 Summary of the Chapter

Chapter Three provided the comprehensive architectural blueprint for the NINCore system. It commenced with a critical analysis of the fragmented, static nature of the existing Nigerian identity management model. The chapter then formally introduced the NINCore improved model and its core theoretical justification — the shift from reactive, deterministic identity validation to proactive, probabilistic, ML-driven identity governance.

The methodology chapter adopted the Prototyping Model, justified by the iterative nature of machine learning model development. The technical specifications detailed the design of a 20-feature, 50,000-record synthetic dataset calibrated to Nigerian demographic patterns, and formally defined the evaluation metrics, with Recall as the primary success criterion. The chapter concluded with the complete software engineering design specifications: the NIN-centric relational database schema, the UML diagrams, the NINCore API endpoint specification, and the system flowchart.

---

## REFERENCES

Alemu, S. (2025). AI may identify suspicious transactions through behavioral patterns. *Magna Scientia Advanced Research and Reviews, 13*(02), 218–229.

Bhatta, U. (2025). *Machine learning (ML) to evaluate governance, risk, and compliance (GRC) risks associated with large language models (LLMs)*. ITM Central Washington University.

Digital Identity Verification. (2026). Digital identity verification using machine learning to reduce fraud in micro-lending and enhance credit risk assessment. ResearchGate.

Eyikorogha, Q., & Chigozie, J. N. (2025). National identity management and security: An assessment of NIMS's performance in Nigeria. *International Journal of Public Administration and Digital Society*.

Loughborough University. (2024). *Paradox of intention and outcome in digital identity management: A user-centric analysis of Nigeria's national identification number system*.

Monye, S. N., & Koker, L. (2022). Financial inclusion, the National Identity Management Commission (NIMC), and the regulatory framework for digital identification in Nigeria. *Law and Development Review, 15*(2), 291–327.

National Identity Management Commission. (2025). NIMC launches NIN authentication service (NINAuth) for secure and seamless identity authentication and verification.

National Security Adviser. (2024). National identity management and national security in Nigeria in the era of artificial intelligence: The imperative of AI-driven joint national identity database. *Cyber Secure Nigeria Conference*.

Omada. (2026). *The state of identity governance report 2026: AI, NHIs, and the identity security blind spots*.

Onanuga, B. (2025). Credible, inclusive national identity management system fundamental to national development goals - President Tinubu. State House Nigeria.

Philips, A. (2026). Artificial intelligence–enabled identity governance for risk-based access control systems. ResearchGate.

ResearchGate. (2025). AI-powered risk assessment models for enhancing data governance compliance.

Rodriguez, R., et al. (2025). Digital identity trends and advanced synthetic identity ways. *Sarc. Jr. Eng. Com. Sci., 4*(8), 680–685.
