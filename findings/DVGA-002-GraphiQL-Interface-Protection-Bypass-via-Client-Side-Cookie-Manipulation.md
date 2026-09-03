# DVGA-002 — GraphiQL Interface Protection Bypass via Client-Side Cookie Manipulation

## Severity

**Medium**

**CVSS v3.1**

Score: **5.3 (Medium)**

Vector: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N`

## Overall CVSS Calculation

Vector: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N`

CVSS Base Score:          5.3
Impact Subscore:          1.4
Exploitability Subscore:  3.9
CVSS Temporal Score:      NA
CVSS Environmental Score: NA
Modified Impact Subscore: NA
Overall CVSS Score:     **5.3**

## CWE

**CWE-602 - Client-Side Enforcement of Server-Side Security**

## OWASP Mapping

* OWASP Top 10 2021: **A05 - Security Misconfiguration**
* OWASP API Security Top 10 2023: **API8 - Security Misconfiguration**

## Affected Endpoints

* `GET /graphiql`
* `POST /graphql`

## Affected Functionality

* GraphiQL interface protection controlled by the `graphiql:disable` cookie
* GraphQL introspection through `/graphiql`

## Description

During Day-1 testing, the `/graphiql` interface was initially not accessible.

During testing, I identified a `graphiql:disable` cookie associated with the GraphiQL interface. The cookie value was modified to test whether the interface restriction could be bypassed.

After modifying the cookie, the GraphiQL interface became accessible.

I then tested whether GraphQL introspection was available through the newly accessible interface. The introspection request was successfully processed and returned the application's GraphQL schema.

This confirmed that the intended restriction on the GraphiQL interface could be bypassed by modifying a value controlled by the client.

The main security issue is that access to the GraphiQL interface was being controlled through a client-side cookie. Since the cookie can be modified directly by the user, it cannot reliably enforce a security-sensitive restriction on its own.

The successful introspection returned information about the application's GraphQL schema, including available queries, mutations, subscriptions, types, fields, and arguments.

## Steps to Reproduce

### 1. Access the GraphiQL Interface

1. Browse to:

```text
/graphiql
```

2. Initially, the GraphiQL interface was not accessible.

3. During testing, the following cookie was identified:

```text
graphiql:disable
```

### 2. Modify the Client-Side Cookie

1. Open the browser developer tools and locate the `graphiql:disable` cookie.

2. Modify the cookie value to enable the GraphiQL interface.

3. Access `/graphiql` again.

4. The GraphiQL interface becomes accessible.

This demonstrates that the intended interface restriction can be bypassed by modifying a value controlled by the client.

### 3. Manual GraphQL Introspection

After enabling the GraphiQL interface, I tested whether GraphQL introspection was available through the interface.

The following introspection query was used:

```graphql
query IntrospectionQuery {

    __schema {

        queryType {

            name

        }

        mutationType {

            name

        }

        subscriptionType {

            name

        }

        types {

            ...FullType

        }

        directives {

            name

            description

            args {

                ...InputValue

            }

            onOperation

            onFragment

            onField

        }

    }

}

fragment FullType on __Type {

    kind

    name

    description

    fields(includeDeprecated: true) {

        name

        description

        args {

            ...InputValue

        }

        type {

            ...TypeRef

        }

        isDeprecated

        deprecationReason

    }

    inputFields {

        ...InputValue

    }

    interfaces {

        ...TypeRef

    }

    enumValues(includeDeprecated: true) {

        name

        description

        isDeprecated

        deprecationReason

    }

    possibleTypes {

        ...TypeRef

    }

}

fragment InputValue on __InputValue {

    name

    description

    type {

        ...TypeRef

    }

    defaultValue

}

fragment TypeRef on __Type {

    kind

    name

    ofType {

        kind

        name

        ofType {

            kind

            name

            ofType {

                kind

                name

                ofType {

                    kind

                    name

                }

            }

        }

    }

}
```

### 4. Schema Dump

