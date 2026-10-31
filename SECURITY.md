# Security

Engineering Academy is designed for one learner on a trusted laptop. It has no public-service authentication. Keep native services on loopback; do not expose them with public tunnels or LAN bindings.

The proxy validates the exact configured Host, denies unexpected Origins, validates paths and requires a custom mutation header. The backend also restricts hosts/origins. Restore requires a separate explicit confirmation. These controls address hostile website access; they do not isolate the learner from other local processes or operating-system users.

SQLAlchemy parameter binding, strict Pydantic inputs, safe HTTP(S) links without credentials, escaped React content, Markdown without raw HTML, security headers, bounded imports and snapshot integrity checks provide defense in depth. API keys are backend environment variables only. Provider failures omit credential-bearing URLs. Configured secrets never enter exports.

Keep `.env`, `data`, snapshots, private notes and traces out of Git. Check research-profile content before making the repository public. No application license has been selected.

To report a vulnerability, use the repository's private GitHub security advisory/reporting facility if enabled, or contact the repository owner privately through GitHub. Do not include secrets, private databases or personal notes in a public issue.

Known development-only dependency advisories and audit scope are documented in `SECURITY_AUDIT.md`. Production dependency scans and boundary regression tests run in CI. A passing scan does not guarantee security.
