// @vitest-environment node
import { afterEach, expect, it, vi } from "vitest";
import { NextRequest } from "next/server";
import { GET, POST } from "../app/api/[...path]/route";

afterEach(() => vi.unstubAllGlobals());
const context = { params: Promise.resolve({ path: ["data", "export"] }) };

it("rejects hostile Host even when Origin is absent", async () => {
  const fetch = vi.fn();
  vi.stubGlobal("fetch", fetch);
  const response = await GET(
    new NextRequest("http://evil.example:3000/api/data/export", {
      headers: { host: "evil.example:3000" },
    }),
    context,
  );
  expect(response.status).toBe(403);
  expect(fetch).not.toHaveBeenCalled();
});
it("rejects cross-origin access with a legitimate local Host", async () => {
  const response = await GET(
    new NextRequest("http://127.0.0.1:3000/api/data/export", {
      headers: { host: "127.0.0.1:3000", origin: "https://evil.example" },
    }),
    context,
  );
  expect(response.status).toBe(403);
});
it("forwards explicit restore confirmation after validating the local boundary", async () => {
  const fetch = vi.fn().mockResolvedValue(Response.json({ restored: true }));
  vi.stubGlobal("fetch", fetch);
  const response = await POST(
    new NextRequest("http://127.0.0.1:3000/api/data/restore", {
      method: "POST",
      headers: {
        host: "127.0.0.1:3000",
        "x-academy-client": "local-workspace",
        "x-academy-confirm": "restore",
      },
      body: "fixture",
    }),
    { params: Promise.resolve({ path: ["data", "restore"] }) },
  );
  expect(response.status).toBe(200);
  expect(fetch.mock.calls[0][1].headers["X-Academy-Confirm"]).toBe("restore");
});
it("rejects encoded path traversal", async () => {
  const response = await GET(
    new NextRequest("http://127.0.0.1:3000/api/data/export", {
      headers: { host: "127.0.0.1:3000" },
    }),
    { params: Promise.resolve({ path: ["..", "export"] }) },
  );
  expect(response.status).toBe(400);
});