The introspection request successfully returned the GraphQL schema.

The schema identified the following root types:

```text
Query
Mutations
Subscription
```

### GraphQL Operations Summary

**Queries:**

* `audits`
* `deleteAllPastes`
* `me`
* `paste`
* `pastes`
* `readAndBurn`
* `search`
* `systemDebug`
* `systemDiagnostics`
* `systemHealth`
* `systemUpdate`
* `users`

**Mutations:**

* `createPaste`
* `createUser`
* `deletePaste`
* `editPaste`
* `importPaste`
* `login`
* `uploadPaste`

**Subscriptions:**

* `paste`

The schema also exposed object types including:

* `PasteObject`
* `OwnerObject`
* `UserObject`
* `AuditObject`

along with their associated fields and arguments.

The schema further exposed fields such as:

* `PasteObject.id`
* `PasteObject.title`
* `PasteObject.content`
* `PasteObject.public`
* `PasteObject.userAgent`
* `PasteObject.ipAddr`
* `PasteObject.ownerId`
* `PasteObject.owner`

The `UserObject` type also exposed:

* `id`
* `username`
* `password`

The schema contained additional system-related operations such as:

* `systemUpdate`
* `systemDiagnostics`
* `systemDebug`
* `systemHealth`

These operations provided useful information for subsequent security testing.

## Proof of Concept

### Screenshot Evidence

The evidence for this finding was captured through browser screenshots during testing.

The screenshots demonstrate:

* The initial state where `/graphiql` was not accessible.
* The `graphiql:disable` cookie identified during testing.
* Modification of the client-side cookie.
* The GraphiQL interface becoming accessible after modifying the cookie.
* The manual GraphQL introspection query executed through the enabled GraphiQL interface.
* The successful introspection result containing the GraphQL schema.

All evidence for this finding is stored in:

```text
evidence/DVGA-002-GraphiQL-Interface-Protection-Bypass-via-Client-Side-Cookie-Manipulation/
```

### Evidence Contents

The evidence folder contains the browser screenshots captured during testing, including the cookie modification, GraphiQL interface access, manual introspection query, and resulting schema information.

## Impact

An attacker who can modify their own client-side cookie can enable the GraphiQL interface that was initially disabled.

Once enabled, the interface provides a convenient way to interact with the GraphQL endpoint and, during testing, allowed successful schema introspection.

The returned schema provides information about:

* Available GraphQL queries.
* Available mutations.
* Available subscriptions.
* Object types.
* Fields.
* Arguments.
* Functionality exposed by the application.

The schema identified operations such as `systemDiagnostics`, `systemDebug`, `systemUpdate`, `users`, `audits`, and `deleteAllPastes`, which can provide useful information for further security testing.

The ability to access GraphiQL and perform introspection does **not by itself demonstrate unauthorized access to these operations**. No such authorization impact is claimed as part of this finding.

The demonstrated impact is therefore primarily the bypass of the intended GraphiQL interface restriction and the resulting exposure of the application's GraphQL schema through the interface.

## Risk Rating

**Medium**

## Remediation

* Do not rely on client-side cookies to enforce access restrictions for security-sensitive functionality.
* Enforce GraphiQL access restrictions through server-side controls.
* If GraphiQL is not required in the production environment, disable it completely.
* If GraphiQL is required, protect it using appropriate server-side authentication and authorization controls.
* Consider restricting GraphQL introspection in production if it is not required.
* Ensure that changing or removing a client-side cookie cannot enable functionality that is intended to be restricted.

## References

* CWE-602 - Client-Side Enforcement of Server-Side Security
* https://cwe.mitre.org/data/definitions/602.html
* OWASP Top 10 2021: A05 - Security Misconfiguration
* https://owasp.org/Top10/A05_2021-Security_Misconfiguration/
* OWASP API Security Top 10 2023: API8 - Security Misconfiguration
* https://owasp.org/API-Security/editions/2023/en/0xa8-security-misconfiguration/

