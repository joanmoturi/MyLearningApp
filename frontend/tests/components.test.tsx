import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import Markdown from "react-markdown";
import { Editor, External } from "../app/components";
import { api, safeLink } from "../lib/data";

describe("safe resource and note rendering", () => {
  it("rejects script URLs and credentials", () => {
    expect(safeLink("javascript:alert(1)")).toBeUndefined();
    expect(safeLink("https://user:password@example.com")).toBeUndefined();
    render(<External url="https://example.com/docs">Documentation</External>);
    expect(screen.getByRole("link")).toHaveAttribute(
      "rel",
      "noopener noreferrer",
    );
  });
  it("never renders raw HTML in Markdown notes", () => {
    const { container } = render(
      <Markdown>{"# Notes\n<script>alert(1)</script>"}</Markdown>,
    );
    expect(container.querySelector("script")).toBeNull();
    expect(screen.getByRole("heading")).toHaveTextContent("Notes");
  });
});

describe("evidence forms", () => {
  it("captures explicit completion and implementation evidence", async () => {
    const save = vi.fn().mockResolvedValue(undefined);
    render(
      <Editor
        fields={[
          { name: "practical", label: "Practical completed", type: "checkbox" },
          {
            name: "evidence",
            label: "Submission evidence",
            type: "textarea",
            required: true,
          },
        ]}
        onSave={save}
      />,
    );
    expect(screen.getByRole("checkbox")).not.toBeChecked();
    fireEvent.click(screen.getByRole("checkbox"));
    fireEvent.change(screen.getByLabelText("Submission evidence"), {
      target: { value: "Tested the failure invariant." },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save" }));
    await waitFor(() =>
      expect(save).toHaveBeenCalledWith({
        practical: true,
        evidence: "Tested the failure invariant.",
      }),
    );
  });
  it("displays rejected API validation rather than fake success", async () => {
    render(
      <Editor
        fields={[]}
        onSave={async () => {
          throw new Error("Evidence required");
        }}
      />,
    );
    fireEvent.click(screen.getByRole("button"));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Evidence required",
    );
  });
  it("allows a multi-track project selection", async () => {
    const save = vi.fn().mockResolvedValue(undefined);
    render(
      <Editor
        fields={[
          {
            name: "track_ids",
            label: "Tracks",
            type: "multi",
            options: [
              { value: "track-swe", label: "Software" },
              { value: "track-ai", label: "AI" },
            ],
          },
        ]}
        onSave={save}
      />,
    );
    const select = screen.getByLabelText("Tracks") as HTMLSelectElement;
    select.options[0].selected = true;
    select.options[1].selected = true;
    fireEvent.change(select);
    fireEvent.click(screen.getByRole("button"));
    await waitFor(() =>
      expect(save).toHaveBeenCalledWith({
        track_ids: ["track-swe", "track-ai"],
      }),
    );
  });
  it("formats server errors while preserving local data", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          Response.json({ detail: "Local API unavailable" }, { status: 503 }),
        ),
    );
    await expect(api("bootstrap")).rejects.toThrow("Local API unavailable");
    vi.unstubAllGlobals();
  });
});
