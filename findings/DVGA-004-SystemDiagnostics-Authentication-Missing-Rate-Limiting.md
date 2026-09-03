# DVGA-004 — SystemDiagnostics Authentication Missing Rate Limiting

## Severity

High

Score: 7.5 (High)

Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N

## Overall CVSS Calculation

Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N
CVSS Base Score:	        7.5
Impact Subscore:	        3.6
Exploitability Subscore:	3.9
CVSS Temporal Score:	    NA
CVSS Environmental Score:	NA
Modified Impact Subscore:	NA
Overall CVSS Score:	        7.5

## CWE

CWE-307 - Improper Restriction of Excessive Authentication Attempts

## OWASP Mapping

* OWASP Top 10 2021: A07 - Identification and Authentication Failures

* OWASP API Security Top 10 2023: API2 - Broken Authentication

## Affected Endpoints

* `POST /graphql`

## Affected Functionality

* GraphQL `systemDiagnostics` query

* `systemDiagnostics` authentication

* Password brute-force protection

## Description

During GraphQL testing, I identified the `systemDiagnostics` query. The query requires a username and password and also accepts a command through the `cmd` parameter.

The query is:

```graphql
query systemDiagnostics {
    systemDiagnostics(username: String, password: String, cmd: String)
}
```

For this test, I wanted to see how the application handles repeated incorrect password attempts and whether it has any protection against password brute-force attacks.

For the current task, the following user data was available:

| User   | Username | Email                                     | Role | ID |
| ------ | -------- | ----------------------------------------- | ---- | -- |
| User A | king     | [king@gmail.com](mailto:king@gmail.com)   | User | 3  |
| User B | king1    | [king1@gmail.com](mailto:king1@gmail.com) | User | 4  |
| User C | king2    | [king2@gmail.com](mailto:king2@gmail.com) | User | 5  |

Initially, `king` was considered as the target user.

I first tried the following query with the `king` username:

```graphql
query systemDiagnostics {
    systemDiagnostics(username: "king", password: "king", cmd: "ls")
}
```

The application returned:

```json
{"data":{"systemDiagnostics":"Username is invalid"}}
```

Well, the username is valid according to the available user data, so this suggested that the `systemDiagnostics` functionality may be intended for an administrative account rather than a normal user.

I then tried `admin` as the username. The password `changeme` had already been identified during previous testing.

First, I used an incorrect password to confirm that the application was actually checking the supplied password:

```graphql
query systemDiagnostics {
    systemDiagnostics(username: "admin", password: "king", cmd: "ls")
}
```

The application returned:

```json
{"data":{"systemDiagnostics":"Password Incorrect"}}
```

This confirmed that `admin` was a valid username for this functionality and that the supplied password was being checked.

I then tried the previously identified administrative password:

```graphql
query systemDiagnostics {
    systemDiagnostics(username: "admin", password: "changeme", cmd: "whoami")
}
```

The response was:

```json
{"data":{"systemDiagnostics":"dvga\n"}}
```

Well, see: it works. This confirmed that the credentials were valid and that successful authentication allowed the supplied command to execute.

Now I wanted to check whether the application would block repeated incorrect password attempts.

If we don't get blocked even after 300-400 / 1000+ wrong attempts, the password protection is weak and no effective rate limiting is implemented.

The password list used for the test was the SecLists `10k-most-common.txt` list:

```text
https://raw.githubusercontent.com/danielmiessler/SecLists/refs/heads/master/Passwords/Common-Credentials/10k-most-common.txt
```

I configured Burp Suite Intruder with the `password` parameter as the attack position and started the password attack against the `admin` account.

The main thing I was looking for was whether the application would start blocking the requests, rate-limiting the attempts, locking the account, or introducing any other protection after a large number of failed attempts.

The application continued accepting the password attempts without any visible blocking or effective rate limiting.

During **attempt 1014**, the password:

```text
changeme
```

was identified as the correct password.

The successful response was:

```http
HTTP/2 200 OK
Content-Type: application/json
Date: Mon, 31 Aug 2026 11:33:49 GMT
Ngrok-Agent-Ips: X
Content-Length: 39

{"data":{"systemDiagnostics":"dvga\n"}}
```

The response shows that the password was accepted and the requested `whoami` command was executed successfully.

This demonstrates that the application allowed a large number of automated authentication attempts against the `systemDiagnostics` functionality without introducing effective brute-force protection.

No account lockout, request throttling, or other effective protection was observed during the test.

## Steps to Reproduce

### 1. Identify the `systemDiagnostics` Query

Identify the GraphQL `systemDiagnostics` query:

```graphql
query systemDiagnostics {
    systemDiagnostics(username: String, password: String, cmd: String)
}
```

The query accepts:

* `username`
* `password`
* `cmd`

### 2. Verify the Username

Initially, I tested the known `king` username:

```graphql
query systemDiagnostics {
    systemDiagnostics(username: "king", password: "king", cmd: "ls")
}
```

The application returned:

```json
{"data":{"systemDiagnostics":"Username is invalid"}}
```

This suggested that the functionality was restricted to a different account.

I then tested `admin` with an incorrect password:

