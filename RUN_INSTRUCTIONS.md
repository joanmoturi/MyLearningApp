# How to run Engineering Academy

These instructions use Windows PowerShell. No Docker, API key or paid service is required.

## 1. Open the project

On the current machine:

```powershell
Set-Location C:\Users\joanmoturi\engineering-academy
```

On another machine, install Git, Python 3.14 and Node.js 26 (including npm), then clone the repository:

```powershell
git clone https://github.com/joanmoturi/MyLearningApp.git engineering-academy
Set-Location engineering-academy
```

The repository is private, so you need GitHub access. Use your actual project directory if it differs from the path above.

## 2. Install dependencies once

Run from the project directory:

```powershell
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
}
.\scripts\Setup.ps1
```

This installs backend/frontend dependencies and builds the frontend. The default configuration is sufficient. Existing `.env` settings are preserved.

If setup was already completed successfully on this machine, skip this step for normal startup.

## 3. Start the backend

In **PowerShell terminal 1**, run:

```powershell
Set-Location C:\Users\joanmoturi\engineering-academy
.\scripts\Start-Backend.ps1
```

Use your own clone's directory on another machine. Leave this terminal running.

The backend listens at `http://127.0.0.1:8000`. On first startup it initializes the database, runs migrations and loads the research catalogue.

## 4. Start the frontend

Open **a second PowerShell terminal**, then run:

```powershell
Set-Location C:\Users\joanmoturi\engineering-academy
.\scripts\Start-Frontend.ps1
```

Leave this terminal running too. Wait for the frontend to report that it is ready.

## 5. Open the application

Enter this address in your browser:

**http://127.0.0.1:3000**

To check the backend from another terminal:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

These addresses assume the default configuration. Keep the application bound to localhost; it is not an authenticated public website.

## Stop and restart

Press **Ctrl+C in both server terminals** to stop the application. Closing the browser alone does not stop the servers.

To use it again, repeat steps 3-5. You do not need to reinstall dependencies each time.

Learning progress and personal records are stored in `data\academy.sqlite3`, not in the browser. Do not delete the `data` directory, and keep `.env` private.

## Back up and update

While both servers are running, create a private backup:

```powershell
.\scripts\Backup.ps1
```

Then stop both servers before updating:

```powershell
git pull --ff-only
.\scripts\Setup.ps1
```

Restart using steps 3-5. Do not overwrite `.env` or delete your database during updates.

## If something goes wrong

- **Missing dependency or frontend build:** run step 2 and resolve any reported errors.
- **Browser cannot connect:** confirm both terminals are still running and inspect their errors.
- **Port already in use:** stop your own existing Academy server with Ctrl+C before restarting; do not stop unrelated services.
- **PowerShell blocks scripts:** follow the equivalent native commands in [README.md](README.md); do not bypass your security policy.

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more help and [BACKUP_AND_RESTORE.md](BACKUP_AND_RESTORE.md) for recovery and moving data to another laptop.
