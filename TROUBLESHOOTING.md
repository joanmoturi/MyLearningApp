# Troubleshooting

| Symptom | Action |
|---|---|
| Local API unavailable | Start the backend; check `http://127.0.0.1:8000/api/health`. Existing data remains on disk. |
| Untrusted local Host / cross-origin denied | Open the exact configured `APP_ORIGIN`. Defaults use `127.0.0.1`, not a different hostname or port. Restart the frontend after configuration changes. |
| Port in use | Identify the listener; do not kill unrelated processes. Set a free frontend `APP_ORIGIN` and use the start script. For backend changes use an explicit loopback Uvicorn port and matching `BACKEND_URL`. |
| Missing research | Restore tracked dataset files. Available validated content is shown; absent curricula cannot be generated. The JSON schema file is essential. |
| Invalid import | Read the validation error, resolve IDs/schema/references and create a new preview. Nothing is applied on preview failure. |
| Preview stale/expired | Generate a fresh preview after edits or after 30 minutes. |
| Lesson not fully complete | Save all four explicit flags; practical completion needs evidence and knowledge completion needs an answer. |
| Higher competency rejected | Provide a concrete practical artifact/test explanation, not just a background claim. |
| Plan grows after shortening | Historical/custom/annotated work is retained, so the result can exceed the requested template length. |
| Company deletion rejected | Reassign/delete linked jobs before deleting the employer. |
| Provider not configured / quota error | Use stored links and local rubrics. Configure only optional server-side keys; do not bypass restrictions. |
| Snapshot restore rejected | Check file size, SQLite format and compatible migration version. Keep the original and recovery copy safe. |
| PowerShell script restricted | Run the equivalent explicit README commands; do not change execution policy for this application. |
| npm install script warning | A dependency can request native optional installation. Tested build/tests work without broad script approval; investigate a concrete failure rather than enabling approve-all. |
| Development npm advisory | See `SECURITY_AUDIT.md`; do not force a breaking ESLint downgrade to hide an unresolved transitive advisory. |

Stop native servers with Ctrl+C in their own terminals. Do not delete `data` when updating or troubleshooting.
