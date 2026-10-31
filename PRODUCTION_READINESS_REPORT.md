# Production readiness report - 2026-10-31

**Status: core native workflows verified; release acceptance still conditional.** This is a local single-learner product, not an authenticated Internet-facing service.

The incoming assumption that implementation was complete was incorrect: the backend was unvalidated and the actual frontend was missing. The audit therefore included completing the functional workspace rather than merely reviewing scaffolding.

## Prioritized defect register

| ID | Priority | Defect | Outcome |
|---|---|---|---|
| D01 | Critical | Missing functional frontend/workflows | Eleven functional sections implemented; browser acceptance passes. |
| D02 | High | Proxy omitted Host validation | Fixed; independent finding plus unit/real HTTP regressions. |
| D03 | High | Backup/restore failed on Windows/open handles and file limit | Explicit connection close, compact snapshots, 64 MB restore and validated recovery tested. |
| D04 | High | Custom plan route shadowed by action route | Dedicated status path; custom lessons tested. |
| D05 | High | Recalculation moved later-started lessons before prerequisites/lost annotations | Ordering and retained identities/annotations fixed and tested. |
| D06 | High | Proxy discarded restore confirmation | Exact confirmation forwarding fixed and tested. |
| D07 | High | Research missing-file startup failed | Explicit partial-catalog mode; missing data displayed, no invented resources. |
| D08 | High | Backup imports lacked strong index/reference/evidence checks | Scalar/schema/FK/index/domain validation and stale-preview rejection added. |
| D09 | Medium | Streak lost earlier days when lessons updated | Separate UTC daily activity persistence added. |
| D10 | Medium | Provider timeout/status errors could become server errors | Safe bounded request adapter and mocked regression cases. |
| D11 | Medium | Standalone frontend startup warning/asset mismatch | Dedicated native standalone launcher and successful browser startup. |
| D12 | Medium | Development dependency advisory | Unresolved upstream minimatch advisory; 16 moderate dependent reports, zero production advisories. |
| D13 | Medium | Docker execution not available | Compose/Dockerfiles supplied; native alternative tested, Docker acceptance pending. |
| D14 | Medium | Fresh-install/hosted CI acceptance | Native clean-clone installation/restart/restore passed; hosted CI verification pending. |
| D15 | Low | Monolithic frontend orchestration | Shared typed helpers/components; future section extraction documented. |
| D16 | Low | License/public visibility undecided | Explicit pending license; repository stays private. |

## Verified evidence and remaining conditions

See `TEST_RESULTS.md` for 47 passing application tests and quality checks; `SECURITY_AUDIT.md` for scope, findings and dependency scans; `INSTALLATION_VERIFICATION.md` for fresh-checkout evidence.

Research files/history are preserved. Core operation needs no API key or paid service. AI feedback, provider quota usage, cloud exercise deployments and external hosting may cost money when explicitly configured.

Do not declare all production-readiness acceptance items complete until the fresh installation and GitHub-hosted CI are recorded. Docker execution, live provider credentials and public-service authentication remain outside current verified readiness.
