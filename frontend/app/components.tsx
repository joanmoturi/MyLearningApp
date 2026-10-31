"use client";

import { useState, type ReactNode } from "react";
import { human, obj, safeLink, text, type Row } from "../lib/data";

export function External({
  url,
  children,
}: {
  url: unknown;
  children: ReactNode;
}) {
  const href = safeLink(url);
  return href ? (
    <a
      className="external"
      href={href}
      target="_blank"
      rel="noopener noreferrer"
    >
      {children} <span aria-hidden="true">↗</span>
    </a>
  ) : (
    <span className="muted">Link unavailable</span>
  );
}

export function Content({ value }: { value: unknown }) {
  if (value === null || value === undefined)
    return <span className="muted">Not available in the research</span>;
  if (Array.isArray(value))
    return (
      <ul className="content-list">
        {value.map((item, index) => (
          <li key={index}>
            <Content value={item} />
          </li>
        ))}
      </ul>
    );
  if (typeof value === "object")
    return (
      <dl className="content-detail">
        {Object.entries(obj(value)).map(([key, item]) => (
          <div key={key}>
            <dt>{human(key)}</dt>
            <dd>
              <Content value={item} />
            </dd>
          </div>
        ))}
      </dl>
    );
  return <span className="prose">{String(value)}</span>;
}

export interface Field {
  name: string;
  label: string;
  type?:
    | "text"
    | "textarea"
    | "number"
    | "checkbox"
    | "select"
    | "multi"
    | "url"
    | "date";
  options?: { value: string; label: string }[];
  required?: boolean;
  min?: number;
  max?: number;
  hint?: string;
}

export function Editor({
  fields,
  initial = {},
  onSave,
  submit = "Save",
  extra,
}: {
  fields: Field[];
  initial?: Row;
  onSave: (data: Row) => Promise<void>;
  submit?: string;
  extra?: ReactNode | ((data: Row) => ReactNode);
}) {
  const [data, setData] = useState<Row>(initial);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  return (
    <form
      className="editor"
      onSubmit={async (event) => {
        event.preventDefault();
        setError("");
        setSaving(true);
        try {
          await onSave(data);
        } catch (error) {
          setError(error instanceof Error ? error.message : "Save failed");
        } finally {
          setSaving(false);
        }
      }}
    >
      {fields.map((field) => (
        <label
          key={field.name}
          className={field.type === "checkbox" ? "check" : ""}
        >
          <span>{field.label}</span>
          {field.type === "textarea" ? (
            <textarea
              aria-label={field.label}
              required={field.required}
              value={text(data[field.name])}
              onChange={(event) =>
                setData({ ...data, [field.name]: event.target.value })
              }
              rows={5}
            />
          ) : field.type === "select" || field.type === "multi" ? (
            <select
              aria-label={field.label}
              required={field.required}
              multiple={field.type === "multi"}
              value={
                field.type === "multi"
                  ? Array.isArray(data[field.name])
                    ? (data[field.name] as string[])
                    : []
                  : text(data[field.name])
              }
              onChange={(event) =>
                setData({
                  ...data,
                  [field.name]:
                    field.type === "multi"
                      ? Array.from(
                          event.target.selectedOptions,
                          (option) => option.value,
                        )
                      : event.target.value,
                })
              }
            >
              {field.type !== "multi" && <option value="">Select…</option>}
              {field.options?.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          ) : (
            <input
              aria-label={field.label}
              type={field.type ?? "text"}
              required={field.required}
              min={field.min}
              max={field.max}
              checked={
                field.type === "checkbox"
                  ? Boolean(data[field.name])
                  : undefined
              }
              value={
                field.type === "checkbox" ? undefined : text(data[field.name])
              }
              onChange={(event) =>
                setData({
                  ...data,
                  [field.name]:
                    field.type === "checkbox"
                      ? event.target.checked
                      : field.type === "number"
                        ? event.target.value === ""
                          ? ""
                          : Number(event.target.value)
                        : event.target.value,
                })
              }
            />
          )}
          {field.hint && <small>{field.hint}</small>}
        </label>
      ))}
      {typeof extra === "function" ? extra(data) : extra}
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      <button className="primary" disabled={saving} type="submit">
        {saving ? "Saving…" : submit}
      </button>
    </form>
  );
}

export function Card({
  title,
  children,
  eyebrow,
}: {
  title: string;
  children: ReactNode;
  eyebrow?: string;
}) {
  return (
    <article className="card">
      {eyebrow && <p className="eyebrow">{eyebrow}</p>}
      <h3>{title}</h3>
      {children}
    </article>
  );
}
