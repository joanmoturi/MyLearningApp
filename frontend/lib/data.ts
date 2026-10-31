export interface Row {
  id?: string;
  [key: string]: unknown;
}
export function obj(value: unknown): Row {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as Row)
    : {};
}
export function rows(value: unknown): Row[] {
  return Array.isArray(value) ? value.map(obj) : [];
}
export function text(value: unknown): string {
  return typeof value === "string"
    ? value
    : typeof value === "number"
      ? String(value)
      : "";
}
export function num(value: unknown): number {
  return typeof value === "number" ? value : 0;
}
export function strings(value: unknown): string[] {
  return Array.isArray(value)
    ? value.filter((item): item is string => typeof item === "string")
    : [];
}
export function human(value: string): string {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export async function api<T = Row>(
  path: string,
  method = "GET",
  payload?: unknown,
): Promise<T> {
  const response = await fetch(`/api/${path}`, {
    method,
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
      "X-Academy-Client": "local-workspace",
    },
    ...(payload === undefined ? {} : { body: JSON.stringify(payload) }),
  });
  const body: unknown = await response.json();
  if (!response.ok) {
    const detail = obj(body).detail;
    throw new Error(
      typeof detail === "string"
        ? detail
        : JSON.stringify(detail ?? "Request failed"),
    );
  }
  return body as T;
}

export function safeLink(value: unknown): string | undefined {
  if (typeof value !== "string") return undefined;
  try {
    const url = new URL(value);
    return ["http:", "https:"].includes(url.protocol) &&
      !url.username &&
      !url.password
      ? url.href
      : undefined;
  } catch {
    return undefined;
  }
}

export async function catalogue(kind: string): Promise<Row> {
  const first = await api(`catalog/${kind}?limit=400&offset=0`);
  const total = num(first.total);
  if (total > 10000)
    throw new Error(
      "Catalogue exceeds the supported 10,000-record collection limit.",
    );
  const items = rows(first.items);
  while (items.length < total) {
    const page = await api(`catalog/${kind}?limit=400&offset=${items.length}`);
    const batch = rows(page.items);
    if (num(page.total) !== total || batch.length === 0)
      throw new Error("Catalogue changed while loading. Retry the workspace.");
    items.push(...batch);
  }
  if (new Set(items.map((item) => item.id)).size !== items.length)
    throw new Error("Catalogue changed while loading. Retry the workspace.");
  return { items, total };
}