```graphql
query systemDiagnostics {
    systemDiagnostics(username: "admin", password: "king", cmd: "ls")
}
```

The application returned:

```json
{"data":{"systemDiagnostics":"Password Incorrect"}}
```

This confirmed that `admin` was recognized as a valid username.

### 3. Verify Valid Administrative Credentials

I tested the previously identified password `changeme`:

```graphql
query systemDiagnostics {
    systemDiagnostics(username: "admin", password: "changeme", cmd: "whoami")
}
```

The application returned:

```json
{"data":{"systemDiagnostics":"dvga\n"}}
```

This confirmed that the credentials were valid and that command execution was possible after successful authentication.

### 4. Load the Password List

Use the following SecLists password list:

```text
https://raw.githubusercontent.com/danielmiessler/SecLists/refs/heads/master/Passwords/Common-Credentials/10k-most-common.txt
```

### 5. Configure Burp Suite Intruder

1. Send the `systemDiagnostics` request to Burp Suite Intruder.

2. Use `admin` as the username.

3. Set the password parameter as the attack position.

4. Load the SecLists password list.

5. Start the attack.

### 6. Monitor the Authentication Attempts

While the attack was running, I checked whether the application would:

* Block repeated requests.
* Rate-limit the requests.
* Lock the account.
* Introduce increasing delays.
* Return a different response indicating that brute-force protection had been triggered.

The application continued processing the attempts without any visible blocking or effective rate limiting.

### 7. Identify the Correct Password

During **attempt 1014**, the password:

```text
changeme
```

was identified as the correct password.

The successful response was:

```http
HTTP/2 200 OK
Content-Type: application/json
Date: Mon, 31 Aug 2026 11:33:49 GMT
Ngrok-Agent-Ips: X
Content-Length: 39

{"data":{"systemDiagnostics":"dvga\n"}}
```

The response confirms that the credentials were accepted and that the `whoami` command was successfully executed.

## Proof of Concept

### Burp Suite Intruder

Burp Suite Intruder was used to automate password attempts against the `admin` account through the `systemDiagnostics` GraphQL query.

The application continued accepting the requests without visibly blocking the account or applying effective rate limiting.

The attack reached **attempt 1014**, where the correct password `changeme` was identified.

### Successful Authentication and Command Execution

The successful attempt returned:

```http
HTTP/2 200 OK
Content-Type: application/json
Date: Mon, 31 Aug 2026 11:33:49 GMT
Ngrok-Agent-Ips: X
Content-Length: 39

{"data":{"systemDiagnostics":"dvga\n"}}
```

The returned value:

```text
dvga
```

shows that the `whoami` command was executed successfully after authentication.

This confirms that the identified password was valid and that successful authentication provides access to the `systemDiagnostics` functionality.

### Screenshot Evidence

The screenshots captured during testing demonstrate:

* The `systemDiagnostics` GraphQL query being tested.
* The initial username and password validation.
* The successful authentication using the `admin` account.
* Burp Suite Intruder configured for the password attack.
* The large number of password attempts being processed.
* The absence of visible blocking or effective rate limiting.
* The correct password being identified at attempt **1014**.
* The successful response showing command execution.

All evidence for this finding is stored in:

```text
evidence/DVGA-004-SystemDiagnostics-Authentication-Missing-Rate-Limiting/
```

### Evidence Contents

The evidence folder contains the **request, response, and screenshots** saved during the testing process.

## Impact

The lack of effective rate limiting allows an attacker to automate a large number of password attempts against the `systemDiagnostics` authentication mechanism.

In this test, the application processed more than one thousand password attempts without visibly blocking the attack or locking the account. The password `changeme` was identified at **attempt 1014** using a commonly used password list.

The impact is more significant because `systemDiagnostics` is not simply a normal authentication endpoint. Once valid credentials are supplied, the functionality allows commands to be executed through the `cmd` parameter.

Therefore, an attacker who successfully guesses the administrative password may be able to gain access to command-execution functionality exposed through the GraphQL API.

The use of a weak administrative password such as `changeme` further increases the practical risk of this issue.

## Risk Rating

High

## Remediation

* Implement server-side rate limiting for authentication attempts to the `systemDiagnostics` functionality.

* Limit the number of failed authentication attempts within a defined time period.

* Introduce increasing delays after repeated failed authentication attempts.

* Consider temporarily locking or challenging the account after a reasonable number of consecutive failures.

* Use both account-based and IP-based throttling where appropriate.

* Monitor repeated authentication failures and detect automated password-guessing activity.

* Remove default or weak administrative passwords such as `changeme`.

* Require strong and unique credentials for administrative functionality.

* Restrict `systemDiagnostics` to authorized administrative users only.

* Where possible, restrict administrative diagnostic functionality to trusted internal interfaces rather than exposing it directly through the public GraphQL API.

* Ensure that brute-force protection is enforced server-side and cannot be bypassed by modifying GraphQL parameters or request values.

## References

* CWE-307 - Improper Restriction of Excessive Authentication Attempts

* https://cwe.mitre.org/data/definitions/307.html

* OWASP Top 10 2021: A07 - Identification and Authentication Failures

* https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/

* OWASP API Security Top 10 2023: API2 - Broken Authentication

* https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/