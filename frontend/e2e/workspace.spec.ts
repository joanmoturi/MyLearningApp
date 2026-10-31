import { test, expect } from "@playwright/test";

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
