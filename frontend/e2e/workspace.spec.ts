import { test, expect } from "@playwright/test";

test("DSA course, blind coding, isolated execution and persisted interview evidence", async ({
  page,
  request,
}) => {
  await page.goto("/");
  await page
    .getByRole("link", { name: "Learning Tracks", exact: true })
    .click();
  await page.getByLabel("Choose track").selectOption("track-dsa");
  await expect(
    page
      .getByRole("heading", {
        name: "Data Structures and Algorithms - Big Tech Coding Interviews",
        exact: true,
      })
      .first(),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Create learning plan", exact: true })
    .click();
  await page.getByLabel("Study duration", { exact: true }).selectOption("14");
  await page.getByRole("button", { name: "Generate study plan" }).click();
  await page
    .getByRole("button", { name: "Study", exact: true })
    .first()
    .click();
  await expect(
    page.getByText(
      "Algorithmic foundations, arrays and strings - concept and slice",
      { exact: true },
    ),
  ).toBeVisible();
  const youtube = page.locator('a[href*="youtube.com"]').first();
  await expect(youtube).toHaveAttribute("target", "_blank");
  await page
    .getByRole("link", { name: "Interview Preparation", exact: true })
    .click();
  await expect(
    page.getByRole("heading", {
      name: "DSA coding interview workspace",
      exact: true,
    }),
  ).toBeVisible();
  await page
    .getByLabel("DSA practice mode", { exact: true })
    .selectOption("blind");
  await page
    .getByLabel("Assessment duration", { exact: true })
    .selectOption("20");
  await page
    .getByLabel("Coding pattern", { exact: true })
    .selectOption("skill-dsa-foundations");
  await page
    .getByLabel("Coding difficulty", { exact: true })
    .selectOption("easy");
  await page
    .getByRole("button", { name: "Start coding practice", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Count triangular work", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText("Requested reference solution", { exact: true }),
  ).toHaveCount(0);
  await page
    .getByLabel("Coding solution", { exact: true })
    .fill("function solve(n) { return n * (n + 1) / 2; }");
  await page
    .getByLabel("Coding Approach", { exact: true })
    .fill("Sum the lengths from one through n using the closed form.");
  await page.getByLabel("Coding Time Complexity", { exact: true }).fill("O(1)");
  await page
    .getByLabel("Coding Space Complexity", { exact: true })
    .fill("O(1)");
  await page
    .getByRole("button", { name: "Save coding draft", exact: true })
    .click();
  await page.reload();
  await expect(
    page.getByRole("heading", {
      name: "DSA coding interview workspace",
      exact: true,
    }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Resume or inspect session", exact: true })
    .first()
    .click();
  await expect(page.getByLabel("Coding solution", { exact: true })).toHaveValue(
    "function solve(n) { return n * (n + 1) / 2; }",
  );
  await expect(
    page.getByRole("timer", { name: "Coding time remaining" }),
  ).toContainText("19:");
  await page
    .getByRole("button", { name: "Run sample tests", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Runner outputs", exact: true }),
  ).toBeVisible();
  await expect(page.locator("p[role='alert']")).toHaveCount(0);
  await page.getByLabel("I solved the problem", { exact: true }).check();
  for (const label of [
    "Understanding",
    "Pattern",
    "Algorithm",
    "Correctness",
    "Quality",
    "Time Complexity",
    "Space Complexity",
    "Edge Cases",
    "Testing",
    "Communication",
  ]) {
    await page
      .getByLabel(`${label} self-rating (0-5)`, { exact: true })
      .fill("4");
  }
  await page
    .getByRole("button", { name: "Submit coding answer", exact: true })
    .click();
  await expect(
    page.getByRole("heading", {
      name: "Coding session completed",
      exact: true,
    }),
  ).toBeVisible();
  const overview = await (await request.get("/api/dsa")).json();
  expect(overview.analytics.solved_independently).toBe(1);
  expect(overview.analytics.states["question-dsa-01"]).toBe(
    "solved_independently",
  );
  await page
    .getByText("Saved answer 1: Count triangular work", { exact: true })
    .click();
  await expect(
    page
      .locator("pre")
      .filter({ hasText: "function solve(n) { return n * (n + 1) / 2; }" }),
  ).toBeVisible();
  await page
    .getByLabel("Company preparation profile", { exact: true })
    .selectOption("profile-dsa-microsoft");
  await expect(
    page.getByRole("button", {
      name: "Start researched company practice",
      exact: true,
    }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Create company DSA plan", exact: true })
    .click();
  await expect(
    page.getByText(
      "Company DSA plan saved; sourced priorities are highlighted without violating prerequisites.",
      { exact: true },
    ),
  ).toBeVisible();
  const plans = await (await request.get("/api/plans")).json();
  expect(
    plans.some(
      (plan: { config: { target_role: string; duration_days: number } }) =>
        plan.config.target_role === "Microsoft coding preparation" &&
        plan.config.duration_days === 30,
    ),
  ).toBe(true);
  await page
    .getByRole("button", {
      name: "Start researched company practice",
      exact: true,
    })
    .click();
  const companyOverview = await (await request.get("/api/dsa")).json();
  expect(
    companyOverview.analytics.history.some(
      (item: { config: { mode: string } }) => item.config.mode === "company",
    ),
  ).toBe(true);
  const sandbox = await request.get("/coding-sandbox");
  expect(sandbox.headers()["content-security-policy"]).toContain(
    "connect-src 'none'",
  );
  const home = await request.get("/");
  expect(home.headers()["content-security-policy"]).not.toContain(
    "unsafe-eval",
  );
  await page
    .getByRole("button", {
      name: "Practice recommended next question",
      exact: true,
    })
    .click();
  await expect(
    page.getByRole("button", {
      name: "Practice recommended next question",
      exact: true,
    }),
  ).toBeEnabled();
  let probeRequests = 0;
  await page.context().route("**/dsa-network-probe", async (route) => {
    probeRequests += 1;
    await route.fulfill({
      status: 200,
      body: "public test response",
      headers: { "Access-Control-Allow-Origin": "*" },
    });
  });
  await page
    .getByLabel("Coding solution", { exact: true })
    .fill(
      'async function solve(input) { try { await fetch("http://127.0.0.1:3127/dsa-network-probe"); return "connected"; } catch { return "blocked"; } }',
    );
  await page
    .getByRole("button", { name: "Run sample tests", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Runner outputs", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText("blocked", { exact: true }).first(),
  ).toBeVisible();
  expect(probeRequests).toBe(0);
  await page
    .getByLabel("Coding solution", { exact: true })
    .fill("function solve(input) { while (true) {} }");
  await page
    .getByRole("button", { name: "Run sample tests", exact: true })
    .click();
  await expect(page.locator("p[role='alert']")).toContainText(
    "Execution exceeded 3 seconds.",
  );
  await expect(page.locator('iframe[src="/coding-sandbox"]')).toHaveCount(0);
});

test("complete a local learning, interview, career and recovery workflow", async ({
  page,
  request,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Dashboard", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Continue learning" }),
  ).toBeVisible();
  await page
    .getByRole("link", { name: "Learning Tracks", exact: true })
    .click();
  await page.getByLabel("Choose track").selectOption("track-cloud");
  await expect(
    page
      .getByRole("heading", { name: "Cloud Engineering", exact: true })
      .first(),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Create learning plan", exact: true })
    .click();
  await page.getByLabel("Study duration", { exact: true }).selectOption("14");
  await page.getByLabel("Daily study minutes", { exact: true }).fill("180");
  await page.getByRole("button", { name: "Generate study plan" }).click();
  await expect(
    page.getByRole("button", { name: "Study", exact: true }).first(),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Study", exact: true })
    .first()
    .click();
  await page.getByLabel("Video completed", { exact: true }).check();
  await page.getByLabel("Reading completed", { exact: true }).check();
  await page.getByLabel("Practical completed", { exact: true }).check();
  await page.getByLabel("Knowledge check completed", { exact: true }).check();
  await page.getByLabel("Actual minutes watched").fill("20");
  await page.getByLabel("Other actual study minutes").fill("100");
  await page
    .getByLabel("Practical submission evidence")
    .fill("Ran the local failure and recovery tests with repeatable evidence.");
  await page
    .getByLabel("Knowledge-check answers")
    .fill("The identity boundary is enforced before any protected operation.");
  await page.getByRole("button", { name: "Save lesson progress" }).click();
  await expect(page.getByRole("status")).toContainText("Lesson progress saved");
  await page
    .getByLabel("Note title", { exact: true })
    .fill("Browser acceptance notes");
  await page
    .getByLabel("Markdown note", { exact: true })
    .fill("# Evidence\n\nThe local failure test passed.");
  await page.getByRole("button", { name: "Save note", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("Note saved");
  await page
    .getByRole("link", { name: "Interview Preparation", exact: true })
    .click();
  await page.getByRole("button", { name: "Quick random question" }).click();
  await page
    .getByLabel("Your interview answer")
    .fill(
      "I would first establish invariants, measure a baseline and validate the failure boundary.",
    );
  await page.getByRole("button", { name: "Record interview attempt" }).click();
  await expect(page.getByRole("status")).toContainText("Answer recorded");
  await page
    .getByRole("link", { name: "Career Intelligence", exact: true })
    .click();
  await page.getByRole("button", { name: "Add company", exact: true }).click();
  await page.getByLabel("Company name").fill("Acceptance employer");
  await page
    .getByLabel("Career page", { exact: true })
    .fill("https://example.com/careers");
  await page.getByRole("button", { name: "Save", exact: true }).click();
  await expect(
    page.getByText("Acceptance employer · priority 3"),
  ).toBeVisible();
  await page.getByRole("button", { name: "Add job", exact: true }).click();
  const employer = await page
    .getByLabel("Employer", { exact: true })
    .locator("option")
    .filter({ hasText: "Acceptance employer" })
    .getAttribute("value");
  await page.getByLabel("Employer", { exact: true }).selectOption(employer!);
  await page
    .getByLabel("Job title", { exact: true })
    .fill("Senior Python platform engineer");
  await page
    .getByLabel("Job description", { exact: true })
    .fill(
      "Requirements: Python, AWS and Terraform. Own production reliability.",
    );
  await page
    .getByLabel("Confirmed required skills")
    .selectOption(["skill-python", "skill-aws", "skill-iac"]);
  await page.getByRole("button", { name: "Save", exact: true }).click();
  await page
    .getByText("Senior Python platform engineer · saved", { exact: true })
    .click();
  await page
    .getByRole("button", { name: "Analyze skill gaps", exact: true })
    .last()
    .click();
  await expect(
    page.getByRole("heading", {
      name: "Skill gaps: Senior Python platform engineer",
    }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Practical Labs", exact: true }).click();
  await page
    .getByRole("button", { name: "Start project", exact: true })
    .first()
    .click();
  await expect(page.getByRole("status")).toContainText("Project added");
  await page.getByRole("link", { name: "My Projects", exact: true }).click();
  await expect(page.getByRole("checkbox").first()).toBeVisible();
  await page.getByRole("checkbox").first().check();
  await expect(page.getByRole("status")).toContainText("Task saved locally");
  await page.reload();
  await expect(page.getByRole("checkbox").first()).toBeChecked();
  await page
    .getByRole("link", { name: "Notes and Revision", exact: true })
    .click();
  await expect(
    page.getByRole("heading", {
      name: "Browser acceptance notes",
      exact: true,
    }),
  ).toBeVisible();

  const backup = await request.get("/api/data/backup");
  expect(backup.ok()).toBeTruthy();
  const restore = await request.post("/api/data/restore", {
    headers: {
      "X-Academy-Client": "local-workspace",
      "X-Academy-Confirm": "restore",
      "Content-Type": "application/octet-stream",
    },
    data: await backup.body(),
  });
  expect(restore.ok()).toBeTruthy();
  await page.reload();
  await expect(
    page.getByRole("heading", {
      name: "Browser acceptance notes",
      exact: true,
    }),
  ).toBeVisible();
});

test("mobile navigation fits and hostile-host exports are rejected", async ({
  page,
  request,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await expect(
    page.getByRole("button", { name: "Continue learning" }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBeTruthy();
  const rejected = await request.get("/api/data/export", {
    headers: { host: "evil.example:3127" },
  });
  expect(rejected.status()).toBe(403);
});
