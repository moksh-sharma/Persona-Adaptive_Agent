"""
Full in-memory support knowledge base.

Articles are keyword-matched at retrieval time (`kb_retriever`). General Support is last (fallback).
"""

from __future__ import annotations

from typing import TypedDict


class KBEntry(TypedDict):
    title: str
    content: str
    keywords: tuple[str, ...]


# Curated KB (General Support is last)
KNOWLEDGE_BASE: tuple[KBEntry, ...] = (
    {
        "title": "Login Issue",
        "content": (
            "If login fails: confirm email and password, reset password via the Forgot Password link, "
            "clear browser cache/cookies for our domain, disable VPN or ad-blockers temporarily, "
            "and verify your account has not been locked after repeated failures. "
            "If SSO is enabled, validate IdP SAML/OIDC settings with your administrator."
        ),
        "keywords": (
            "login",
            "sign in",
            "signin",
            "password",
            "credential",
            "locked",
            "forgot password",
            "cannot access",
            "session",
            "logout",
            "mfa",
            "2fa",
        ),
    },
    {
        "title": "API Authentication Error",
        "content": (
            "For API authentication errors (e.g., 401/403): verify API keys/scopes have not rotated, "
            "check expiry and clock skew, confirm you send the Authorization header/OAuth bearer token correctly, "
            "validate environment (sandbox vs prod), inspect recent permission changes and audit logs."
        ),
        "keywords": (
            "401",
            "403",
            "api",
            "token",
            "oauth",
            "bearer",
            "authentication",
            "authorization",
            "key",
            "webhook",
            "integration",
            "endpoint",
            "rate limit",
        ),
    },
    {
        "title": "Billing Issue",
        "content": (
            "For billing discrepancies: review invoices in Billing History, verify payment method "
            "and tax region, reconcile seat counts vs active users. Open a billing ticket if charges "
            "look incorrect - we can escalate to Finance with transaction IDs."
        ),
        "keywords": (
            "invoice",
            "bill",
            "billing",
            "payment",
            "charge",
            "subscription",
            "plan",
            "refund",
            "credit card",
        ),
    },
    {
        "title": "Service Downtime",
        "content": (
            "During suspected downtime: check the public status page, subscribe to notifications, "
            "collect timestamps and impacted regions/workflows. Retry with exponential backoff. "
            "If SLA applies, preserve evidence (error codes, dashboards) for post-incident review."
        ),
        "keywords": (
            "down",
            "outage",
            "downtime",
            "status",
            "unavailable",
            "500",
            "503",
            "service unavailable",
            "incident",
        ),
    },
    {
        "title": "Account Access Issue",
        "content": (
            "For account/org access problems: validate user role mappings, SSO group claims, domain claims, "
            "SCIM provisioning, and deactivated users. Administrators can reinstate seats and fix group sync."
        ),
        "keywords": (
            "access",
            "permission",
            "role",
            "admin",
            "workspace",
            "organization",
            "sso",
            "scim",
            "provision",
            "invite",
            "member",
        ),
    },
    {
        "title": "Data Sync Issue",
        "content": (
            "For sync delays or missing records: check connector health logs, backoff windows, webhook "
            "delivery failures, conflicting schema changes, idempotency keys, and reconcile last successful sync timestamps."
        ),
        "keywords": (
            "sync",
            "synchronization",
            "delay",
            "missing data",
            "connector",
            "import",
            "export",
            "etl",
            "reconciliation",
            "duplicate",
            "latency",
            "queued",
        ),
    },
    {
        "title": "Password Reset and Recovery",
        "content": (
            "Use Forgot Password from the login screen. Check spam for the reset email. "
            "If SSO-only org: reset flows through your IdP. After reset, wait 5 minutes before retrying to avoid lockouts. "
            "Admins can trigger a force password reset for managed accounts."
        ),
        "keywords": (
            "reset password",
            "forgot",
            "recovery",
            "reset link",
            "email link",
            "did not receive",
        ),
    },
    {
        "title": "Mobile App Issues",
        "content": (
            "Update the app to the latest version, confirm OS meets minimum requirements, clear app cache, "
            "and re-authenticate. If offline mode is enabled, sync when back online. "
            "Collect device model, OS version, and in-app build number for support."
        ),
        "keywords": (
            "mobile",
            "iphone",
            "android",
            "ios",
            "tablet",
            "app crash",
            "app store",
            "play store",
        ),
    },
    {
        "title": "Email Notifications",
        "content": (
            "Verify notification preferences under Settings > Notifications and that the address is verified. "
            "Check SPF/DMARC if using a custom outbound domain and allow-list our sender domain. "
            "Delays during incidents are listed on the status page."
        ),
        "keywords": (
            "email",
            "notification",
            "not receiving emails",
            "digest",
            "alert",
            "smtp",
            "bounce",
        ),
    },
    {
        "title": "Exports and Reporting",
        "content": (
            "Large exports queue asynchronously; retry after the stated SLA window if pending. "
            "Use CSV for spreadsheets and API for programmatic pulls. Filters and date ranges apply at export time. "
            "If row counts mismatch, regenerate after cache refresh."
        ),
        "keywords": (
            "export",
            "csv",
            "report",
            "download",
            "analytics",
            "metrics",
            "snowflake",
            "spreadsheet",
        ),
    },
    {
        "title": "Privacy and Data Requests",
        "content": (
            "Data subject requests (access, deletion, portability) are handled via Privacy Requests in Settings or legal@. "
            "Retention follows your organization's policy and contracted region. Confirm account identity before fulfillment."
        ),
        "keywords": (
            "privacy",
            "gdpr",
            "delete my data",
            "export my data",
            "dsar",
            "compliance personal data",
        ),
    },
    {
        "title": "VPN, Firewall and Network Access",
        "content": (
            "Allow required domains and egress IPs documented in Networking Requirements. Split-tunnel VPNs may block SSO or API calls. "
            "Corporate proxies must support WebSockets where real-time features are used. Capture traceroute/MTR when intermittent."
        ),
        "keywords": (
            "vpn",
            "firewall",
            "proxy",
            "network",
            "blocked",
            "egress ip",
            "websocket",
            "corporate network",
        ),
    },
    {
        "title": "Browser and Compatibility",
        "content": (
            "Use supported browsers (current Chrome, Edge, Firefox, Safari). Disable incompatible extensions that inject scripts. "
            "Hard refresh (cache clear) resolves many UI glitches. Third-party cookie restrictions can break SSO in some setups."
        ),
        "keywords": (
            "browser",
            "chrome",
            "safari",
            "firefox",
            "edge",
            "blank page",
            "javascript",
            "cookies",
            "compatible",
        ),
    },
    {
        "title": "Changing Plans and Seats",
        "content": (
            "Admins adjust seat counts and SKU in Billing > Plans mid-cycle with proration where applicable. "
            "Downgrades take effect at period end unless support applies an exception. "
            "Invoices reflect changes within one billing cycle."
        ),
        "keywords": (
            "upgrade",
            "downgrade",
            "seats",
            "license",
            "plan change",
            "add user",
            "remove user",
        ),
    },
    {
        "title": "Feature Requests and Roadmap",
        "content": (
            "Submit ideas via Product Feedback inside the app. Prioritization considers customer impact and strategic fit. "
            "No committed dates until an item enters the published roadmap."
        ),
        "keywords": (
            "feature request",
            "roadmap",
            "when will you",
            "enhancement suggestion",
            "wishlist",
        ),
    },
    {
        "title": "Trial and Sandbox",
        "content": (
            "Trials expire after the stated duration; sandbox data does not migrate to production. "
            "Request extension via sales before expiration. Sandbox rate limits differ from prod."
        ),
        "keywords": (
            "trial",
            "sandbox",
            "poc",
            "demo environment",
            "trial expired",
        ),
    },
    {
        "title": "General Support",
        "content": (
            "We're here to help. Share what you're trying to do, recent steps, screenshots or error messages, "
            "and timestamps. We'll guide you toward the quickest resolution or escalate if needed."
        ),
        "keywords": (),
    },
)
