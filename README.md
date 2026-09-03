# DVGA-application-security-assessment
6-day black-box web application and API security assessment of DVGA, following OWASP WSTG and OWASP API Security Top 10 methodologies. Identified and validated 13 security findings across authentication, authorization, GraphQL/API security, and injection attack surfaces, supported by evidence and professional VAPT reporting.

# DVGA VAPT DAST Project Completed By Maloy Roy Orko

From GraphQL reconnaissance to confirmed exploitation.

This project documents a six-day black-box VAPT of DVGA, where the application was systematically tested beyond its intended functionality to identify weaknesses across its GraphQL interface, authentication and authorization controls, input handling, and server-side processing. The assessment resulted in 13 confirmed vulnerabilities, each manually validated and documented with reproducible evidence, technical impact, CVSS v3.1 assessment, and remediation recommendations.

# DVGA Vulnerability Assessment & Penetration Testing (VAPT)

## Overview

This project documents a **6-day black-box Vulnerability Assessment and Penetration Testing (VAPT)** conducted against the deliberately vulnerable **DVGA (Damn Vulnerable GraphQL Application)**.

**Assessment Period:** **29 August 2026 – 3 September 2026**

The assessment focused on identifying and validating real-world **web application, GraphQL, and API security vulnerabilities** using industry-standard methodologies aligned with:

* **OWASP Web Security Testing Guide (WSTG)**
* **OWASP API Security Top 10**

A total of **13 confirmed security vulnerabilities** were identified and documented with proof-of-concept evidence, impact analysis, severity classification, **CVSS v3.1 scoring**, and remediation guidance.

---

## Objectives

* Identify security vulnerabilities in a black-box environment
* Assess GraphQL and API security controls
* Evaluate authentication and authorization mechanisms
* Test JWT-based authentication and token security
* Analyze GraphQL schema and introspection security
* Assess GraphiQL interface protection
* Test authentication rate-limiting controls
* Identify input validation and injection vulnerabilities
* Assess server-side request and command execution attack surfaces
* Test GraphQL resource-exhaustion risks
* Demonstrate real-world exploitation techniques safely
* Map findings to relevant OWASP and CWE classifications
* Perform **CVSS v3.1 severity assessment and score calculation** for identified vulnerabilities
* Provide practical remediation recommendations

---

## Scope

### In Scope

* Web Application
* GraphQL API
* GraphQL Schema and Introspection
* Authentication Mechanisms
* Authorization Controls
* GraphiQL Interface
* Paste Creation and Management
* Paste Import Functionality
* Paste Upload Functionality
* System Diagnostics Functionality
* System Debug Functionality
* Input Validation and Injection Handling
* Application-Level Resource Exhaustion / Denial of Service

### Out of Scope

* Infrastructure Testing
* Source Code Review
* Operating System Assessment
* Third-Party Services and External Infrastructure
* Social Engineering
* Physical Security Testing

---

## Methodology

The assessment followed a structured **black-box security testing methodology** based on OWASP testing principles.

### Testing Phases

1. Reconnaissance and Application Mapping
2. GraphQL Endpoint Discovery
3. GraphQL Schema and Introspection Analysis
4. Endpoint and Functionality Enumeration
5. Authentication Testing
6. Authorization and Access Control Testing
7. JWT Security Testing
8. GraphQL Security Testing
9. Parameter Manipulation
10. Injection and Input Validation Testing
11. Stored XSS Testing
12. GraphQL Abuse and Resource-Exhaustion Testing
13. Automated Security Scanning
14. Manual Vulnerability Verification
15. Evidence Collection
16. CVSS v3.1 Severity Assessment
17. Risk Analysis and Vulnerability Classification
18. Professional Security Reporting

Automated tools were used to assist with discovery, reconnaissance, endpoint enumeration, and identification of potential security issues. Identified issues were manually verified before being classified as confirmed vulnerabilities.

Requests, responses, screenshots, reconnaissance artifacts, and relevant tool outputs were collected and organized as supporting evidence.

---

# Vulnerability Matrix

The following matrix provides a consolidated overview of the **13 confirmed vulnerabilities**, including their final severity classifications, CVSS v3.1 scores, and vectors.

