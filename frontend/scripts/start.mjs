import { cpSync } from "node:fs";

cpSync(".next/static", ".next/standalone/.next/static", { recursive: true });
process.env.HOSTNAME = "127.0.0.1";
const index = process.argv.indexOf("--port");
process.env.PORT =
  index >= 0 ? process.argv[index + 1] : (process.env.PORT ?? "3000");
await import("../.next/standalone/server.js");
