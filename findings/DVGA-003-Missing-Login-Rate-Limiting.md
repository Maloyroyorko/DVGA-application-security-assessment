**# DVGA-003 — Missing Login Rate Limiting**

**## Severity**

High

CVSS v3.1

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
Overall CVSS Score:     	7.5

**## CWE**

CWE-307 - Improper Restriction of Excessive Authentication Attempts

**## OWASP Mapping**

* OWASP Top 10 2021: A07 - Identification and Authentication Failures

* OWASP API Security Top 10 2023: API2 - Broken Authentication

**## Affected Endpoints**

* `POST /graphql`

**## Affected Functionality**

* GraphQL `login` mutation

* Password authentication

* Automated authentication attempts

**## Description**

During login mutation operation testing (password protection security), we tested whether the application blocks repeated failed authentication attempts or implements any effective rate limiting.

The following login mutation was identified:

```graphql
mutation login {
    login(password: String, username: String) {
        accessToken
        refreshToken
    }
}
```

For the current task:

| User   | Email | Password                                  | Role | ID |
| ------ | ----- | ----------------------------------------- | ---- | -- |
| User A | king  | [king@gmail.com](mailto:king@gmail.com)   | User | 3  |
| User B | king1 | [king1@gmail.com](mailto:king1@gmail.com) | User | 4  |
| User C | king2 | [king2@gmail.com](mailto:king2@gmail.com) | User | 5  |

Now we will brute-force and see that we get blocked or not!

User `king` is our target for now.

The following password list was used:

```text
https://raw.githubusercontent.com/danielmiessler/SecLists/refs/heads/master/Passwords/Common-Credentials/10k-most-common.txt
```

Setting Intruder to attack!

The password parameter was configured as the attack position and the password list was used to perform automated login attempts.

Well, if we don't get blocked even after 300-400 / 1000+ wrong attempts, the password protection is weak and no rate limiting is implemented.

During the attack, we did not get blocked after hundreds of incorrect authentication attempts.

Well, see the `6221` no request and the error message it gave us:

```http
HTTP/2 200 OK
Content-Type: application/json
Date: Mon, 31 Aug 2026 09:16:59 GMT
Ngrok-Agent-Ips: X
Content-Length: 124

{"errors":[{"message":"Authentication Failure","locations":[{"line":2,"column":5}],"path":["login"]}],"data":{"login":null}}
```

There was no trace of blocking. The application continued processing the authentication attempts and returned the same `Authentication Failure` response.

Let's perform a negative search for `Authentication Failure` and see we get any password or not!

During **attempt 471**, we got `king` as the correct password without getting blocked.

The correct password resulted in successful authentication and the application returned both an `accessToken` and a `refreshToken`.

**## Steps to Reproduce**

**### 1. Identify the Login Mutation**

1. Identify the GraphQL `login` mutation.

2. The mutation accepts `username` and `password` and returns `accessToken` and `refreshToken`.

```graphql
mutation login {
    login(password: String, username: String) {
        accessToken
        refreshToken
    }
}
```

**### 2. Select the Target User**

1. Use the `king` user as the target account.

2. The target username is:

```text
king
```

**### 3. Configure the Password Wordlist**

The following SecLists password wordlist was used:

```text
https://raw.githubusercontent.com/danielmiessler/SecLists/refs/heads/master/Passwords/Common-Credentials/10k-most-common.txt
```

**### 4. Configure Burp Suite Intruder**

1. Send the login request to Burp Suite Intruder.

2. Set the password parameter as the attack position.

3. Load the password wordlist.

4. Start the Intruder attack.

**### 5. Observe the Authentication Responses**

The application continued responding to incorrect password attempts with:

```http
HTTP/2 200 OK
Content-Type: application/json

{"errors":[{"message":"Authentication Failure","locations":[{"line":2,"column":5}],"path":["login"]}],"data":{"login":null}}
```

There was no trace of blocking or account lockout.

**### 6. Identify the Correct Password**

After continuing the attack, a negative search for `Authentication Failure` was performed.

During **attempt 471**, we got:

```text
king
```

