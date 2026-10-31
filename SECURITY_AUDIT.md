# Security audit - 2026-10-31

## Scope and outcome

An independent read-only security agent reviewed the implemented FastAPI/data-management/provider code and Next.js proxy/configuration. The frontend was incomplete at that review; subsequent application completion and boundary regression testing were performed by the implementing agent. This is not a claim of an independent final penetration test.

| # | Severity | File | Lines | Vulnerability | Confidence |
|---|----------|------|-------|---------------|------------|
| 1 | HIGH | `frontend\app\api\[...path]\route.ts` | Original 5-13, 42-54 | Missing Host validation enabled a DNS-rebinding route to personal exports through the trusted proxy | 9/10 |

**Remediated:** the proxy rejects absent/unexpected Host authorities before forwarding any method, retains Origin/custom-header checks and forwards restore confirmation only explicitly. Vitest hostile-Host tests and a real Playwright request verify rejection. The independent reproduction used a mocked upstream; browser-level DNS rebinding was not performed.

## Additional hardening and checks

- Loopback native listeners; Docker only publishes a loopback frontend port.
- No permissive CORS; unexpected Origins denied, including export GETs.
- Strict Pydantic fields, bounded file/JSON sizes, credential-free HTTP(S) links.
- SQLAlchemy parameterized queries and database relationships.
- React escaping and Markdown without raw HTML; no unsafe rendering of provider comments.
- Explicit practical/knowledge evidence; backup validation enforces the same invariants.
- Restore validates schema/version/integrity/references before replacing data and keeps a recovery copy.
- Imports are previewed/digest-checked, reject stale previews and cannot remove historical research IDs.
- Outgoing provider network/status/JSON errors are translated into safe errors; HTTP-client URL logging is restricted.
- Git secret-pattern check found no matching committed private-key/API-token patterns. This is a targeted check, not a guarantee against every possible secret.

## Dependency scans

`pip_audit --progress-spinner off`: no known dependency advisories. The editable application itself is not a PyPI package and is not covered by that dependency scanner.

`npm audit --omit=dev --audit-level=moderate`: **0 production dependency advisories**.

Full `npm audit`: **16 moderate development-tree advisories**, rooted in minimatch globparts amplification (`GHSA-g3hv-75wg-m249`) and reported through ESLint/transitive dependents. The advisory currently covers all minimatch versions. The suggested force command downgrades ESLint to a breaking old version; it was not used. These are not 16 independently exploitable application endpoints. Linting only processes repository-controlled patterns, but the unresolved dependency risk remains documented. Recheck upstream patches before a public release. CI's production scan is explicitly scoped; it does not claim the complete development tree is advisory-free.

## Residual boundaries

No real multi-user authentication, no isolation from other local OS users/processes, no live provider credential verification and no Docker network execution test on this machine. Do not expose this local product as a public service. Review research-profile content and select a license before changing repository visibility.
