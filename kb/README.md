# Support Knowledge Base

Curated Help Center articles used by the Persona Support Agent for keyword-based retrieval (`backend/kb_retriever.py`).

## Articles

| # | Title | Keywords |
|---|-------|----------|
| 1 | [Login Issue](articles/login-issue.md) | login, sign in, password, MFA, session |
| 2 | [API Authentication Error](articles/api-authentication-error.md) | 401, 403, API, token, OAuth, webhook |
| 3 | [Billing Issue](articles/billing-issue.md) | invoice, billing, payment, subscription, refund |
| 4 | [Service Downtime](articles/service-downtime.md) | outage, downtime, status, 500, 503 |
| 5 | [Account Access Issue](articles/account-access-issue.md) | access, permission, role, SSO, SCIM |
| 6 | [Data Sync Issue](articles/data-sync-issue.md) | sync, connector, ETL, latency, duplicate |
| 7 | [Password Reset and Recovery](articles/password-reset-and-recovery.md) | reset password, forgot, recovery |
| 8 | [Mobile App Issues](articles/mobile-app-issues.md) | mobile, iOS, Android, app crash |
| 9 | [Email Notifications](articles/email-notifications.md) | email, notification, alert, SMTP |
| 10 | [Exports and Reporting](articles/exports-and-reporting.md) | export, CSV, report, analytics |
| 11 | [Privacy and Data Requests](articles/privacy-and-data-requests.md) | privacy, GDPR, DSAR, delete my data |
| 12 | [VPN, Firewall and Network Access](articles/vpn-firewall-and-network-access.md) | VPN, firewall, proxy, websocket |
| 13 | [Browser and Compatibility](articles/browser-and-compatibility.md) | browser, Chrome, Safari, cookies |
| 14 | [Changing Plans and Seats](articles/changing-plans-and-seats.md) | upgrade, downgrade, seats, license |
| 15 | [Feature Requests and Roadmap](articles/feature-requests-and-roadmap.md) | feature request, roadmap, enhancement |
| 16 | [Trial and Sandbox](articles/trial-and-sandbox.md) | trial, sandbox, POC, demo |
| 17 | [General Support](articles/general-support.md) | *(fallback — no keywords)* |

## Retrieval behavior

- Articles are matched by **keyword hits** in the user query (case-insensitive substring match).
- Up to **4** top-scoring articles are returned when scores are within 1 of the best match.
- **General Support** is used when no keywords match.

## Source

These files were exported from `backend/kb_articles.py`. Machine-readable metadata lives in `kb/index.json`.
