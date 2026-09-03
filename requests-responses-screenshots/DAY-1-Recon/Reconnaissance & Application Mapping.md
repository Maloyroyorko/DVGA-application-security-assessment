# Day 1 Notes - Reconnaissance & Application Mapping

---

## 1. Setup & Installation:

### DVGA Setup via Docker

DVGA was set up via Docker.

### Tools

Tools used:

* Katana
* Burp Suite

  * Necessary Extensions: InQL, JWT Editor, JSON Web Tokens, JWT Scanner
* ngrok
* Windows Snipping Tool
* graphw00f
* ffuf
* Gobuster
* Firefox Browser

### Test Account

* No Login/Sign-up utility was found at Day-1.

### Port Forwarding

Port forwarding was used to access the DVGA target from different devices, as we wanted to maintain confidentiality before launch. Therefore, the total setup was maintained in the local system rather than using online hosting.

### Evidence Collection

* Requests and responses are being saved as `.txt` files.
* Notes are being taken after understanding the functionality.
* Screenshots of all relevant requests/responses captured by Burp Suite have been taken.
* Web UI screenshots have also been taken.

---

# 2. Functionality Observation:

---

## Authentication

As per Day-1 planning, we didn't find any traces of authentication or login/sign-up functionality.

## Homepage Functionality

Nothing special was observed on the homepage during the initial reconnaissance.

## Private Pastes Functionality

GraphQL API activity has been detected with a query while visiting:

```text
/my_pastes
```

Screenshots of the requests/responses captured by Burp Suite have been taken, and web UI screenshots have also been collected.

A similar GraphQL query is used for both public and private paste grabbing, but an argument value changes the behavior:

```text
public: true
public: false
```

This will require further authorization testing during the next phases.

## Public Pastes Functionality

GraphQL API activity has been detected with a query while visiting:

```text
/public_pastes
```

Screenshots of the requests/responses captured by Burp Suite have been taken, and web UI screenshots have also been collected.

A similar GraphQL query is used for both public and private paste grabbing, but an argument value changes the behavior:

```text
public: true
public: false
```

This will require further testing to understand whether the server-side access control properly enforces the public/private distinction.

## Create Pastes Functionality

GraphQL API activity has been detected with a query while visiting:

```text
/create_paste
```

Screenshots of the requests/responses captured by Burp Suite have been taken, and web UI screenshots have also been collected.

Both public and private pastes can be created with the value change of an argument called:

```text
public: true
public: false
```

XSS and HTML Injection may be possible and will be tested later.

## Import Paste Functionality

Pastes can be imported from external sources via a GraphQL query.

The following variables are used:

```text
host
port
path
```

This may lead to a potential SSRF attack surface, which will be tested later.

## Cookies

Only one cookie attracted my attention:

```text
env=graphiql:disable
```

It looks like it may be related to the GraphQL/GraphiQL interface, but its exact purpose and security impact are not confirmed yet.

## Upload Paste Functionality

Pastes can be uploaded via files, and again this creates another opportunity to test for:

* XSS
* HTML Injection
* File/content validation issues

These are only potential attack surfaces at this stage and are not confirmed vulnerabilities.

## GraphQL Query Log Page

```text
/audit
```

The `/audit` page is the log page where I personally see chances of:

* XSS
* HTML Injection
* Log Injection

These areas will require proper validation during security testing.

## Interesting Endpoints

* `/graphql`
* `/graphiql`
* `/audit`

########## Overall Comment:

**All major functions of this website observed during Day-1 are entirely reliant on the GraphQL API. So, we need to focus on this API majorly during the security assessment.**

---

# 3. Reconnaissance & Enumeration:

---

Let's find endpoints as we saw GraphQL API traces using Gobuster and screenshot collection.

### Gobuster

Command used:

```bash
gobuster dir -u http://localhost:5013 -w /home/pentester/bank/graphql.txt
```

Got 2 endpoints:

```text
graphiql    (Status: 400) [Size: 53]
graphql     (Status: 400) [Size: 53]
```

### API Endpoint and Interface

API endpoint:

```text
/graphql
```

GraphQL API Interface:

```text
/graphiql
```

#### Lets find out overall all files and directories of it using dirb and katana

Katana Command: katana -u http://localhost:5013/ -d 5 -js-crawl -kf all -ef woff,css,png,jpg,jpeg,svg,gif,ico,pdf -silent -o nuclei_targets.txt 

Urls saved in: DAY-1/Tool-Results/katana-urls.txt and DAY-1/Tool-Results/dirb-result.txt 

---

# 4. GraphQL API Detection via graphw00f

GraphQL API detection was performed using graphw00f, along with screenshot collection.

### Commands

```bash
python3 main.py -d -t http://localhost:5013/graphiql
```

```bash
python3 main.py -d -t http://localhost:5013/graphql
```

Yeah, it is surely a GraphQL API.

Relevant tool output and screenshots have been saved as evidence.

---

# 5. GraphQL API Fingerprinting

GraphQL API fingerprinting was performed to identify the GraphQL engine and understand the underlying technology.

### Command

```bash
python3 main.py -t http://localhost:5013/graphiql -f
```

The same fingerprinting was also checked against the GraphQL endpoint where required.

### Result

```text
Engine: Graphene
Technology: Python
```

So, the GraphQL engine was identified as **Graphene**, with **Python** identified as the underlying technology.

### Reference

The following GraphQL Threat Matrix reference was reviewed:

https://github.com/nicholasaleks/graphql-threat-matrix/blob/master/implementations/graphene.md

It says:

```text
Graphene Features Configuration Reference
==========================================

Feature                     | Status
----------------------------|---------------------
Field Suggestions           | Enabled by Default (✅)
Query Depth Limit           | No Support (❌)
Query Cost Analysis        | No Support (❌)
Automatic Persisted Queries | No Support (❌)
Introspection               | Enabled by Default (✅)
Debug Mode                  | No Support (❌)
Batch Requests              | Disabled by Default (⚠️)
```

> **Note:** These are general Graphene characteristics from the reference and do not automatically confirm that every listed behavior is configured the same way in the DVGA deployment. The actual behavior will be verified during security testing.

---

# 6. Day-1 Completion Assessment

| Area                      | Status |
| ------------------------- | ------ |
| Environment setup         | ✅      |
| Proxy/Burp setup          | ✅      |
| Functional mapping        | ✅      |
| GraphQL discovery         | ✅      |
| Endpoint enumeration      | ✅      |
| Technology fingerprinting | ✅      |
| Request/response evidence | ✅      |
| Screenshot evidence       | ✅      |
| Attack-surface hypotheses | ✅      |

---

# Day-1 Status

**COMPLETED ✅**

Day-1 reconnaissance and application mapping have been completed.

The main functionality, GraphQL endpoints, GraphQL implementation, technology stack, baseline requests/responses, screenshots, and initial security-relevant attack surfaces have been documented.

Potential XSS, HTML Injection, SSRF, Log Injection, and authorization-related areas identified during Day-1 are **not being treated as confirmed vulnerabilities yet**. They will be properly tested and validated during the upcoming assessment phases.

---

# Note

We have a lot of time, so we will start **Day-2 tasks** as well to ensure our project completion before the deadline.

Day-1 reconnaissance evidence will remain as the baseline, while any security testing performed from this point will be documented under the Day-2 assessment records.

---
