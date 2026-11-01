# Production readiness report - 2026-10-31

**Sixth-track update, November 1, 2026:** 90 local application tests pass; DSA research, coding isolation, migration/legacy restore and exact existing personal-data retention are verified. See `DSA_IMPLEMENTATION_REPORT.md` for current scope and remaining limitations. Hosted sixth-track CI is pending; the original evidence below refers to the original five-track runtime.

**Status: core native release, fresh-checkout recovery and hosted CI verified; remaining acceptance gaps are explicit.** This is a local single-learner product, not an authenticated Internet-facing service.

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
| D14 | Medium | Fresh-install/hosted CI acceptance | Native clean-clone installation/restart/restore passed; published runtime `a2ab363` passed hosted CI run `41233814617`. |
| D15 | Low | Monolithic frontend orchestration | Shared typed helpers/components; future section extraction documented. |
| D16 | Low | License/public visibility undecided | Explicit pending license; repository stays private. |
| D17 | Medium | Imported catalogues silently stopped at 400 records | Initial and post-import loading aggregate pages; 401-question regression passes, with a 10,000-record per-kind bound. |

## Verified evidence and remaining conditions

See `TEST_RESULTS.md` for the current 90-test release and historical 48-test baseline; `SECURITY_AUDIT.md` for scope, findings and dependency scans; `INSTALLATION_VERIFICATION.md` for fresh-checkout evidence.

Research files/history are preserved. Core operation needs no API key or paid service. AI feedback, provider quota usage, cloud exercise deployments and external hosting may cost money when explicitly configured.

The original five-track runtime is `a2ab3639aa3cc3b8847ecef6aac32ea36231e1e0`; its report-only commits record historical evidence. Docker execution, live provider credentials, an actual laptop reboot and exhaustive video playback remain unverified. Development-tree dependency advisories and the owner's licensing decision remain unresolved.

Product-depth limitations also remain: job analysis uses editable keyword/section matching, priority skills are highlighted rather than semantically rescheduled, and resource availability/content quality still requires human review. Public-service authentication and PostgreSQL deployment are not implemented or claimed. These limitations prevent an unconditional all-requirements acceptance claim, but do not require paid APIs for verified core local use.