| ID           | Vulnerability                                                             | Severity     | CVSS v3.1 Score | Vector                                         |
| ------------ | ------------------------------------------------------------------------- | ------------ | --------------: | ---------------------------------------------- |
| **DVGA-001** | JWT Token-Based Authorization Vulnerability — Signature Validation Bypass | **High**     |         **8.8** | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H` |
| **DVGA-002** | GraphiQL Interface Protection Bypass via Client-Side Cookie Manipulation  | **Medium**   |         **5.3** | `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N` |
| **DVGA-003** | Missing Login Rate Limiting                                               | **High**     |         **7.5** | `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N` |
| **DVGA-004** | SystemDiagnostics Authentication — Missing Rate Limiting                  | **High**     |         **7.5** | `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N` |
| **DVGA-005** | OS Command Injection via systemDiagnostics                                | **High**     |         **7.2** | `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H` |
| **DVGA-006** | SSRF via importPaste                                                      | **High**     |         **7.5** | `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N` |
| **DVGA-007** | OS Command Injection via ImportPaste Path                                 | **Critical** |         **9.8** | `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H` |
| **DVGA-008** | SQL Injection via pastes.filter                                           | **Critical** |         **9.1** | `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N` |
| **DVGA-009** | Stored Cross-Site Scripting (XSS) via CreatePaste                         | **Critical** |         **9.3** | `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N` |
| **DVGA-010** | Stored Cross-Site Scripting (XSS) via ImportPaste                         | **Critical** |         **9.3** | `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N` |
| **DVGA-011** | Stored Cross-Site Scripting (XSS) via UploadPaste                         | **High**     |         **9.3** | `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N` |
| **DVGA-012** | Denial of Service via Multiple Resource-Exhaustion Techniques             | **Critical** |         **7.5** | `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H` |
| **DVGA-013** | OS Command Injection via systemDebug                                      | **Critical** |         **9.8** | `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H` |

---

## Severity Distribution

| Severity     |  Count |
| ------------ | -----: |
| **Critical** |  **6** |
| **High**     |  **6** |
| **Medium**   |  **1** |
| **Low**      |  **0** |
| **Total**    | **13** |

### Overall Risk Metrics

* **Confirmed Vulnerabilities:** 13
* **Critical:** 6
* **High:** 6
* **Medium:** 1
* **Low:** 0
* **Highest CVSS v3.1 Score:** **9.8 — Critical**
* **Average CVSS Score:** **8.2**

---

## CVSS v3.1 Assessment

CVSS v3.1 was used to provide a standardized severity assessment for each confirmed vulnerability.

The assessment considered the following CVSS Base Metrics:

* **Attack Vector (AV)**
* **Attack Complexity (AC)**
* **Privileges Required (PR)**
* **User Interaction (UI)**
* **Scope (S)**
* **Confidentiality (C)**
* **Integrity (I)**
* **Availability (A)**

Each confirmed vulnerability was individually assessed based on its demonstrated attack characteristics, required privileges, user interaction, scope, and security impact.

The individual finding reports contain the corresponding **CVSS v3.1 score, vector, and severity classification**.

---

## Key Vulnerability Categories

The assessment identified vulnerabilities across multiple security domains:

* JWT Authentication and Token Security
* Authentication Weaknesses
* Authorization Vulnerabilities
* GraphQL Security
* GraphiQL Interface Protection
* Missing Rate Limiting
* Server-Side Request Forgery (SSRF)
* OS Command Injection
* SQL Injection
* Stored Cross-Site Scripting (XSS)
* Resource Exhaustion / Denial of Service
* Input Validation Weaknesses

---

## Key Highlights

* JWT signature validation weaknesses enabled unauthorized token manipulation.
* GraphiQL interface protection could be bypassed through client-side cookie manipulation.
* Authentication mechanisms lacked effective rate-limiting protections.
* Multiple OS command injection vulnerabilities were successfully validated.
* SSRF was identified through the `importPaste` functionality.
* SQL injection was identified through the `pastes.filter` functionality.
* Multiple stored XSS vulnerabilities were identified across paste creation, import, and upload functionality.
* Multiple resource-exhaustion techniques demonstrated application-level denial-of-service risk.
* All reported vulnerabilities were manually validated and supported by collected evidence.
* Findings were classified using relevant **OWASP, CWE, and CVSS v3.1** frameworks.

---

# Repository Structure

```text id="repo1"
DVGA-application-security-assessment/
│
├── README.md
│
├── evidence/
│   ├── DVGA-001-...
│   ├── DVGA-002-...
│   ├── DVGA-003-...
│   ├── ...
│   ├── DVGA-013-...
│   └── Reconnaissance & Application Mapping
│
├── findings/
│   ├── DVGA-001-....md
│   ├── DVGA-002-....md
│   ├── DVGA-003-....md
│   ├── ...
│   ├── DVGA-013-....md
│   ├── WAPITI/
│   ├── ZAP/
    └── Reconnaissance & Application Mapping.md
