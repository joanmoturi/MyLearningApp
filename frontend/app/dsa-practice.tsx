"use client";

import { useCallback, useEffect, useState } from "react";
import {
  api,
  catalogue,
  human,
  num,
  obj,
  rows,
  strings,
  text,
  type Row,
} from "../lib/data";
import { runCoding, type CodingRun } from "../lib/coding-runner";
import { Card, Content, Editor, External } from "./components";

const DRAFT_KEYS = [
  "code",
  "clarification",
  "approach",
  "time_complexity",
  "space_complexity",
  "tradeoffs",
];
const MODES = ["pattern", "random", "timed", "company", "mock", "blind"];
const utc = (value: unknown) => Date.parse(text(value).replace(/Z$/, "") + "Z");

export default function DsaPractice({
  aiConfigured,
  onChanged,
}: {
  aiConfigured: boolean;
  onChanged: () => Promise<unknown>;
}) {
  const [overview, setOverview] = useState<Row>({});
  const [questions, setQuestions] = useState<Row[]>([]);
  const [session, setSession] = useState<Row>({});
  const [draft, setDraft] = useState<Row>({});
  const [run, setRun] = useState<CodingRun>({ outputs: [] });
  const [feedback, setFeedback] = useState<Row>({});
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [clock, setClock] = useState(0);
  const [companyId, setCompanyId] = useState("");
  const [topic, setTopic] = useState("");
  const [difficulty, setDifficulty] = useState("");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const refresh = useCallback(async () => {
    setOverview(await api("dsa"));
  }, []);
  useEffect(() => {
    let alive = true;
    void Promise.all([api("dsa"), catalogue("question")])
      .then(([data, bank]) => {
        if (alive) {
          setOverview(data);
          setQuestions(
            rows(bank.items).filter((q) => q.track_id === "track-dsa"),
          );
        }
      })
      .catch((error: unknown) => {
        if (alive)
          setError(
            error instanceof Error ? error.message : "DSA loading failed.",
          );
      });
    return () => {
      alive = false;
    };
  }, []);
  useEffect(() => {
    if (!session.id) return;
    const base = Date.now();
    const server = utc(session.server_now);
    const tick = () => setClock(server + Date.now() - base);
    tick();
    const timer = setInterval(tick, 1000);
    return () => clearInterval(timer);
  }, [session.id, session.server_now]);

  const analytics = obj(overview.analytics);
  const companies = rows(overview.companies);
  const company = companies.find((item) => item.id === companyId);
  const topics = rows(analytics.topics);
  const question = obj(session.question);
  const remaining = Math.max(
    0,
    Math.floor((utc(session.deadline_at) - clock) / 1000),
  );
  const filtered = questions.filter(
    (q) =>
      (!topic || strings(q.skill_ids).includes(topic)) &&
      (!difficulty || q.difficulty === difficulty) &&
      (!search ||
        `${text(q.title)} ${text(q.question)}`
          .toLowerCase()
          .includes(search.toLowerCase())),
  );

  function loadSession(value: Row) {
    setSession(value);
    setDraft(obj(value.draft));
    setRun({ outputs: [] });
    setFeedback(obj(value.feedback));
  }
  async function action(work: () => Promise<void>) {
    setError("");
    setBusy(true);
    try {
      await work();
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Practice operation failed.",
      );
    } finally {
      setBusy(false);
    }
  }
  const draftPayload = () =>
    Object.fromEntries(DRAFT_KEYS.map((key) => [key, text(draft[key])]));
  const updateDraft = (key: string, value: string) => {
    setDraft({ ...draft, [key]: value });
    setRun({ outputs: [] });
  };
  async function startQuestion(id: string) {
    loadSession(
      await api("dsa/sessions", "POST", {
        mode: "blind",
        minutes: 30,
        count: 1,
        question_id: id,
      }),
    );
  }
  async function help(kind: string) {
    await api(`dsa/sessions/${session.id}`, "PATCH", draftPayload());
    const result = await api(`dsa/sessions/${session.id}/help/${kind}`, "POST");
    setSession(result);
    await refresh();
  }

  return (
    <div className="stack">
      <Card
        title="DSA coding interview workspace"
        eyebrow="Sixth learning track"
      >
        <p>
          Original exercises, timed conversations and company research.
          JavaScript runs in an opaque-origin, network-blocked worker; it never
          executes on the backend.
        </p>
        <p className="muted">
          Sample checks are not a complete judge. Pattern and complexity ratings
          are your self-assessment. Code in other languages can be studied or
          tested locally, but this runner executes JavaScript only.
        </p>
        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
        {message && (
          <p className="notice" role="status">
            {message}
          </p>
        )}
        <div className="grid">
          {[
            ["Questions attempted", analytics.questions_attempted],
            ["Questions with passing solved claims", analytics.solved],
            ["Solved independently", analytics.solved_independently],
            ["Attempts using hints", analytics.with_hints],
            ["Attempts viewing solutions", analytics.with_solutions],
          ].map(([label, value]) => (
            <div key={text(label)}>
              <small>{text(label)}</small>
              <div className="metric">{num(value)}</div>
            </div>
          ))}
        </div>
        <Content value={analytics.difficulty} />
        <p>{text(analytics.limitations)}</p>
      </Card>
      <div className="split">
        <div className="stack">
          <Card title="Configure coding practice">
            <Editor
              fields={[
                {
                  name: "mode",
                  label: "DSA practice mode",
                  type: "select",
                  options: MODES.map((value) => ({
                    value,
                    label: human(value),
                  })),
                },
                {
                  name: "minutes",
                  label: "Assessment duration",
                  type: "select",
                  options: [20, 30, 45, 60, 90].map((value) => ({
                    value: String(value),
                    label: `${value} minutes`,
                  })),
                },
                {
                  name: "count",
                  label: "Distinct coding questions",
                  type: "number",
                  min: 1,
                  max: 5,
                },
                {
                  name: "skill_id",
                  label: "Coding pattern",
                  type: "select",
                  options: [
                    { value: "", label: "Any pattern" },
                    ...topics.map((t) => ({
                      value: text(t.skill_id),
                      label: text(t.name),
                    })),
                  ],
                },
                {
                  name: "difficulty",
                  label: "Coding difficulty",
                  type: "select",
                  options: [
                    { value: "", label: "Any difficulty" },
                    ...["easy", "medium", "hard"].map((value) => ({
                      value,
                      label: human(value),
                    })),
                  ],
                },
                {
                  name: "company_profile_id",
                  label: "Researched company",
                  type: "select",
                  options: [
                    { value: "", label: "Select for company mode" },
                    ...companies.map((c) => ({
                      value: text(c.id),
                      label: text(c.name),
                    })),
                  ],
                },
              ]}
              initial={{ mode: "random", minutes: "30", count: 1 }}
              submit="Start coding practice"
              onSave={async (data) => {
                const payload = { ...data, minutes: Number(data.minutes) };
                for (const key of [
                  "skill_id",
                  "difficulty",
                  "company_profile_id",
                ])
                  if (!payload[key as keyof typeof payload])
                    delete (payload as Row)[key];
                loadSession(await api("dsa/sessions", "POST", payload));
                setMessage(
                  "Session and timer saved locally. Save your draft before leaving.",
                );
                await refresh();
              }}
            />
            <button
              disabled={!analytics.next_question_id || busy}
              onClick={() =>
                void action(async () =>
                  startQuestion(text(analytics.next_question_id)),
                )
              }
            >
              Practice recommended next question
            </button>
            {analytics.next_lesson != null && (
              <p>
                Recommended 30-day lesson:{" "}
                {text(obj(analytics.next_lesson).topic)}. Open this topic in My
                Curriculum. This recommendation prioritizes due revisions and
                observed weaknesses, then course prerequisites.
              </p>
            )}
            <p className="muted">
              A 30-minute routine fits alongside another course only when its
              time is reserved in that course&apos;s plan. Dedicated
              14/30/60-day DSA plans are available in My Curriculum; interview
              intensity supports a pre-interview period.
            </p>
          </Card>
          <Card title="Topic performance and revision">
            {topics.map((item) => (
              <div className="row" key={text(item.skill_id)}>
                <div>
                  <strong>{text(item.name)}</strong>
                  <p>
                    {num(item.attempts)} attempts · independent sample-pass
                    rate:{" "}
                    {item.independent_rate == null
                      ? "Not assessed"
                      : `${item.independent_rate}%`}
                  </p>
                  <small>
                    Pattern self-rating:{" "}
                    {item.pattern_self_rating == null
                      ? "Not assessed"
                      : `${item.pattern_self_rating}/5`}{" "}
                    · Complexity self-rating:{" "}
                    {item.complexity_self_rating == null
                      ? "Not assessed"
                      : `${item.complexity_self_rating}/5`}
                  </small>
                </div>
              </div>
            ))}
            {rows(analytics.revision_due).map((revision) => (
              <button
                key={text(revision.id)}
                onClick={() =>
                  void action(async () =>
                    startQuestion(text(revision.question_id)),
                  )
                }
              >
                Revise{" "}
                {text(
                  questions.find((q) => q.id === revision.question_id)?.title,
                )}
              </button>
            ))}
            {!rows(analytics.revision_due).length && (
              <p>No DSA revisions due yet.</p>
            )}
          </Card>
        </div>
        <div className="stack">
          {session.id && (
            <Card
              title={
                question.id ? text(question.title) : "Coding session completed"
              }
            >
              <p role="timer" aria-label="Coding time remaining">
                {Math.floor(remaining / 60)}:
                {String(remaining % 60).padStart(2, "0")} remaining
              </p>
              {remaining === 0 && session.status === "active" && (
                <p className="notice">
                  Time expired. You can preserve and submit your work, but it is
                  recorded as late, not an independent timed success.
                </p>
              )}
              <p>
                {num(session.current_index)} /{" "}
                {strings(session.question_ids).length} submitted
              </p>
              {question.id && (
                <>
                  <p>{text(question.question)}</p>
                  <small>
                    {text(question.difficulty)}{" "}
                    {question.pattern
                      ? `· ${text(question.pattern)}`
                      : "· Blind practice"}
                  </small>
                  <Content value={question.constraints} />
                  <details>
                    <summary>Input/output fixtures</summary>
                    <Content value={question.test_cases} />
                  </details>
                  {DRAFT_KEYS.filter((key) => key !== "code").map((key) => (
                    <label key={key}>
                      <span>{human(key)}</span>
                      <textarea
                        disabled={busy}
                        aria-label={`Coding ${human(key)}`}
                        value={text(draft[key])}
                        onChange={(event) =>
                          updateDraft(key, event.target.value)
                        }
                      />
                    </label>
                  ))}
                  <label>
                    <span>JavaScript solution: implement solve(input)</span>
                    <textarea
                      disabled={busy}
                      aria-label="Coding solution"
                      rows={14}
                      spellCheck={false}
                      value={text(draft.code)}
                      onChange={(event) =>
                        updateDraft("code", event.target.value)
                      }
                    />
                  </label>
                  <div className="actions">
                    <button
                      disabled={busy}
                      onClick={() =>
                        void action(async () => {
                          await api(
                            `dsa/sessions/${session.id}`,
                            "PATCH",
                            draftPayload(),
                          );
                          setMessage(
                            "Coding draft saved. Resume this session after reload.",
                          );
                        })
                      }
                    >
                      Save coding draft
                    </button>
                    <button
                      disabled={busy}
                      onClick={() =>
                        void action(async () =>
                          setRun(
                            await runCoding(
                              text(draft.code),
                              question.test_cases,
                            ),
                          ),
                        )
                      }
                    >
                      Run sample tests
                    </button>
                    <button
                      disabled={busy}
                      onClick={() => void action(async () => help("hint"))}
                    >
                      Request hint
                    </button>
                    <button
                      disabled={busy}
                      onClick={() => void action(async () => help("solution"))}
                    >
                      Reveal solution
                    </button>
                  </div>
                  {run.error && (
                    <p className="error" role="alert">
                      {run.error}
                    </p>
                  )}
                  {run.outputs.length > 0 && (
                    <>
                      <h3>Runner outputs</h3>
                      <Content value={run.outputs} />
                    </>
                  )}
                  {question.hints != null && (
                    <>
                      <h3>Requested hints</h3>
                      <Content value={question.hints} />
                    </>
                  )}
                  {question.solution_code != null && (
                    <details open>
                      <summary>Requested reference solution</summary>
                      <pre>{text(question.solution_code)}</pre>
                      <Content value={question.detailed_explanation} />
                      <Content value={question.complexity} />
                    </details>
                  )}
                  <details>
                    <summary>Self-assessment rubric</summary>
                    <Content value={question.evaluation_rubric} />
                  </details>
                  <Editor
                    key={`coding-submit-${question.id}`}
                    fields={[
                      {
                        name: "solved",
                        label: "I solved the problem",
                        type: "checkbox",
                      },
                      ...strings(overview.dimensions).map((name) => ({
                        name,
                        label: `${human(name)} self-rating (0-5)`,
                        type: "number" as const,
                        min: 0,
                        max: 5,
                        required: true,
                      })),
                    ]}
                    submit="Submit coding answer"
                    initial={Object.fromEntries(
                      strings(overview.dimensions).map((name) => [name, 0]),
                    )}
                    onSave={async (data) => {
                      const result = await api(
                        `dsa/sessions/${session.id}/submit`,
                        "POST",
                        {
                          ...draftPayload(),
                          question_id: question.id,
                          solved: Boolean(data.solved),
                          outputs: run.outputs,
                          ratings: Object.fromEntries(
                            strings(overview.dimensions).map((key) => [
                              key,
                              Number(data[key]),
                            ]),
                          ),
                          elapsed_seconds: Math.max(
                            0,
                            Math.floor(
                              (clock - utc(session.started_at)) / 1000,
                            ),
                          ),
                        },
                      );
                      loadSession(result);
                      await refresh();
                      await onChanged();
                      setMessage(
                        "Submission recorded; assistance and failed checks schedule revision.",
                      );
                    }}
                  />
                  {aiConfigured && (
                    <details>
                      <summary>Optional AI feedback (may incur costs)</summary>
                      <Editor
                        fields={[
                          {
                            name: "consent",
                            label:
                              "I consent to sending this code and explanation to the configured AI provider",
                            type: "checkbox",
                          },
                        ]}
                        submit="Request coding feedback"
                        onSave={async (data) =>
                          setFeedback(
                            await api("interviews/evaluate", "POST", {
                              question_id: question.id,
                              consent: Boolean(data.consent),
                              answer: `${text(draft.approach)}\n${text(draft.code)}\nTime: ${text(draft.time_complexity)}\nSpace: ${text(draft.space_complexity)}`,
                            }),
                          )
                        }
                      />
                    </details>
                  )}
                </>
              )}
              {Object.keys(feedback).length > 0 && (
                <>
                  <h3>Recorded feedback</h3>
                  <Content value={feedback} />
                </>
              )}
              {rows(session.submissions).map((submission, index) => {
                const answer = obj(submission.answer);
                const savedQuestion = questions.find(
                  (q) => q.id === answer.question_id,
                );
                return (
                  <details key={text(answer.question_id)}>
                    <summary>
                      Saved answer {index + 1}: {text(savedQuestion?.title)}
                    </summary>
                    <p>
                      Submitted {text(submission.submitted_at)} UTC ·{" "}
                      {num(answer.elapsed_seconds)} seconds wall-clock ·{" "}
                      {submission.late ? "Late" : "On time"} ·{" "}
                      {submission.hint_used || submission.solution_used
                        ? "Assisted"
                        : "No requested help"}
                    </p>
                    <p>
                      State:{" "}
                      {human(
                        text(obj(analytics.states)[text(answer.question_id)]),
                      )}
                    </p>
                    <Content
                      value={{
                        clarification: answer.clarification,
                        approach: answer.approach,
                        time_complexity: answer.time_complexity,
                        space_complexity: answer.space_complexity,
                        tradeoffs: answer.tradeoffs,
                      }}
                    />
                    <pre>{text(answer.code)}</pre>
                    <h4>Stored sample checks and self-ratings</h4>
                    <Content value={submission.sample_checks} />
                    <Content value={answer.ratings} />
                    <details>
                      <summary>
                        Review explanation, mistakes and follow-ups
                      </summary>
                      <Content value={savedQuestion?.detailed_explanation} />
                      <Content value={savedQuestion?.complexity} />
                      <Content value={savedQuestion?.common_mistakes} />
                      <Content value={savedQuestion?.follow_up_questions} />
                    </details>
                    <button
                      disabled={busy}
                      onClick={() =>
                        void action(async () => {
                          setSession(
                            await api(
                              `dsa/sessions/${session.id}/revision/${answer.question_id}`,
                              "POST",
                            ),
                          );
                          await refresh();
                          await onChanged();
                          setMessage(
                            "Question marked needs revision; its existing attempt is preserved.",
                          );
                        })
                      }
                    >
                      Mark needs revision
                    </button>
                  </details>
                );
              })}
            </Card>
          )}
          <Card title="Saved coding sessions">
            {!rows(analytics.history).length && (
              <p>
                No sessions yet. Starting or viewing a solution does not count
                as a solved problem.
              </p>
            )}
            {rows(analytics.history).map((item) => (
              <div key={text(item.id)} className="row">
                <div>
                  {human(text(obj(item.config).mode))} · {text(item.status)} ·{" "}
                  {num(item.current_index)} submissions
                </div>
                <button
                  disabled={busy}
                  onClick={() =>
                    void action(async () =>
                      loadSession(await api(`dsa/sessions/${item.id}`)),
                    )
                  }
                >
                  Resume or inspect session
                </button>
              </div>
            ))}
            <p>
              Mastery is earned through independent successes on three separate
              dates, not selected from a dropdown.
            </p>
          </Card>
        </div>
      </div>
      <Card title="Company-specific preparation research">
        <label>
          <span>Company preparation profile</span>
          <select
            aria-label="Company preparation profile"
            value={companyId}
            onChange={(event) => setCompanyId(event.target.value)}
          >
            <option value="">Choose a company</option>
            {companies.map((c) => (
              <option key={text(c.id)} value={text(c.id)}>
                {text(c.name)}
              </option>
            ))}
          </select>
        </label>
        {company && (
          <>
            <h3>
              {text(company.name)} · Preparation tier{" "}
              {num(company.preparation_tier)}
            </h3>
            <p>
              {human(text(company.interview_evidence))} ·{" "}
              {text(company.confidence)} confidence · Researched{" "}
              {text(company.research_date)}
            </p>
            <External url={company.career_url}>Official careers</External>
            <Content value={company.coding_assessment_format} />
            <Content value={company.relevant_job_titles} />
            <p>{text(company.job_title_status)}</p>
            <h4>Location and remote eligibility</h4>
            <Content value={company.location_eligibility} />
            <h4>System design and practical coding</h4>
            <Content value={company.system_design_expectations} />
            <Content value={company.practical_coding_expectations} />
            <h4>Behavioral and role preparation</h4>
            <Content value={company.behavioral_requirements} />
            <Content value={company.role_specific_requirements} />
            <Content value={company.main_dsa_topics} />
            <Content value={company.candidate_report_scope} />
            <Content value={company.limitations} />
            {strings(company.source_urls).map((url) => (
              <p key={url}>
                <External url={url}>Research source</External>
              </p>
            ))}
            <div className="actions">
              <button
                disabled={busy}
                onClick={() =>
                  void action(async () =>
                    loadSession(
                      await api("dsa/sessions", "POST", {
                        mode: "company",
                        minutes: 45,
                        count: 1,
                        company_profile_id: company.id,
                      }),
                    ),
                  )
                }
              >
                Start researched company practice
              </button>
              <Editor
                fields={[
                  {
                    name: "duration_days",
                    label: "Company DSA plan length",
                    type: "select",
                    options: [14, 30, 60].map((n) => ({
                      value: String(n),
                      label: `${n} days`,
                    })),
                  },
                ]}
                initial={{ duration_days: "30" }}
                submit="Create company DSA plan"
                onSave={async (data) => {
                  await api("plans", "POST", {
                    track_id: "track-dsa",
                    duration_days: Number(data.duration_days),
                    daily_minutes: 210,
                    target_role: `${text(company.name)} coding preparation`,
                    priority_skill_ids: strings(company.pattern_skill_ids),
                  });
                  await onChanged();
                  setMessage(
                    "Company DSA plan saved; sourced priorities are highlighted without violating prerequisites.",
                  );
                }}
              />
            </div>
            <p className="muted">
              An unknown interview process produces balanced generic practice,
              not invented company questions. Edit watchlist priorities and
              notes in Career Intelligence; update profile research through
              Settings imports.
            </p>
          </>
        )}
      </Card>
      <Card title={`DSA coding question bank (${filtered.length} matches)`}>
        <div className="filters">
          <label>
            Search original exercises
            <input
              aria-label="Search coding questions"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(0);
              }}
            />
          </label>
          <label>
            Pattern
            <select
              aria-label="Filter coding pattern"
              value={topic}
              onChange={(e) => {
                setTopic(e.target.value);
                setPage(0);
              }}
            >
              <option value="">All patterns</option>
              {topics.map((t) => (
                <option key={text(t.skill_id)} value={text(t.skill_id)}>
                  {text(t.name)}
                </option>
              ))}
            </select>
          </label>
          <label>
            Difficulty
            <select
              aria-label="Filter coding difficulty"
              value={difficulty}
              onChange={(e) => {
                setDifficulty(e.target.value);
                setPage(0);
              }}
            >
              <option value="">All difficulties</option>
              {["easy", "medium", "hard"].map((d) => (
                <option key={d}>{d}</option>
              ))}
            </select>
          </label>
        </div>
        {filtered.slice(page * 10, page * 10 + 10).map((q) => (
          <div className="row" key={text(q.id)}>
            <div>
              <small>
                {text(q.difficulty)} · {text(q.pattern)} ·{" "}
                {human(text(obj(analytics.states)[text(q.id)]))}
              </small>
              <p>{text(q.title)}</p>
            </div>
            <button
              disabled={busy}
              onClick={() => void action(async () => startQuestion(text(q.id)))}
            >
              Practice coding question
            </button>
          </div>
        ))}
        <div className="actions">
          <button disabled={!page} onClick={() => setPage(page - 1)}>
            Previous coding page
          </button>
          <span>Page {page + 1}</span>
          <button
            disabled={(page + 1) * 10 >= filtered.length}
            onClick={() => setPage(page + 1)}
          >
            Next coding page
          </button>
        </div>
      </Card>
    </div>
  );
}
