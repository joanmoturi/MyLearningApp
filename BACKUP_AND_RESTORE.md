# Backup and restore

Keep private snapshots outside public/cloud-shared folders unless you intentionally protect and transfer that data.

With both servers running:

```powershell
.\scripts\Backup.ps1
.\scripts\Backup.ps1 -Destination C:\private-backups\academy.sqlite3
.\scripts\Restore.ps1 -Snapshot C:\private-backups\academy.sqlite3 -Confirm
```

The destination directory must exist for a custom path. Default backups go to the ignored repository `backups` directory and use timestamps. Settings provides equivalent snapshot, full JSON and Markdown exports.

Snapshots use SQLite's backup API, not a copy of a live/writable file. Transient import previews are removed from the copy and it is compacted. Personal tables, learning evidence, research, notes and optional metadata cache remain. Restore verifies the header, integrity, known schema/version, foreign references, JSON/research indexes and evidence before replacing the database. The original is retained as `data\academy.pre-restore.sqlite3`.

JSON imports merge matching IDs after preview and confirmation; they are not an exact deletion/replacement mechanism. SQLite restore is the exact whole-database recovery mechanism. A changed workspace invalidates a pending JSON preview.

## Move laptops

1. Create and privately transfer a SQLite snapshot.
2. Clone and install the same application release on the new laptop using the README.
3. Start both servers and explicitly restore.
4. Reload the browser and check plans, notes and evidence before removing the old copy.

No API keys are inside the snapshot. Reconfigure optional keys separately if desired.

Current SQLite restore accepts migration revisions `0001` and `0002` and files up to 64 MB. Older snapshots undergo full legacy-schema validation before migration to `0002` and replacement. JSON import is bounded to 20 MB. For incompatible or larger databases, keep the original safe and use a version-aware maintenance process; never alter the schema to bypass validation.

DSA sessions, saved code/approaches, self-ratings, assistance flags and review schedules are included in private backups/JSON exports. Coding fixture checks are recomputed during validation. Restoring an older five-track snapshot requires a backend restart to add missing optional DSA documents; older personal records remain intact. Research refreshes never replace saved attempts or notes.

Automated tests cover restore after later changes, restore into a fresh initialized database, rejection of invalid snapshots and restart persistence. Docker-volume restart/reboot recovery requires Docker verification and has not been claimed on the native-only test machine.
