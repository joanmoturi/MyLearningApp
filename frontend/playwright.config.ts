import { defineConfig } from "@playwright/test";
import path from "node:path";

const root = path.resolve(process.cwd(), "..");
const python =
  process.platform === "win32"
    ? path.join(root, ".venv", "Scripts", "python.exe")
    : path.join(root, ".venv", "bin", "python");
const origin = "http://127.0.0.1:3127";

export default defineConfig({
  testDir: "./e2e",
  timeout: 90000,
  workers: 1,
  use: {
    baseURL: origin,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  webServer: [
    {
      command: `"${python}" -m uvicorn academy.main:app --app-dir "${path.join(root, "backend")}" --host 127.0.0.1 --port 8127`,
      url: "http://127.0.0.1:8127/api/health",
      env: {
        DATABASE_URL:
          "sqlite:///" + path.join(root, "data", `e2e-${Date.now()}.sqlite3`),
        APP_ORIGIN: origin,
        YOUTUBE_API_KEY: "",
        OPENAI_API_KEY: "",
        AI_MODEL: "",
      },
      reuseExistingServer: false,
    },
    {
      command: "npm run start -- --port 3127",
      url: origin,
      env: { BACKEND_URL: "http://127.0.0.1:8127", APP_ORIGIN: origin },
      reuseExistingServer: false,
    },
  ],
});