│
├── report/
│   ├── DVGA-VAPT-DAST-Final-Report-By-Maloy-Roy-Orko.md
│   └── DVGA-VAPT-DAST-Final-Report-By-Maloy-Roy-Orko.pdf
│
└── requests-responses-screenshots/
    ├── DVGA-Screenshots/
    ├── DVGA-Requests-Responses/
    └── DAY-1-Recon/
```

---

## File Directory Breakdown

### `evidence/`

Contains dedicated evidence directories for the confirmed vulnerabilities along with reconnaissance and application-mapping documentation.

```text id="evidence1"
evidence/
├── DVGA-001-...
├── DVGA-002-...
├── DVGA-003-...
├── ...
├── DVGA-013-...
└── Reconnaissance & Application Mapping
```

Each `DVGA-XXX` directory contains supporting evidence associated with the corresponding vulnerability.

**`Reconnaissance & Application Mapping.md`** documents the reconnaissance, application mapping, endpoint discovery, functionality enumeration, and initial assessment activities performed during the engagement.

---

### `findings/`

Contains the individual technical vulnerability reports and automated scanning results.

```text id="findings1"
findings/
├── DVGA-001-....md
├── DVGA-002-....md
├── DVGA-003-....md
├── ...
├── DVGA-013-....md
├── WAPITI/
├── ZAP/
└── Reconnaissance & Application Mapping.md
```

The individual vulnerability reports contain relevant information including:

* Vulnerability description
* Severity
* CWE classification
* OWASP mapping
* CVSS v3.1 score and vector
* Affected endpoints / GraphQL operations
* Steps to reproduce
* Proof of concept
* Impact
* Risk assessment
* Remediation
* Supporting evidence

The `WAPITI/` and `ZAP/` directories contain relevant automated scanning results and outputs.

---

### `report/`

Contains the final consolidated VAPT report in Markdown and PDF formats.

```text id="report1"
report/
├── DVGA-VAPT-DAST-Final-Report-By-Maloy-Roy-Orko.md
└── DVGA-VAPT-DAST-Final-Report-By-Maloy-Roy-Orko.pdf
```

* **Markdown Report:** Complete text-based version of the final VAPT assessment.
* **PDF Report:** Professionally formatted final version of the VAPT assessment.

---

### `requests-responses-screenshots/`

Contains centralized testing artifacts, including screenshots, HTTP/GraphQL requests and responses, and Day-1 reconnaissance material.

```text id="artifacts1"
requests-responses-screenshots/
├── DVGA-Screenshots/
├── DVGA-Requests-Responses/
└── DAY-1-Recon/
```

* **`DVGA-Screenshots/`** — Screenshot evidence collected during testing.
* **`DVGA-Requests-Responses/`** — HTTP and GraphQL request/response evidence.
* **`DAY-1-Recon/`** — Reconnaissance artifacts and supporting material from Day 1 of the assessment.

---

## Tools Used

* Burp Suite
* OWASP ZAP
* Wapiti
* ffuf
* Katana
* InQL
* GraphQL Voyager
* graphw00f
* Browser Developer Tools
* JWT Testing Tools
* Manual GraphQL/API Testing

---

## Assessment Approach

The assessment combined **automated security scanning with manual penetration testing**.

Automated tools were used for discovery, reconnaissance, endpoint enumeration, and identification of potential security issues. Manual testing was then performed to validate exploitability and security impact.

Only issues that were sufficiently verified through manual testing and reproducible evidence were included as confirmed vulnerabilities in the final assessment.

The project demonstrates an end-to-end security assessment workflow covering:

**Reconnaissance → Enumeration → Security Testing → Exploitation → Manual Validation → Evidence Collection → CVSS Assessment → Vulnerability Classification → Professional Reporting**

---

## Disclaimer

This project was conducted in a controlled laboratory environment using the deliberately vulnerable DVGA application for **educational and ethical security research purposes only**.

No real-world systems were targeted or harmed during the assessment.

---

## Author

**Maloy Roy Orko**

**Project Type:** Black-Box VAPT — Learning / Portfolio Project

**Focus Area:** GraphQL, API & Web Application Security

---

## Acknowledgements

AI-assisted tools were used for formatting, documentation, organization, and report preparation.

All security testing, vulnerability validation, exploitation, evidence collection, classification, and findings presented in this repository were performed by the author.

Supporting evidence and assessment artifacts are included within the repository.

---

## Note

This project represents a practical security assessment focused on **GraphQL, API, and web application security testing**.

It demonstrates an end-to-end workflow covering reconnaissance, enumeration, security testing, exploitation, manual validation, evidence collection, CVSS-based risk assessment, vulnerability classification, and professional security reporting.
