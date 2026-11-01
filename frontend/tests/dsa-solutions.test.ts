// @vitest-environment node
import { readFileSync } from "node:fs";
import { runInNewContext } from "node:vm";
import { expect, it } from "vitest";

interface Question {
  id: string;
  title: string;
  solution_code: string;
  test_cases: { input: unknown; output: unknown }[];
}

const { questions } = JSON.parse(
  readFileSync(
    new URL("../../research/dsa/DSA_QUESTION_BANK.json", import.meta.url),
    "utf8",
  ),
) as { questions: Question[] };

// Only committed, Academy-authored references run here, never personal submissions.
it.each(questions)(
  "$id: $title matches its authored fixtures",
  async (question) => {
    for (const fixture of question.test_cases) {
      const result: unknown = await runInNewContext(
        `${question.solution_code}\nsolve(input)`,
        { input: structuredClone(fixture.input) },
        { timeout: 1000 },
      );
      expect(JSON.parse(JSON.stringify(result))).toEqual(fixture.output);
    }
  },
);
