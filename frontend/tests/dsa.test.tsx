import { render, screen } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import DsaPractice from "../app/dsa-practice";

it("shows unassessed DSA performance without fabricating percentages", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation((url: string) =>
      Promise.resolve(
        Response.json(
          url === "/api/dsa"
            ? {
                analytics: {
                  topics: [
                    {
                      skill_id: "skill-dsa-graphs",
                      name: "Graphs",
                      attempts: 0,
                      independent_rate: null,
                    },
                  ],
                  history: [],
                  questions_attempted: 0,
                  solved_independently: 0,
                  states: {},
                },
                companies: [],
                dimensions: [],
              }
            : { items: [], total: 0 },
        ),
      ),
    ),
  );
  try {
    render(<DsaPractice aiConfigured={false} onChanged={vi.fn()} />);
    expect(
      await screen.findByText("Graphs", { selector: "strong" }),
    ).toBeVisible();
    expect(
      screen.getByText(/independent sample-pass rate: Not assessed/),
    ).toBeVisible();
    expect(screen.queryByText("0%")).toBeNull();
    expect(
      screen.queryByRole("button", { name: "Request coding feedback" }),
    ).toBeNull();
  } finally {
    vi.unstubAllGlobals();
  }
});
