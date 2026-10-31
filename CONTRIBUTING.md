# Contributing

Read the README, architecture and security boundary before making changes. Keep the product local-first and optional APIs optional.

Use the pinned backend lock and frontend lockfile. Run the documented backend tests/Ruff checks and frontend typecheck/lint/format/tests/build/browser acceptance. Add focused regression cases for changed behavior. Do not weaken evidence validation, Host/Origin checks or import checks to make tests pass.

Preserve canonical research, unique IDs and personal plan snapshots. New database changes need new Alembic revisions with upgrade/persistence tests. Do not commit secrets, personal databases, notes, snapshots, traces or dependency directories.

The repository's license decision is pending; contributions and a public release require clarification from the owner.