as the correct password without getting blocked.

The application accepted the correct credentials and returned authentication tokens.

**## Proof of Concept**

**### Burp Suite Intruder Testing**

The Burp Suite Intruder attack demonstrated that repeated authentication attempts could be performed against the `king` user without effective rate limiting or blocking.

The attack continued through hundreds of password attempts.

During attempt **471**, the correct password `king` was identified without the account being blocked.

**### Successful Authentication Response**

After the correct password was identified, the application returned a successful GraphQL response:

```http
HTTP/2 200 OK
Content-Type: application/json
Date: Mon, 31 Aug 2026 09:26:59 GMT
Ngrok-Agent-Ips: X
Content-Length: 568

{"data":{"login":{"accessToken":"[REDACTED]","refreshToken":"[REDACTED]"}}}
```

The response confirms that the identified password resulted in successful authentication and that the application issued both an `accessToken` and a `refreshToken`.

The original response containing the tokens is preserved in the evidence directory.

**### Authentication Failure Response**

The application returned an HTTP `200 OK` response containing the GraphQL authentication failure:

```http
HTTP/2 200 OK
Content-Type: application/json
Date: Mon, 31 Aug 2026 09:16:59 GMT
Ngrok-Agent-Ips: X
Content-Length: 124

{"errors":[{"message":"Authentication Failure","locations":[{"line":2,"column":5}],"path":["login"]}],"data":{"login":null}}
```

The response itself is not the vulnerability. The security issue is that the application continued accepting automated authentication attempts without effective rate limiting or blocking.

**### Screenshot Evidence**

The evidence for this finding was captured during the Burp Suite Intruder testing.

The screenshots demonstrate:

* The login mutation being tested.

* Burp Suite Intruder configured for automated password attempts.

* The repeated `Authentication Failure` responses.

* The absence of effective blocking after hundreds of attempts.

* The successful identification of the correct password at attempt **471**.

* The successful authentication response containing the `accessToken` and `refreshToken`.

All evidence for this finding is stored in:

```text
evidence/DVGA-003-Missing-Login-Rate-Limiting/
```

**### Evidence Contents**

The evidence folder contains the **request, response, and screenshots** captured from intruder during the testing process, including the successful authentication response with all the 10000 attempt data.

**## Impact**

An attacker can automate password-guessing attacks against valid users without being effectively blocked.

If a user's password is weak or exists in a commonly used password list, an attacker may be able to recover the user's credentials.

In this testing, the correct password `king` was identified during attempt **471** without the application blocking the authentication attempts.

The successful authentication response confirmed that the recovered credentials could be used to authenticate successfully and obtain both an `accessToken` and a `refreshToken`.

An attacker who obtains valid authentication tokens may then gain unauthorized access to the functionality available to the compromised user account.

**## Risk Rating**

High

**## Remediation**

* Implement effective server-side rate limiting on the GraphQL `login` mutation.

* Limit the number of failed authentication attempts within a defined time period.

* Implement progressive delays after repeated failed login attempts.

* Consider temporary account lockout or additional verification after excessive failed attempts.

* Implement IP-based and account-based throttling where appropriate.

* Detect and block automated password-guessing activity.

* Monitor repeated authentication failures and generate appropriate security alerts.

* Ensure that rate-limiting controls are enforced server-side and cannot be bypassed by modifying client-side parameters.

**## References**

* CWE-307 - Improper Restriction of Excessive Authentication Attempts

* https://cwe.mitre.org/data/definitions/307.html

* OWASP Top 10 2021: A07 - Identification and Authentication Failures

* https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/

* OWASP API Security Top 10 2023: API2 - Broken Authentication

* https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/

**## Retest Status**

Not Yet Retested

Retesting should confirm that:

1. Repeated failed authentication attempts against the `login` mutation are properly rate-limited.

2. The application blocks or throttles excessive authentication attempts.

3. Account lockout or another appropriate protection mechanism is triggered after excessive failed attempts.

4. Automated password-guessing attempts cannot continue indefinitely.

5. Rate-limiting controls are enforced server-side and cannot be bypassed through request manipulation.
