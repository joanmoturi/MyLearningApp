import { NextRequest } from "next/server";

const MAX_BODY = 20 * 1024 * 1024;

async function proxy(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const origin = request.headers.get("origin");
  const allowedOrigin = process.env.APP_ORIGIN ?? "http://127.0.0.1:3000";
  if (request.headers.get("host") !== new URL(allowedOrigin).host) {
    return Response.json({ detail: "Untrusted local host." }, { status: 403 });
  }
  if (origin && origin !== allowedOrigin) {
    return Response.json(
      { detail: "Cross-origin requests are not allowed." },
      { status: 403 },
    );
  }
  if (
    !["GET", "HEAD"].includes(request.method) &&
    request.headers.get("x-academy-client") !== "local-workspace"
  ) {
    return Response.json(
      { detail: "Missing same-origin client header." },
      { status: 403 },
    );
  }
  const path = (await context.params).path;
  if (path.some((part) => !/^[a-zA-Z0-9_-]+$/.test(part))) {
    return Response.json({ detail: "Invalid API path." }, { status: 400 });
  }
  const limit = path.join("/") === "data/restore" ? 64 * 1024 * 1024 : MAX_BODY;
  const declared = Number(request.headers.get("content-length") ?? 0);
  if (declared > limit)
    return Response.json(
      { detail: "File exceeds the permitted size." },
      { status: 413 },
    );
  let body: ArrayBuffer | undefined;
  if (!["GET", "HEAD"].includes(request.method)) {
    const chunks: Uint8Array[] = [];
    let size = 0;
    const reader = request.body?.getReader();
    if (reader) {
      while (true) {
        const part = await reader.read();
        if (part.done) break;
        size += part.value.byteLength;
        if (size > limit) {
          await reader.cancel();
          return Response.json(
            { detail: "Import exceeds 20 MB." },
            { status: 413 },
          );
        }
        chunks.push(part.value);
      }
    }
    const bytes = new Uint8Array(size);
    let offset = 0;
    for (const chunk of chunks) {
      bytes.set(chunk, offset);
      offset += chunk.length;
    }
    body = bytes.buffer;
  }
  const backend = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";
  try {
    const response = await fetch(
      `${backend}/api/${path.join("/")}${request.nextUrl.search}`,
      {
        method: request.method,
        headers: {
          "Content-Type":
            request.headers.get("content-type") ?? "application/json",
          "X-Academy-Client": "local-workspace",
          ...(request.headers.get("x-academy-confirm") === "restore"
            ? { "X-Academy-Confirm": "restore" }
            : {}),
        },
        body,
        cache: "no-store",
        signal: AbortSignal.timeout(60000),
      },
    );
    const headers = new Headers({
      "Content-Type":
        response.headers.get("content-type") ?? "application/json",
      "Cache-Control": "no-store",
    });
    const disposition = response.headers.get("content-disposition");
    if (disposition) headers.set("Content-Disposition", disposition);
    return new Response(response.body, { status: response.status, headers });
  } catch {
    return Response.json(
      {
        detail:
          "The local API is unavailable. Start the backend and retry; your data remains on disk.",
      },
      { status: 503 },
    );
  }
}

export const GET = proxy;
export const POST = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
