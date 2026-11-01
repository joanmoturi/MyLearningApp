"use client";

import { useCallback, useEffect, useState } from "react";
import Markdown from "react-markdown";
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
import { Card, Content, Editor, External, type Field } from "./components";
import DsaPractice from "./dsa-practice";

const sections = [
  "Dashboard",
  "Learning Tracks",
  "My Curriculum",
  "Study Room",
  "Resource Library",
  "Practical Labs",
  "Interview Preparation",
  "Career Intelligence",
  "My Projects",
  "Notes and Revision",
  "Settings",
];
const slug = (title: string) => title.toLowerCase().replaceAll(" ", "-");
const levels = [
  "Not assessed",
  "Unfamiliar",
  "Learning",
  "Basic understanding",
  "Can implement independently",
  "Can troubleshoot in production",
  "Can defend trade-offs",
];
const choices = (values: string[]) =>
  values.map((value) => ({ value, label: human(value) }));
const options = (values: Row[]) =>
  values.map((value) => ({
    value: text(value.id),
    label: text(value.title ?? value.name ?? value.scenario ?? value.id),
  }));
const selected = (data: Row, keys: string[]) =>
  Object.fromEntries(
    keys
      .filter((key) => data[key] !== undefined)
      .map((key) => [key, data[key]]),
  );
const personalKinds = [
  "note",
  "resource",
  "competency",
  "company",
  "job",
  "project",
  "attempt",
  "review",
];

export default function Workspace() {
  const [section, setSection] = useState("Dashboard");
  const [boot, setBoot] = useState<Row>({});
  const [dashboard, setDashboard] = useState<Row>({});
  const [plans, setPlans] = useState<Row[]>([]);
  const [catalog, setCatalog] = useState<Record<string, Row[]>>({});
  const [personal, setPersonal] = useState<Record<string, Row[]>>({});
  const [trackId, setTrackId] = useState("track-swe");
  const [plan, setPlan] = useState<Row>({});
  const [lesson, setLesson] = useState<Row>({});
  const [editing, setEditing] = useState<Row | null>(null);
  const [question, setQuestion] = useState<Row>({});
  const [mockQueue, setMockQueue] = useState<string[]>([]);
  const [gaps, setGaps] = useState<Row>({});
  const [targetJob, setTargetJob] = useState<Row>({});
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [ready, setReady] = useState(false);
  const [epoch, setEpoch] = useState(0);
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [preview, setPreview] = useState<Row>({});
  const [importKind, setImportKind] = useState("research");
  const [integrationResult, setIntegrationResult] = useState<Row>({});

  const reload = useCallback(async () => {
    const [bootstrap, home, allPlans, ...records] = await Promise.all([
      api("bootstrap"),
      api("dashboard"),
      api<Row[]>("plans"),
      ...personalKinds.map((kind) => api<Row[]>(`personal/${kind}`)),
    ]);
    setBoot(bootstrap);
    setDashboard(home);
    setPlans(allPlans);
    setPersonal(
      Object.fromEntries(
        personalKinds.map((kind, index) => [kind, records[index]]),
      ),
    );
    const prefs = obj(bootstrap.settings);
    const theme = text(prefs.theme);
    document.documentElement.dataset.theme =
      theme === "system"
        ? matchMedia("(prefers-color-scheme: light)").matches
          ? "light"
          : "dark"
        : theme;
    setEpoch((value) => value + 1);
    return bootstrap;
  }, []);

  useEffect(() => {
    let alive = true;
    async function start() {
      try {
        const [bootstrap, ...data] = await Promise.all([
          reload(),
          ...["resource", "question", "project", "mock"].map((kind) =>
            catalogue(kind),
          ),
        ]);
        if (!alive) return;
        setCatalog(
          Object.fromEntries(
            ["resource", "question", "project", "mock"].map((kind, index) => [
              kind,
              rows(data[index].items),
            ]),
          ),
        );
        setTrackId(text(obj(bootstrap.settings).active_track_id));
        const route = decodeURIComponent(window.location.hash.slice(1));
        setSection(
          sections.find((title) => slug(title) === route) ?? "Dashboard",
        );
        setReady(true);
      } catch (error) {
        if (alive)
          setError(error instanceof Error ? error.message : "Startup failed");
      }
    }
    void start();
    const navigate = () =>
      setSection(
        sections.find(
          (title) => slug(title) === window.location.hash.slice(1),
        ) ?? "Dashboard",
      );
    window.addEventListener("hashchange", navigate);
    return () => {
      alive = false;
      window.removeEventListener("hashchange", navigate);
    };
  }, [reload]);

  function go(title: string) {
    setSection(title);
    setEditing(null);
    setFilters({});
    window.history.replaceState(null, "", `#${slug(title)}`);
  }
  async function run(
    action: () => Promise<unknown>,
    message = "Saved locally.",
  ) {
    setError("");
    try {
      await action();
      await reload();
      setNotice(message);
    } catch (error) {
      setError(error instanceof Error ? error.message : "Operation failed");
    }
  }
  async function openLesson(id: string) {
    await run(async () => {
      setLesson(await api(`lessons/${id}`));
      go("Study Room");
    }, "Opening a lesson does not mark it complete.");
  }
  async function openPlan(id: string) {
    await run(async () => {
      setPlan(await api(`plans/${id}`));
      go("My Curriculum");
    }, "Plan loaded.");
  }
  const priorityOrder = strings(obj(boot.settings).priorities);
  const tracks = rows(boot.tracks).sort((a, b) => {
    const rank = (item: Row) =>
      priorityOrder.includes(text(item.id))
        ? priorityOrder.indexOf(text(item.id))
        : priorityOrder.length + num(item.priority);
    return rank(a) - rank(b);
  });
  const skills = rows(boot.skills);
  const track = tracks.find((item) => item.id === trackId) ?? {};
  const prefs = obj(boot.settings);
  const nameOf = (id: unknown) =>
    text(tracks.find((item) => item.id === id)?.name ?? id);
  const skillName = (id: unknown) =>
    text(skills.find((item) => item.id === id)?.name ?? id);
  const filter = (
    key: string,
    label: string,
    values?: { value: string; label: string }[],
    type = "text",
  ) => (
    <label>
      <span className="muted">{label}</span>
      {values ? (
        <select
          aria-label={label}
          value={filters[key] ?? ""}
          onChange={(event) =>
            setFilters({ ...filters, [key]: event.target.value })
          }
        >
          <option value="">All</option>
          {values.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      ) : (
        <input
          aria-label={label}
          type={type}
          value={filters[key] ?? ""}
          onChange={(event) =>
            setFilters({ ...filters, [key]: event.target.value })
          }
        />
      )}
    </label>
  );
  const trackFilter = () => filter("track", "Track filter", options(tracks));
  const planFields: Field[] = [
    {
      name: "track_id",
      label: "Learning track",
      type: "select",
      options: options(tracks),
      required: true,
    },
    { name: "target_role", label: "Target role", required: true },
    {
      name: "duration_days",
      label: "Study duration",
      type: "select",
      options: [14, 30, 60].map((value) => ({
        value: String(value),
        label: `${value} days`,
      })),
      required: true,
    },
    {
      name: "daily_minutes",
      label: "Daily study minutes",
      type: "number",
      min: 180,
      max: 240,
      required: true,
    },
    {
      name: "intensity",
      label: "Learning intensity",
      type: "select",
      options: choices(["balanced", "practical", "interview"]),
    },
    {
      name: "dsa_practice_minutes",
      label: "DSA routine within daily budget",
      type: "select",
      options: [
        { value: "0", label: "No companion routine / dedicated DSA plan" },
        {
          value: "30",
          label: "Reserve 30 minutes alongside this non-DSA track",
        },
        {
          value: "45",
          label: "Reserve 45 minutes alongside this non-DSA track",
        },
      ],
      hint: "Reserved from implementation time, not added to your daily total.",
    },
    {
      name: "existing_competency",
      label: "Existing competency context",
      hint: "Context only. Advanced competency requires separate practical evidence.",
    },
    {
      name: "priority_skill_ids",
      label: "Priority skills",
      type: "multi",
      options: options(skills),
    },
    {
      name: "company_id",
      label: "Target company",
      type: "select",
      options: options(personal.company ?? []),
    },
    {
      name: "job_id",
      label: "Target job",
      type: "select",
      options: options(personal.job ?? []),
    },
    {
      name: "reuse_demonstrated",
      label: "Waive demonstrated conceptual skills",
      type: "checkbox",
      hint: "Only independently evidenced competencies qualify; skipped lessons are not completed.",
    },
  ];
  async function savePlan(data: Row) {
    const payload = {
      ...data,
      duration_days: Number(data.duration_days),
      dsa_practice_minutes: Number(data.dsa_practice_minutes ?? 0),
      company_id: data.company_id || null,
      job_id: data.job_id || null,
    };
    const saved = await api(
      editing?.kind === "plan" ? `plans/${editing.id}` : "plans",
      editing?.kind === "plan" ? "PATCH" : "POST",
      selected(
        payload,
        planFields.map((field) => field.name),
      ),
    );
    setPlan(saved);
    setEditing(null);
    await reload();
    go("My Curriculum");
  }
  async function activate(id: string) {
    const existing = plans.find((item) => item.track_id === id);
    await run(async () => {
      if (existing) await api(`plans/${existing.id}/status/activate`, "POST");
      else
        await api("settings", "PATCH", {
          ...prefs,
          active_track_id: id,
          active_plan_id: null,
        });
      setTrackId(id);
    }, "Active track changed. Existing progress is preserved.");
  }
  const noteFields: Field[] = [
    { name: "title", label: "Note title", required: true },
    { name: "body", label: "Markdown note", type: "textarea" },
  ];
  function noteForm(targetType = "general", targetId: string | null = null) {
    return (
      <Editor
        key={`note-${editing?.id ?? targetId}-${epoch}`}
        fields={noteFields}
        initial={editing?.kind === "note" ? editing : { title: "", body: "" }}
        submit={editing?.kind === "note" ? "Update note" : "Save note"}
        onSave={async (data) => {
          await api(
            `personal/note${editing?.kind === "note" ? "/" + editing.id : ""}`,
            editing?.kind === "note" ? "PATCH" : "POST",
            {
              ...selected(data, ["title", "body"]),
              target_type: editing?.target_type ?? targetType,
              target_id: editing?.target_id ?? targetId,
            },
          );
          setEditing(null);
          await reload();
          setNotice("Note saved locally.");
        }}
      />
    );
  }
  function renderResource(resource: Row) {
    const pref =
      (personal.resource ?? []).find(
        (item) => item.research_ref === resource.id,
      ) ?? {};
    const metadata = text(resource.last_verified_at).slice(0, 10);
    return (
      <Card
        key={resource.id}
        title={text(resource.title)}
        eyebrow={human(text(resource.resource_type))}
      >
        <p className="muted">
          {text(resource.creator ?? resource.provider)} ·{" "}
          {resource.duration_minutes == null
            ? "Duration unavailable"
            : `${resource.duration_minutes} min`}
        </p>
        <p>
          <span className="pill">{human(text(resource.free_status))}</span>
          <span className="pill">
            Research score {text(resource.overall_score)}/100
          </span>
          <span className="pill">{text(resource.confidence)} confidence</span>
        </p>
        <p className="muted">
          Evidence checked {metadata || "date unavailable"}.{" "}
          <strong>
            {pref.flag && pref.flag !== "none"
              ? human(text(pref.flag))
              : "Needs current verification"}
          </strong>
        </p>
        <External url={resource.url}>Open original resource</External>
        <details>
          <summary>Quality, selection and limitations</summary>
          <Content value={resource.score_breakdown ?? resource.evaluation} />
          <Content value={resource.selection_reason} />
          <Content value={resource.limitations} />
          <p>
            <strong>Community feedback</strong>
          </p>
          <Content value={resource.community_feedback_summary} />
          <p>
            Views:{" "}
            {resource.view_count == null
              ? "unavailable"
              : text(resource.view_count)}{" "}
            · Likes:{" "}
            {resource.like_count == null
              ? "unavailable"
              : text(resource.like_count)}{" "}
            · Comments:{" "}
            {resource.comment_count == null
              ? "unavailable"
              : text(resource.comment_count)}
          </p>
          <p>{strings(resource.skill_ids).map(skillName).join(", ")}</p>
        </details>
        <div className="actions">
          <button
            onClick={() =>
              void run(() =>
                api(`resources/${resource.id}/personal`, "PATCH", {
                  ...selected(pref, [
                    "bookmarked",
                    "completed",
                    "rating",
                    "flag",
                  ]),
                  bookmarked: !pref.bookmarked,
                }),
              )
            }
          >
            {pref.bookmarked ? "Remove bookmark" : "Bookmark"}
          </button>
          <button
            onClick={() => {
              setEditing({ kind: "resource", ...resource });
            }}
          >
            Personal rating / notes
          </button>
          <button
            disabled={!obj(boot.integrations).youtube_configured}
            onClick={() =>
              void run(
                async () =>
                  setIntegrationResult(
                    await api(`resources/${resource.id}/metadata`, "POST"),
                  ),
                "Metadata refreshed through the official API; research scores are unchanged.",
              )
            }
          >
            Refresh metadata
          </button>
          <button
            onClick={() =>
              void run(
                async () =>
                  setIntegrationResult(
                    await api(`resources/${resource.id}/metadata`),
                  ),
                "Cached provider metadata loaded; the stale flag is explicit.",
              )
            }
          >
            View cached metadata
          </button>
        </div>
        {editing?.kind === "resource" && editing.id === resource.id && (
          <div className="stack">
            <Editor
              fields={[
                {
                  name: "rating",
                  label: "Your rating (1–5)",
                  type: "number",
                  min: 1,
                  max: 5,
                },
                {
                  name: "completed",
                  label: "Resource completed",
                  type: "checkbox",
                },
                {
                  name: "flag",
                  label: "Verification flag",
                  type: "select",
                  options: choices([
                    "none",
                    "needs_verification",
                    "broken_link",
                    "outdated",
                    "unavailable_metadata",
                  ]),
                },
              ]}
              initial={{
                rating: pref.rating ?? "",
                completed: pref.completed ?? false,
                flag: pref.flag ?? "needs_verification",
              }}
              onSave={async (data) => {
                await api(`resources/${resource.id}/personal`, "PATCH", {
                  bookmarked: Boolean(pref.bookmarked),
                  ...data,
                  rating: data.rating === "" ? null : data.rating,
                });
                await reload();
                setNotice("Personal rating saved separately from research.");
              }}
            />
            {noteForm("resource", text(resource.id))}
          </div>
        )}
      </Card>
    );
  }
  function empty(values: Row[], label: string) {
    return values.length === 0 ? <p className="empty">{label}</p> : null;
  }
  const questionList = (catalog.question ?? []).filter(
    (item) =>
      (!filters.track || item.track_id === filters.track) &&
      (!filters.difficulty || item.difficulty === filters.difficulty) &&
      (!filters.category || item.category === filters.category) &&
      (!filters.skill || strings(item.skill_ids).includes(filters.skill)) &&
      (!filters.q ||
        JSON.stringify(item).toLowerCase().includes(filters.q.toLowerCase())),
  );
  async function startMock(id: string) {
    const mock = (catalog.mock ?? []).find((item) => item.id === id) ?? {};
    const ids = strings(mock.question_ids);
    setMockQueue(ids.slice(1));
    setQuestion(
      (catalog.question ?? []).find((item) => item.id === ids[0]) ?? {},
    );
    setIntegrationResult({});
  }
  const companyFields: Field[] = [
    { name: "name", label: "Company name", required: true },
    { name: "website", label: "Website", type: "url" },
    { name: "career_url", label: "Career page", type: "url" },
    { name: "location", label: "Company location" },
    { name: "arrangement", label: "Preferred work arrangement" },
    { name: "target_roles", label: "Target roles" },
    {
      name: "priority",
      label: "Company priority",
      type: "number",
      min: 1,
      max: 5,
    },
    { name: "notes", label: "Company research notes", type: "textarea" },
    { name: "enabled", label: "Watchlist enabled", type: "checkbox" },
  ];
  const jobFields: Field[] = [
    {
      name: "company_id",
      label: "Employer",
      type: "select",
      options: options(personal.company ?? []),
      required: true,
    },
    { name: "title", label: "Job title", required: true },
    { name: "url", label: "Original job URL", type: "url" },
    {
      name: "description",
      label: "Job description",
      type: "textarea",
      required: true,
    },
    { name: "location", label: "Job location" },
    { name: "employment_type", label: "Employment type" },
    { name: "required_experience", label: "Required experience" },
    {
      name: "required_skill_ids",
      label: "Confirmed required skills",
      type: "multi",
      options: options(skills),
    },
    {
      name: "preferred_skill_ids",
      label: "Confirmed preferred skills",
      type: "multi",
      options: options(skills),
    },
    { name: "deadline", label: "Application deadline", type: "date" },
    {
      name: "application_status",
      label: "Application status",
      type: "select",
      options: choices([
        "researching",
        "saved",
        "applied",
        "interviewing",
        "offer",
        "rejected",
        "closed",
      ]),
    },
    { name: "notes", label: "Preparation notes", type: "textarea" },
    {
      name: "interview_feedback",
      label: "Interview feedback",
      type: "textarea",
    },
  ];
  const projectFields: Field[] = [
    { name: "title", label: "Project title", required: true },
    {
      name: "track_ids",
      label: "Related learning tracks",
      type: "multi",
      options: options(tracks),
      required: true,
    },
    {
      name: "skill_ids",
      label: "Project skills",
      type: "multi",
      options: options(skills),
    },
    ...["overview", "architecture", "requirements", "testing_checklist"].map(
      (name) => ({ name, label: human(name), type: "textarea" as const }),
    ),
    { name: "github_url", label: "GitHub repository", type: "url" },
    { name: "deployment_url", label: "Deployment URL", type: "url" },
    {
      name: "status",
      label: "Project status",
      type: "select",
      options: choices(["not_started", "active", "paused", "completed"]),
    },
  ];
  async function toggleTask(item: Row, task: Row, completed: boolean) {
    const previous = personal.project;
    const tasks = rows(item.tasks).map((existing) =>
      existing.id === task.id ? { ...existing, completed } : existing,
    );
    setPersonal((current) => ({
      ...current,
      project: (current.project ?? []).map((project) =>
        project.id === item.id ? { ...project, tasks } : project,
      ),
    }));
    try {
      await api(`personal/project/${item.id}`, "PATCH", {
        ...selected(
          item,
          projectFields.map((field) => field.name),
        ),
        tasks,
      });
      await reload();
      setNotice("Task saved locally.");
    } catch (error) {
      setPersonal((current) => ({ ...current, project: previous }));
      setError(error instanceof Error ? error.message : "Task save failed.");
    }
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <small>Build. Understand. Advance.</small>Engineering Academy
        </div>
        <nav aria-label="Main navigation">
          {sections.map((title) => (
            <a
              key={title}
              href={`#${slug(title)}`}
              className={section === title ? "active" : ""}
              aria-current={section === title ? "page" : undefined}
              onClick={() => go(title)}
            >
              {title}
            </a>
          ))}
        </nav>
        <p className="local">
          LOCAL WORKSPACE
          <br />
          Your progress stays on this device.
          <br />
          External resources open separately.
        </p>
      </aside>
      <main>
        <div className="topline">
          <span>Engineering career accelerator</span>
          <span>Local-first / Evidence-led</span>
        </div>
        <p className="eyebrow">
          {nameOf(prefs.active_track_id) || "Your engineering workspace"}
        </p>
        <h1>{section}</h1>
        {error && (
          <div role="alert" className="error">
            {error}
            <button onClick={() => window.location.reload()}>Retry</button>
          </div>
        )}
        {notice && (
          <div role="status" className="notice">
            {notice}
            <button
              onClick={() => setNotice("")}
              aria-label="Dismiss notification"
            >
              ×
            </button>
          </div>
        )}
        {strings(boot.research_issues).length > 0 && (
          <p className="notice">
            Missing research: {strings(boot.research_issues).join(", ")}. No
            replacement research has been fabricated.
          </p>
        )}
        {!ready ? (
          <p className="empty">
            Loading your local research and learning workspace…
          </p>
        ) : (
          <>
            {section === "Dashboard" && (
              <>
                <p className="lead">
                  Build production judgment, not just familiarity. Continue your
                  next lesson, capture evidence, and turn practical work into a
                  portfolio.
                </p>
                <div className="card hero">
                  <p className="eyebrow">Your next useful action</p>
                  <h2>
                    {text(rows(dashboard.upcoming)[0]?.topic) ||
                      "Choose a track and create a learning plan"}
                  </h2>
                  <p className="muted">
                    {rows(dashboard.upcoming).length
                      ? `Day ${rows(dashboard.upcoming)[0].day} / ${text(rows(dashboard.upcoming)[0].estimated_total_study_minutes)} minutes / ${human(text(obj(rows(dashboard.upcoming)[0].progress).status))}`
                      : "All learning tracks remain accessible. Your existing work is preserved."}
                  </p>
                  <button
                    className="primary"
                    onClick={() =>
                      rows(dashboard.upcoming)[0]?.id
                        ? void openLesson(text(rows(dashboard.upcoming)[0].id))
                        : go("My Curriculum")
                    }
                  >
                    Continue learning
                  </button>
                </div>
                <div className="grid">
                  {[
                    ["Hours studied", dashboard.hours_studied],
                    ["Completed lessons", dashboard.completed_lessons],
                    [
                      "Learning streak",
                      `${num(dashboard.learning_streak)} days`,
                    ],
                    ["Outstanding exercises", dashboard.outstanding_exercises],
                  ].map(([label, value]) => (
                    <Card key={text(label)} title={text(label)}>
                      <div className="metric">{text(value)}</div>
                    </Card>
                  ))}
                </div>
                <h2>Your learning tracks</h2>
                <div className="grid">
                  {tracks.map((item) => {
                    const list = plans.filter(
                      (plan) => plan.track_id === item.id,
                    );
                    const count = list.reduce(
                      (total, plan) => total + num(plan.completed_count),
                      0,
                    );
                    const total = list.reduce(
                      (total, plan) => total + num(plan.lesson_count),
                      0,
                    );
                    return (
                      <Card
                        key={item.id}
                        title={text(item.name)}
                        eyebrow={
                          item.id === prefs.active_track_id
                            ? "Active track"
                            : "Available track"
                        }
                      >
                        <progress
                          aria-label={`${text(item.name)} progress`}
                          max={total || 1}
                          value={count}
                        />
                        <p className="muted">
                          {count} / {total} lesson instances complete
                        </p>
                        <div className="actions">
                          <button onClick={() => void activate(text(item.id))}>
                            Activate
                          </button>
                          <button
                            onClick={() => {
                              setTrackId(text(item.id));
                              go("Learning Tracks");
                            }}
                          >
                            Explore track
                          </button>
                        </div>
                      </Card>
                    );
                  })}
                </div>
                <div className="split">
                  <Card title="Upcoming lessons">
                    {rows(dashboard.upcoming).map((item) => (
                      <div className="row" key={item.id}>
                        <div>
                          <small>Day {text(item.day)}</small>
                          <p>{text(item.topic)}</p>
                        </div>
                        <button onClick={() => void openLesson(text(item.id))}>
                          Study
                        </button>
                      </div>
                    ))}
                  </Card>
                  <Card title="Interview readiness">
                    <p className="muted">
                      Self-rubric averages, not hiring predictions.
                    </p>
                    {rows(dashboard.interview_readiness).map((item) => (
                      <p key={text(item.track_id)}>
                        {nameOf(item.track_id)}:{" "}
                        {item.self_rubric_average == null
                          ? "Not assessed"
                          : `${item.self_rubric_average}/10 across ${item.attempts} attempts`}
                      </p>
                    ))}
                  </Card>
                </div>
                <div className="grid">
                  <Card title="Weak areas">
                    <Content
                      value={rows(dashboard.weak_areas).map(
                        (item) =>
                          `${skillName(item.research_ref)}: ${levels[num(item.level)]}`,
                      )}
                    />
                  </Card>
                  <Card title="Due revision">
                    <p>{rows(dashboard.revision_due).length} questions due</p>
                    <button onClick={() => go("Notes and Revision")}>
                      Open revision queue
                    </button>
                  </Card>
                  <Card title="Active projects">
                    {rows(dashboard.active_projects).map((item) => (
                      <p key={item.id}>{text(item.title)}</p>
                    ))}
                    <button onClick={() => go("My Projects")}>
                      Open project workspace
                    </button>
                  </Card>
                </div>
              </>
            )}
            {section === "Learning Tracks" && (
              <>
                <div className="filters">
                  <label>
                    Choose track
                    <select
                      aria-label="Choose track"
                      value={trackId}
                      onChange={(event) => setTrackId(event.target.value)}
                    >
                      {options(tracks).map((option) => (
                        <option value={option.value} key={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>
                <Card title={text(track.name)}>
                  <Content
                    value={
                      track.description ??
                      track.overview ??
                      track.baseline_assessment
                    }
                  />
                  <p>
                    <strong>Target roles</strong>
                  </p>
                  <Content
                    value={track.target_role_categories ?? track.target_roles}
                  />
                  <div className="actions">
                    <button
                      className="primary"
                      onClick={() => void activate(trackId)}
                    >
                      Activate track
                    </button>
                    <button
                      onClick={() => {
                        setPlan({});
                        go("My Curriculum");
                      }}
                    >
                      Create learning plan
                    </button>
                    {plans
                      .filter((item) => item.track_id === trackId)
                      .map((item) => (
                        <button
                          key={item.id}
                          onClick={() =>
                            void run(() =>
                              api(
                                `plans/${item.id}/status/${item.status === "paused" ? "resume" : "pause"}`,
                                "POST",
                              ),
                            )
                          }
                        >
                          {item.status === "paused" ? "Resume" : "Pause"}{" "}
                          {text(item.title)}
                        </button>
                      ))}
                  </div>
                  <p>
                    Available independent plans: 14 days (49 hours), 30 days
                    (105 hours), 60 days (210 hours) at the default pace. These
                    are practice plans, not guarantees of mastery.
                  </p>
                  <details>
                    <summary>
                      Objectives, prerequisites and shared knowledge
                    </summary>
                    <Content
                      value={selected(track, [
                        "learning_objectives",
                        "baseline_assumptions",
                        "existing_experience_leverage",
                        "new_practical_experience",
                        "priority_rationale",
                      ])}
                    />
                    <p>
                      Shared competencies are assessed once across tracks;
                      explicit evidence can waive conceptual lessons when
                      creating a plan.
                    </p>
                  </details>
                </Card>
                <h2>Skill competency map</h2>
                <p className="muted">
                  Imported background never assigns expertise. Levels 4–6
                  require practical evidence.
                </p>
                <div className="grid">
                  {skills
                    .filter((item) => strings(item.track_ids).includes(trackId))
                    .map((skill) => {
                      const assessment = (personal.competency ?? []).find(
                        (item) => item.research_ref === skill.id,
                      );
                      return (
                        <Card
                          key={skill.id}
                          title={text(skill.name)}
                          eyebrow={levels[num(assessment?.level)]}
                        >
                          <progress
                            aria-label={`${text(skill.name)} competency`}
                            value={num(assessment?.level)}
                            max={6}
                          />
                          <details>
                            <summary>Assess with evidence</summary>
                            <Editor
                              fields={[
                                {
                                  name: "level",
                                  label: `${text(skill.name)} level`,
                                  type: "select",
                                  options: levels.map((label, value) => ({
                                    label,
                                    value: String(value),
                                  })),
                                },
                                {
                                  name: "evidence",
                                  label: "Practical evidence",
                                  type: "textarea",
                                },
                                {
                                  name: "evidence_url",
                                  label: "Evidence URL",
                                  type: "url",
                                },
                              ]}
                              initial={{
                                level: assessment?.level ?? 0,
                                evidence: assessment?.evidence ?? "",
                                evidence_url: assessment?.evidence_url ?? "",
                              }}
                              onSave={async (data) => {
                                await api(`skills/${skill.id}`, "PATCH", {
                                  ...data,
                                  level: Number(data.level),
                                });
                                await reload();
                              }}
                            />
                          </details>
                          <p className="muted">
                            Also used in:{" "}
                            {strings(skill.track_ids)
                              .filter((id) => id !== trackId)
                              .map(nameOf)
                              .join(", ") || "Track-specific"}
                          </p>
                        </Card>
                      );
                    })}
                </div>
                <h2>Recommended free resources</h2>
                <div className="grid">
                  {(catalog.resource ?? [])
                    .filter((item) => strings(item.track_ids).includes(trackId))
                    .sort((a, b) => num(b.overall_score) - num(a.overall_score))
                    .slice(0, 4)
                    .map(renderResource)}
                </div>
                <h2>Practical deliverables and interviews</h2>
                <p>
                  {
                    (catalog.project ?? []).filter((item) =>
                      strings(item.track_ids).includes(trackId),
                    ).length
                  }{" "}
                  project specifications;{" "}
                  {
                    (catalog.question ?? []).filter(
                      (item) => item.track_id === trackId,
                    ).length
                  }{" "}
                  interview questions.
                </p>
                <div className="actions">
                  <button onClick={() => go("Practical Labs")}>
                    Explore projects
                  </button>
                  <button
                    onClick={() => {
                      go("Interview Preparation");
                      setFilters({ track: trackId });
                    }}
                  >
                    Practice interviews
                  </button>
                  <button onClick={() => go("Settings")}>
                    Change track priority order
                  </button>
                </div>
              </>
            )}
            {section === "My Curriculum" && (
              <div className="split">
                <div className="stack">
                  <Card
                    title={
                      editing?.kind === "plan"
                        ? "Recalculate plan"
                        : "Create a research-backed plan"
                    }
                  >
                    <p className="muted">
                      Prerequisite order is preserved. Priority skills are
                      highlighted rather than reordered unsafely. Retained work
                      can extend a shortened plan.
                    </p>
                    <Editor
                      key={`plan-${editing?.id ?? trackId}-${text(targetJob.id)}`}
                      fields={planFields}
                      initial={
                        editing?.kind === "plan"
                          ? obj(editing.config)
                          : {
                              track_id: trackId,
                              target_role:
                                text(targetJob.title) ||
                                text(track.name) ||
                                "Senior Software Engineer",
                              duration_days: 30,
                              daily_minutes: prefs.daily_minutes ?? 210,
                              intensity: "balanced",
                              existing_competency: "Assess using evidence",
                              priority_skill_ids:
                                targetJob.required_skill_ids ?? [],
                              job_id: targetJob.id ?? null,
                              company_id: targetJob.company_id ?? null,
                              reuse_demonstrated: false,
                              dsa_practice_minutes: 0,
                            }
                      }
                      onSave={savePlan}
                      submit={
                        editing?.kind === "plan"
                          ? "Recalculate safely"
                          : "Generate study plan"
                      }
                    />
                  </Card>
                  {plan.id && (
                    <Card title={text(plan.title)}>
                      <p>
                        {text(plan.completed_count)} / {text(plan.lesson_count)}{" "}
                        complete · {text(plan.scheduled_days)} scheduled days
                      </p>
                      <div className="actions">
                        <button
                          onClick={() => setEditing({ ...plan, kind: "plan" })}
                        >
                          Adjust and recalculate
                        </button>
                        <button
                          onClick={() =>
                            void run(() =>
                              api(`plans/${plan.id}/status/activate`, "POST"),
                            )
                          }
                        >
                          Set active plan
                        </button>
                      </div>
                      {rows(plan.lessons).map((item) => (
                        <div className="row" key={item.id}>
                          <div>
                            <small>
                              Day {text(item.day)} ·{" "}
                              {text(item.estimated_total_study_minutes)} min
                            </small>
                            <p>{text(item.topic)}</p>
                            <span className="pill">
                              {item.skipped
                                ? "Skipped, not complete"
                                : human(text(obj(item.progress).status))}
                            </span>
                          </div>
                          <div className="actions">
                            <button
                              onClick={() => void openLesson(text(item.id))}
                            >
                              Study
                            </button>
                            <button
                              onClick={() =>
                                setEditing({ kind: "slot", ...item })
                              }
                            >
                              Adjust
                            </button>
                          </div>
                        </div>
                      ))}
                      {editing?.kind === "slot" && (
                        <Editor
                          key={editing.id}
                          fields={[
                            {
                              name: "day",
                              label: "Move to day",
                              type: "number",
                              min: 1,
                              max: 365,
                            },
                            {
                              name: "skipped",
                              label: "Skip lesson",
                              type: "checkbox",
                            },
                            {
                              name: "resource_id",
                              label: "Replacement free resource",
                              type: "select",
                              options: options(
                                (catalog.resource ?? []).filter((item) =>
                                  ["fully_free", "free_documentation"].includes(
                                    text(item.free_status),
                                  ),
                                ),
                              ),
                            },
                          ]}
                          initial={{
                            day: editing.day,
                            skipped: editing.skipped,
                          }}
                          onSave={async (data) => {
                            const payload = { ...data };
                            if (!payload.resource_id)
                              delete payload.resource_id;
                            await api(
                              `lessons/${editing.id}`,
                              "PATCH",
                              payload,
                            );
                            setPlan(await api(`plans/${plan.id}`));
                            await reload();
                            setEditing(null);
                          }}
                        />
                      )}
                      <details>
                        <summary>Add a learner-authored lesson</summary>
                        <Editor
                          fields={[
                            {
                              name: "topic",
                              label: "Custom topic",
                              required: true,
                            },
                            {
                              name: "objectives",
                              label: "Custom objectives",
                              type: "textarea",
                              required: true,
                            },
                            {
                              name: "exercise",
                              label: "Custom practical exercise",
                              type: "textarea",
                              required: true,
                            },
                            {
                              name: "resource_id",
                              label: "Existing resource",
                              type: "select",
                              options: options(catalog.resource ?? []),
                            },
                          ]}
                          onSave={async (data) => {
                            await api(`plans/${plan.id}/custom`, "POST", {
                              ...data,
                              resource_id: data.resource_id || null,
                            });
                            setPlan(await api(`plans/${plan.id}`));
                            await reload();
                          }}
                        />
                      </details>
                    </Card>
                  )}
                </div>
                <Card title="Your saved learning plans">
                  {empty(plans, "Create your first plan.")}
                  {plans.map((item) => (
                    <div className="row" key={item.id}>
                      <div>
                        <p>{text(item.title)}</p>
                        <small>
                          {nameOf(item.track_id)} · {text(item.status)} ·{" "}
                          {text(item.completed_count)}/{text(item.lesson_count)}
                        </small>
                      </div>
                      <button onClick={() => void openPlan(text(item.id))}>
                        Open
                      </button>
                    </div>
                  ))}
                </Card>
              </div>
            )}
            {section === "Study Room" && (
              <>
                {!lesson.id ? (
                  <Card title="Choose your next lesson">
                    <p>
                      Study guides, practical evidence and independent
                      completion controls live here.
                    </p>
                    {rows(dashboard.upcoming).map((item) => (
                      <div className="row" key={item.id}>
                        <p>
                          Day {text(item.day)}: {text(item.topic)}
                        </p>
                        <button onClick={() => void openLesson(text(item.id))}>
                          Open lesson
                        </button>
                      </div>
                    ))}
                    <button onClick={() => go("My Curriculum")}>
                      Choose any saved plan
                    </button>
                  </Card>
                ) : (
                  <>
                    <Card
                      title={text(lesson.topic)}
                      eyebrow={`Day ${text(lesson.day)} / ${text(lesson.estimated_total_study_minutes)} min / ${text(lesson.phase)}`}
                    >
                      <p className="muted">
                        Difficulty:{" "}
                        {text(
                          (catalog.resource ?? []).find(
                            (item) =>
                              item.id ===
                              lesson.recommended_youtube_resource_id,
                          )?.difficulty,
                        ) || "Not specified"}{" "}
                        · {human(text(obj(lesson.progress).status))}
                      </p>
                      <Content value={lesson.learning_objectives} />
                      <h3>Why this matters</h3>
                      <Content value={lesson.why_it_matters} />
                      <details open>
                        <summary>Prerequisites and time budget</summary>
                        <Content value={lesson.prerequisites} />
                        <Content value={lesson.time_budget_minutes} />
                      </details>
                      {(lesson.example_implementation != null ||
                        num(lesson.dsa_practice_minutes) > 0) && (
                        <details>
                          <summary>
                            DSA implementation and coding practice
                          </summary>
                          {lesson.example_implementation != null && (
                            <>
                              <h3>Original example implementation</h3>
                              <pre>{text(lesson.example_implementation)}</pre>
                              <Content value={lesson.complexity_analysis} />
                            </>
                          )}
                          {num(lesson.dsa_practice_minutes) > 0 && (
                            <p>
                              {num(lesson.dsa_practice_minutes)} minutes are
                              reserved for DSA within this lesson&apos;s total
                              budget.
                            </p>
                          )}
                          <button onClick={() => go("Interview Preparation")}>
                            Open DSA coding practice
                          </button>
                        </details>
                      )}
                    </Card>
                    <div className="split" style={{ marginTop: 24 }}>
                      <div className="stack">
                        <Card title="Before the video">
                          <Content
                            value={obj(lesson.study_guide).before_video}
                          />
                        </Card>
                        <Card title="Watch and implement">
                          <p className="muted">
                            Use the planned slice (
                            {text(lesson.planned_video_minutes)} minutes); the
                            complete video may be longer. No video is downloaded
                            or embedded.
                          </p>
                          {(catalog.resource ?? [])
                            .filter(
                              (item) =>
                                item.id ===
                                lesson.recommended_youtube_resource_id,
                            )
                            .map(renderResource)}
                          <h3>During the video</h3>
                          <Content
                            value={obj(lesson.study_guide).during_video}
                          />
                        </Card>
                        <Card title="Supplementary reading">
                          {strings(
                            lesson.supplementary_reading_resource_ids,
                          ).map((id) => {
                            const resource = (catalog.resource ?? []).find(
                              (item) => item.id === id,
                            );
                            return resource ? (
                              <p key={id}>
                                <External url={resource.url}>
                                  {text(resource.title)}
                                </External>
                              </p>
                            ) : (
                              <p key={id}>Missing resource: {id}</p>
                            );
                          })}
                        </Card>
                        <Card title="Practical implementation">
                          <Content
                            value={lesson.practical_implementation_exercise}
                          />
                          <h3>Expected outcome</h3>
                          <Content value={lesson.expected_outcome} />
                          <h3>Validate understanding</h3>
                          <Content
                            value={
                              obj(obj(lesson.study_guide).after_video)
                                .validate_understanding
                            }
                          />
                          <h3>Completion criteria</h3>
                          <Content value={lesson.completion_criteria} />
                        </Card>
                        <Card title="Knowledge check and revision">
                          <Content
                            value={
                              obj(obj(lesson.study_guide).after_video)
                                .comprehension_questions
                            }
                          />
                          <h3>Revision exercise</h3>
                          <Content value={lesson.revision_exercise} />
                          <h3>Interview practice</h3>
                          <Content
                            value={
                              lesson.interview_question_ids ??
                              lesson.interview_questions
                            }
                          />
                          <button
                            onClick={() => {
                              go("Interview Preparation");
                              setFilters({
                                skill: strings(lesson.skill_ids)[0] ?? "",
                              });
                            }}
                          >
                            Practice this topic
                          </button>
                        </Card>
                      </div>
                      <div className="stack">
                        <Card title="Capture your learning evidence">
                          <p className="muted">
                            All four checks must be explicitly completed.
                            Completion does not promote your competency.
                          </p>
                          <Editor
                            key={`${lesson.id}-${epoch}`}
                            fields={[
                              {
                                name: "video",
                                label: "Video completed",
                                type: "checkbox",
                              },
                              {
                                name: "reading",
                                label: "Reading completed",
                                type: "checkbox",
                              },
                              {
                                name: "practical",
                                label: "Practical completed",
                                type: "checkbox",
                              },
                              {
                                name: "knowledge",
                                label: "Knowledge check completed",
                                type: "checkbox",
                              },
                              {
                                name: "watched_minutes",
                                label: "Actual minutes watched",
                                type: "number",
                                min: 0,
                                max: 1440,
                              },
                              {
                                name: "study_minutes",
                                label: "Other actual study minutes",
                                type: "number",
                                min: 0,
                                max: 1440,
                              },
                              {
                                name: "evidence",
                                label: "Practical submission evidence",
                                type: "textarea",
                                hint: "Describe test results and reproducible artifacts; required for practical completion.",
                              },
                              {
                                name: "knowledge_answer",
                                label: "Knowledge-check answers",
                                type: "textarea",
                                hint: "Answer the numbered questions above. Required for knowledge completion.",
                              },
                            ]}
                            initial={{
                              ...obj(lesson.progress),
                              knowledge_answer: text(
                                obj(obj(lesson.progress).answers)["0"],
                              ),
                            }}
                            submit="Save lesson progress"
                            onSave={async (data) => {
                              const payload = selected(data, [
                                "video",
                                "reading",
                                "practical",
                                "knowledge",
                                "watched_minutes",
                                "study_minutes",
                                "evidence",
                              ]);
                              await api(`progress/${lesson.id}`, "PATCH", {
                                ...payload,
                                answers: {
                                  ...obj(obj(lesson.progress).answers),
                                  "0": text(data.knowledge_answer),
                                },
                              });
                              setLesson(await api(`lessons/${lesson.id}`));
                              await reload();
                              setNotice("Lesson progress saved locally.");
                            }}
                          />
                        </Card>
                        <Card title="Lesson notes">
                          {noteForm("lesson", text(lesson.id))}
                          {(personal.note ?? [])
                            .filter((item) => item.target_id === lesson.id)
                            .map((item) => (
                              <div key={item.id} className="markdown">
                                <h3>{text(item.title)}</h3>
                                <Markdown>{text(item.body)}</Markdown>
                              </div>
                            ))}
                        </Card>
                      </div>
                    </div>
                  </>
                )}
              </>
            )}
            {section === "Resource Library" && (
              <>
                <p className="lead">
                  Research-backed free learning. Unknown metadata stays unknown;
                  personal ratings never change evidence scores.
                </p>
                <div className="filters">
                  {filter("q", "Search resources")}
                  {trackFilter()}
                  {filter("skill", "Skill filter", options(skills))}
                  {filter(
                    "type",
                    "Resource type",
                    choices([
                      ...new Set(
                        (catalog.resource ?? []).map((item) =>
                          text(item.resource_type),
                        ),
                      ),
                    ]),
                  )}
                  {filter(
                    "difficulty",
                    "Difficulty",
                    choices([
                      ...new Set(
                        (catalog.resource ?? []).map((item) =>
                          text(item.difficulty),
                        ),
                      ),
                    ]),
                  )}
                  {filter(
                    "free",
                    "Free status",
                    choices([
                      ...new Set(
                        (catalog.resource ?? []).map((item) =>
                          text(item.free_status),
                        ),
                      ),
                    ]),
                  )}
                  {filter(
                    "duration",
                    "Maximum duration (minutes)",
                    undefined,
                    "number",
                  )}
                  {filter(
                    "score",
                    "Minimum quality score",
                    undefined,
                    "number",
                  )}
                  {filter("published", "Published after", undefined, "date")}
                  {filter(
                    "sort",
                    "Sort resources",
                    choices(["quality", "title", "newest"]),
                  )}
                  {filter("bookmark", "Bookmarks", choices(["bookmarked"]))}
                </div>
                <div className="actions">
                  <button onClick={() => go("Settings")}>
                    Import validated resource catalogue
                  </button>
                  <a href="/api/data/export?kind=research" download>
                    Export resource research
                  </a>
                </div>
                <div className="grid">
                  {(catalog.resource ?? [])
                    .filter(
                      (item) =>
                        (!filters.q ||
                          JSON.stringify(item)
                            .toLowerCase()
                            .includes(filters.q.toLowerCase())) &&
                        (!filters.track ||
                          strings(item.track_ids).includes(filters.track)) &&
                        (!filters.skill ||
                          strings(item.skill_ids).includes(filters.skill)) &&
                        (!filters.type ||
                          item.resource_type === filters.type) &&
                        (!filters.difficulty ||
                          item.difficulty === filters.difficulty) &&
                        (!filters.free || item.free_status === filters.free) &&
                        (!filters.duration ||
                          (item.duration_minutes != null &&
                            num(item.duration_minutes) <=
                              Number(filters.duration))) &&
                        (!filters.score ||
                          num(item.overall_score) >= Number(filters.score)) &&
                        (!filters.published ||
                          text(item.published_at) >= filters.published) &&
                        (!filters.bookmark ||
                          (personal.resource ?? []).some(
                            (pref) =>
                              pref.research_ref === item.id && pref.bookmarked,
                          )),
                    )
                    .sort((a, b) =>
                      filters.sort === "title"
                        ? text(a.title).localeCompare(text(b.title))
                        : filters.sort === "newest"
                          ? text(b.published_at).localeCompare(
                              text(a.published_at),
                            )
                          : num(b.overall_score) - num(a.overall_score),
                    )
                    .map(renderResource)}
                </div>
                {Object.keys(integrationResult).length > 0 && (
                  <Card title="Official API metadata">
                    <Content value={integrationResult} />
                  </Card>
                )}
              </>
            )}
            {section === "Practical Labs" && (
              <>
                <p className="lead">
                  Real engineering specifications: requirements, failure tests,
                  security, deployment and interview trade-offs. Cloud and API
                  execution can incur costs; local exercises need no paid
                  service.
                </p>
                <div className="filters">
                  {trackFilter()}
                  {filter(
                    "category",
                    "Project category",
                    choices([
                      ...new Set(
                        (catalog.project ?? []).map((item) =>
                          text(item.level ?? item.category),
                        ),
                      ),
                    ]),
                  )}
                </div>
                <div className="grid">
                  {(catalog.project ?? [])
                    .filter(
                      (item) =>
                        (!filters.track ||
                          strings(item.track_ids).includes(filters.track)) &&
                        (!filters.category ||
                          (item.level ?? item.category) === filters.category),
                    )
                    .map((item) => (
                      <Card
                        key={item.id}
                        title={text(item.title)}
                        eyebrow={text(item.level ?? item.category)}
                      >
                        <Content value={item.problem_statement} />
                        <details>
                          <summary>Complete engineering specification</summary>
                          <Content
                            value={selected(item, [
                              "architecture",
                              "engineering_requirements",
                              "technologies",
                              "milestones",
                              "testing_strategy",
                              "security_considerations",
                              "deployment_requirements",
                              "expected_github_deliverables",
                              "interview_discussion_points",
                            ])}
                          />
                        </details>
                        <button
                          className="primary"
                          onClick={() =>
                            void run(
                              () => api(`projects/${item.id}/start`, "POST"),
                              "Project added to your persistent workspace.",
                            )
                          }
                        >
                          Start project
                        </button>
                      </Card>
                    ))}
                </div>
              </>
            )}
            {section === "Interview Preparation" && (
              <>
                <details
                  open={
                    trackId === "track-dsa" || filters.track === "track-dsa"
                  }
                >
                  <summary>
                    DSA coding practice, timed assessments and company
                    preparation
                  </summary>
                  <DsaPractice
                    aiConfigured={Boolean(obj(boot.integrations).ai_configured)}
                    onChanged={reload}
                  />
                </details>
                <p className="lead">
                  Reason through incidents and trade-offs. Assess against
                  detailed rubrics, not keyword scoring or memorized flashcards.
                </p>
                <div className="filters">
                  {trackFilter()}
                  {filter("q", "Search questions")}
                  {filter("skill", "Interview skill", options(skills))}
                  {filter(
                    "difficulty",
                    "Question difficulty",
                    choices([
                      ...new Set(
                        (catalog.question ?? []).map((item) =>
                          text(item.difficulty),
                        ),
                      ),
                    ]),
                  )}
                  {filter(
                    "category",
                    "Interview category",
                    choices([
                      ...new Set(
                        (catalog.question ?? []).map((item) =>
                          text(item.category),
                        ),
                      ),
                    ]),
                  )}
                  {filter(
                    "mode",
                    "Practice mode",
                    choices(["quick", "topic", "mock", "senior", "revision"]),
                  )}
                </div>
                <div className="actions">
                  <button
                    className="primary"
                    onClick={() => {
                      const eligible = questionList.filter(
                        (item) =>
                          filters.mode !== "senior" ||
                          ["advanced", "senior"].includes(
                            text(item.difficulty),
                          ),
                      );
                      if (!eligible.length) {
                        setNotice("No questions match those filters.");
                        return;
                      }
                      setQuestion(
                        eligible[Math.floor(Math.random() * eligible.length)],
                      );
                      setIntegrationResult({});
                      setMockQueue([]);
                    }}
                  >
                    Quick random question
                  </button>
                  <select
                    aria-label="Choose mock interview"
                    defaultValue=""
                    onChange={(event) => void startMock(event.target.value)}
                  >
                    <option value="">Choose a mock interview…</option>
                    {options(catalog.mock ?? []).map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="split">
                  <div className="stack">
                    {question.id && (
                      <Card
                        title={text(question.question)}
                        eyebrow={`${text(question.difficulty)} / ${human(text(question.category))}`}
                      >
                        <Editor
                          key={question.id}
                          fields={[
                            {
                              name: "answer",
                              label: "Your interview answer",
                              type: "textarea",
                              required: true,
                            },
                            {
                              name: "score",
                              label: "Self-rubric score (0–10)",
                              type: "number",
                              min: 0,
                              max: 10,
                              required: true,
                            },
                            {
                              name: "confidence",
                              label: "Confidence (1–5)",
                              type: "number",
                              min: 1,
                              max: 5,
                              required: true,
                            },
                            ...[
                              "correctness",
                              "depth",
                              "clarity",
                              "experience",
                              "tradeoffs",
                              "completeness",
                            ].map((name) => ({
                              name,
                              label: `${human(name)} (0–5)`,
                              type: "number" as const,
                              min: 0,
                              max: 5,
                            })),
                          ]}
                          initial={{ answer: "", score: 5, confidence: 3 }}
                          submit="Record interview attempt"
                          onSave={async (data) => {
                            const dimensions = selected(data, [
                              "correctness",
                              "depth",
                              "clarity",
                              "experience",
                              "tradeoffs",
                              "completeness",
                            ]);
                            await api("attempts", "POST", {
                              question_id: question.id,
                              answer: data.answer,
                              score: data.score,
                              confidence: data.confidence,
                              dimensions,
                              mode: mockQueue.length
                                ? "mock"
                                : filters.mode || "quick",
                            });
                            await reload();
                            setNotice(
                              "Answer recorded. Low score or confidence schedules revision.",
                            );
                          }}
                        />
                        <details>
                          <summary>
                            Answer elements, rubric and detailed explanation
                          </summary>
                          <Content value={question.expected_answer_elements} />
                          <Content value={question.evaluation_rubric} />
                          <Content value={question.detailed_explanation} />
                          <h3>Follow-ups</h3>
                          <Content value={question.follow_up_questions} />
                          <h3>Common mistakes</h3>
                          <Content value={question.common_mistakes} />
                        </details>
                        {Boolean(obj(boot.integrations).ai_configured) && (
                          <details>
                            <summary>
                              Optional provider feedback (may incur API costs)
                            </summary>
                            <Editor
                              fields={[
                                {
                                  name: "answer",
                                  label: "Answer to send to provider",
                                  type: "textarea",
                                  required: true,
                                },
                                {
                                  name: "consent",
                                  label:
                                    "I consent to sending this answer to the configured provider",
                                  type: "checkbox",
                                },
                              ]}
                              onSave={async (data) => {
                                setIntegrationResult(
                                  await api("interviews/evaluate", "POST", {
                                    ...data,
                                    question_id: question.id,
                                  }),
                                );
                              }}
                              submit="Request optional feedback"
                            />
                          </details>
                        )}
                        {Object.keys(integrationResult).length > 0 && (
                          <Content value={integrationResult} />
                        )}
                        {mockQueue.length > 0 && (
                          <button
                            onClick={() => {
                              setQuestion(
                                (catalog.question ?? []).find(
                                  (item) => item.id === mockQueue[0],
                                ) ?? {},
                              );
                              setMockQueue(mockQueue.slice(1));
                            }}
                          >
                            Next mock question ({mockQueue.length} remaining)
                          </button>
                        )}
                      </Card>
                    )}
                    {!question.id && (
                      <Card title="Start a practice session">
                        <p>
                          Select a topic, random question or mock interview.
                          Saved answers remain available offline.
                        </p>
                      </Card>
                    )}
                    <Card title="Recent interview history">
                      {empty(
                        personal.attempt ?? [],
                        "No answers recorded yet.",
                      )}
                      {(personal.attempt ?? []).slice(0, 12).map((item) => (
                        <details key={item.id}>
                          <summary>
                            {text(item.created_at).slice(0, 10)} ·{" "}
                            {text(item.score)}/10 · {nameOf(item.track_id)}
                          </summary>
                          <p>
                            {text(
                              (catalog.question ?? []).find(
                                (q) => q.id === item.question_id,
                              )?.question,
                            )}
                          </p>
                          <Content value={item.answer} />
                          <Content value={item.dimensions} />
                        </details>
                      ))}
                    </Card>
                  </div>
                  <Card
                    title={`Question bank (${questionList.length} matches)`}
                  >
                    {questionList
                      .filter(
                        (item) =>
                          filters.mode !== "revision" ||
                          (personal.review ?? []).some(
                            (review) => review.question_id === item.id,
                          ),
                      )
                      .slice(
                        Number(filters.page ?? 0) * 20,
                        Number(filters.page ?? 0) * 20 + 20,
                      )
                      .map((item) => (
                        <div className="row" key={item.id}>
                          <div>
                            <small>
                              {text(item.difficulty)} ·{" "}
                              {human(text(item.category))}
                            </small>
                            <p>{text(item.question)}</p>
                          </div>
                          <button
                            onClick={() => {
                              setQuestion(item);
                              setMockQueue([]);
                              setIntegrationResult({});
                            }}
                          >
                            Practice
                          </button>
                        </div>
                      ))}
                    <div className="actions">
                      <button
                        disabled={!Number(filters.page ?? 0)}
                        onClick={() =>
                          setFilters({
                            ...filters,
                            page: String(Number(filters.page) - 1),
                          })
                        }
                      >
                        Previous
                      </button>
                      <span>Page {Number(filters.page ?? 0) + 1}</span>
                      <button
                        disabled={
                          (Number(filters.page ?? 0) + 1) * 20 >=
                          questionList.length
                        }
                        onClick={() =>
                          setFilters({
                            ...filters,
                            page: String(Number(filters.page ?? 0) + 1),
                          })
                        }
                      >
                        Next
                      </button>
                    </div>
                  </Card>
                </div>
              </>
            )}
            {section === "Career Intelligence" && (
              <>
                <p className="lead">
                  A configurable employer watchlist and manual job workspace.
                  Seed postings are historical research samples, not claims that
                  roles are still open.
                </p>
                <div className="actions">
                  <button
                    onClick={() =>
                      setEditing({
                        kind: "company",
                        name: "",
                        priority: 3,
                        enabled: true,
                      })
                    }
                  >
                    Add company
                  </button>
                  <button
                    onClick={() =>
                      setEditing({
                        kind: "job",
                        title: "",
                        description: "",
                        application_status: "saved",
                        required_skill_ids: [],
                        preferred_skill_ids: [],
                      })
                    }
                  >
                    Add job
                  </button>
                </div>
                <div className="split">
                  <div className="stack">
                    {editing?.kind === "company" && (
                      <Card
                        title={editing.id ? "Edit employer" : "New employer"}
                      >
                        <Editor
                          key={`${editing.id ?? "new-company"}-${epoch}`}
                          fields={companyFields}
                          initial={editing}
                          onSave={async (data) => {
                            await api(
                              `personal/company${editing.id ? "/" + editing.id : ""}`,
                              editing.id ? "PATCH" : "POST",
                              selected(
                                data,
                                companyFields.map((field) => field.name),
                              ),
                            );
                            setEditing(null);
                            await reload();
                          }}
                        />
                      </Card>
                    )}
                    {editing?.kind === "job" && (
                      <Card
                        title={
                          editing.id
                            ? "Edit opportunity"
                            : "Manual job description import"
                        }
                      >
                        <p className="muted">
                          Suggestions are reviewable keyword matches, not expert
                          extraction. Paste the full JD, extract, then confirm
                          skill lists before saving. No URL scraper is required.
                        </p>
                        <Editor
                          key={`${editing.id ?? "new-job"}-${JSON.stringify(editing.required_skill_ids)}`}
                          fields={jobFields}
                          initial={editing}
                          extra={(data) => (
                            <button
                              type="button"
                              onClick={() =>
                                void run(async () => {
                                  const result = await api(
                                    "jobs/analyze",
                                    "POST",
                                    { description: data.description },
                                  );
                                  setEditing({
                                    ...editing,
                                    ...data,
                                    required_skill_ids:
                                      result.required_skill_ids,
                                    preferred_skill_ids:
                                      result.preferred_skill_ids,
                                  });
                                  setNotice(
                                    `${text(result.method)} Seniority signals: ${strings(result.seniority_expectations).join(", ") || "none detected"}`,
                                  );
                                }, "Review and confirm the suggested skills before saving.")
                              }
                            >
                              Extract skill suggestions
                            </button>
                          )}
                          onSave={async (data) => {
                            await api(
                              `personal/job${editing.id ? "/" + editing.id : ""}`,
                              editing.id ? "PATCH" : "POST",
                              {
                                ...selected(
                                  data,
                                  jobFields.map((field) => field.name),
                                ),
                                deadline: data.deadline || null,
                              },
                            );
                            setEditing(null);
                            await reload();
                          }}
                        />
                      </Card>
                    )}
                    <Card title="Employer watchlist">
                      {(personal.company ?? []).map((item) => (
                        <details key={item.id}>
                          <summary>
                            {text(item.name)} · priority {text(item.priority)}
                            {item.enabled === false ? " · disabled" : ""}
                          </summary>
                          <p>
                            {text(item.location)} · {text(item.arrangement)}
                          </p>
                          <External url={item.career_url}>Career page</External>
                          <Content value={item.notes} />
                          <p>Target roles: {text(item.target_roles)}</p>
                          <div className="actions">
                            <button
                              onClick={() =>
                                setEditing({ ...item, kind: "company" })
                              }
                            >
                              Edit company
                            </button>
                            <button
                              onClick={() =>
                                void run(
                                  () =>
                                    api(
                                      `personal/company/${item.id}`,
                                      "DELETE",
                                    ),
                                  "Company removed, if no jobs were linked.",
                                )
                              }
                            >
                              Delete company
                            </button>
                          </div>
                        </details>
                      ))}
                    </Card>
                  </div>
                  <div className="stack">
                    <Card title="Job opportunities">
                      {empty(
                        personal.job ?? [],
                        "Add an opportunity from its original job description.",
                      )}
                      {(personal.job ?? []).map((item) => (
                        <details key={item.id}>
                          <summary>
                            {text(item.title)} · {text(item.application_status)}
                          </summary>
                          <p>
                            {text(
                              (personal.company ?? []).find(
                                (company) => company.id === item.company_id,
                              )?.name,
                            )}{" "}
                            · {text(item.location)}
                          </p>
                          <External url={item.url}>Original posting</External>
                          <Content value={item.description} />
                          <Content value={item.notes} />
                          <Content value={item.interview_feedback} />
                          <div className="actions">
                            <button
                              onClick={() =>
                                setEditing({ ...item, kind: "job" })
                              }
                            >
                              Edit job
                            </button>
                            <button
                              onClick={() =>
                                void run(async () => {
                                  setGaps(await api(`jobs/${item.id}/gaps`));
                                  setTargetJob(item);
                                }, "Gap report uses explicit assessments, not CV claims.")
                              }
                            >
                              Analyze skill gaps
                            </button>
                            <button
                              onClick={() =>
                                void run(() =>
                                  api(`personal/job/${item.id}`, "DELETE"),
                                )
                              }
                            >
                              Delete job
                            </button>
                          </div>
                        </details>
                      ))}
                    </Card>
                    {gaps.rows !== undefined && (
                      <Card title={`Skill gaps: ${text(targetJob.title)}`}>
                        <div className="table-wrap">
                          <table>
                            <thead>
                              <tr>
                                <th>Skill</th>
                                <th>Evidence status</th>
                                <th>Relevant resources</th>
                              </tr>
                            </thead>
                            <tbody>
                              {rows(gaps.rows).map((item) => (
                                <tr key={text(item.skill_id)}>
                                  <td>{skillName(item.skill_id)}</td>
                                  <td>{human(text(item.status))}</td>
                                  <td>
                                    {strings(item.resource_ids).map((id) => {
                                      const resource = (
                                        catalog.resource ?? []
                                      ).find((item) => item.id === id);
                                      return (
                                        <p key={id}>
                                          <External url={resource?.url}>
                                            {text(resource?.title ?? id)}
                                          </External>
                                        </p>
                                      );
                                    })}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                        <Content value={gaps.limitations} />
                        <button
                          className="primary"
                          onClick={() => {
                            setPlan({});
                            go("My Curriculum");
                          }}
                        >
                          Create job-specific plan
                        </button>
                      </Card>
                    )}
                  </div>
                </div>
              </>
            )}
            {section === "My Projects" && (
              <>
                <div className="actions">
                  <button
                    className="primary"
                    onClick={() =>
                      setEditing({
                        kind: "project",
                        title: "",
                        track_ids: [trackId],
                        tasks: [],
                        status: "active",
                      })
                    }
                  >
                    Create custom project
                  </button>
                  <button onClick={() => go("Practical Labs")}>
                    Start from a research specification
                  </button>
                </div>
                {editing?.kind === "project" && (
                  <Card
                    title={
                      editing.id ? "Edit project" : "Custom engineering project"
                    }
                  >
                    <Editor
                      key={editing.id ?? "custom-project"}
                      fields={projectFields}
                      initial={editing}
                      onSave={async (data) => {
                        await api(
                          `personal/project${editing.id ? "/" + editing.id : ""}`,
                          editing.id ? "PATCH" : "POST",
                          {
                            ...selected(
                              data,
                              projectFields.map((field) => field.name),
                            ),
                            tasks: editing.tasks ?? [],
                          },
                        );
                        setEditing(null);
                        await reload();
                      }}
                    />
                  </Card>
                )}
                <div className="grid">
                  {(personal.project ?? []).map((item) => (
                    <Card
                      key={item.id}
                      title={text(item.title)}
                      eyebrow={text(item.status)}
                    >
                      <p className="muted">
                        {strings(item.track_ids).map(nameOf).join(" / ")}
                      </p>
                      <Content value={item.overview} />
                      <progress
                        aria-label={`${text(item.title)} milestones`}
                        max={rows(item.tasks).length || 1}
                        value={
                          rows(item.tasks).filter((task) => task.completed)
                            .length
                        }
                      />
                      <details>
                        <summary>
                          Architecture, requirements and testing
                        </summary>
                        <Content
                          value={selected(item, [
                            "architecture",
                            "requirements",
                            "testing_checklist",
                          ])}
                        />
                      </details>
                      {rows(item.tasks).map((task) => (
                        <div key={task.id} className="row">
                          <label>
                            <input
                              type="checkbox"
                              checked={Boolean(task.completed)}
                              onChange={(event) =>
                                void toggleTask(
                                  item,
                                  task,
                                  event.target.checked,
                                )
                              }
                            />{" "}
                            {text(task.title)}
                            <small
                              className="prose"
                              style={{ display: "block" }}
                            >
                              {text(task.validation)}
                            </small>
                          </label>
                        </div>
                      ))}
                      <details>
                        <summary>Add task / milestone</summary>
                        <Editor
                          fields={[
                            {
                              name: "title",
                              label: "Task title",
                              required: true,
                            },
                            {
                              name: "validation",
                              label: "Task validation criteria",
                              type: "textarea",
                            },
                          ]}
                          onSave={async (data) => {
                            await api(`personal/project/${item.id}`, "PATCH", {
                              ...selected(
                                item,
                                projectFields.map((field) => field.name),
                              ),
                              tasks: [
                                ...rows(item.tasks),
                                {
                                  ...data,
                                  id: crypto.randomUUID(),
                                  completed: false,
                                },
                              ],
                            });
                            await reload();
                          }}
                        />
                      </details>
                      <div className="actions">
                        <External url={item.github_url}>Repository</External>
                        <External url={item.deployment_url}>
                          Deployment
                        </External>
                        <button
                          onClick={() =>
                            setEditing({ ...item, kind: "project" })
                          }
                        >
                          Edit project
                        </button>
                        <button
                          onClick={() =>
                            void run(() =>
                              api(`personal/project/${item.id}`, "DELETE"),
                            )
                          }
                        >
                          Delete project
                        </button>
                      </div>
                    </Card>
                  ))}
                </div>
                {empty(
                  personal.project ?? [],
                  "Start a research project or create your own.",
                )}
              </>
            )}
            {section === "Notes and Revision" && (
              <div className="split">
                <div className="stack">
                  <Card
                    title={
                      editing?.kind === "note"
                        ? "Edit your note"
                        : "Capture an engineering explanation"
                    }
                  >
                    {noteForm()}
                    <p>
                      <a href="/api/data/export?kind=notes" download>
                        Export all notes as Markdown
                      </a>
                    </p>
                  </Card>
                  <Card title="Your notes">
                    {empty(personal.note ?? [], "No notes yet.")}
                    {(personal.note ?? []).map((item) => (
                      <article key={item.id} className="markdown">
                        <small>
                          {human(text(item.target_type))} ·{" "}
                          {text(item.updated_at).slice(0, 10)}
                        </small>
                        <h3>{text(item.title)}</h3>
                        <Markdown>{text(item.body)}</Markdown>
                        <div className="actions">
                          <button
                            onClick={() =>
                              setEditing({ ...item, kind: "note" })
                            }
                          >
                            Edit note
                          </button>
                          <button
                            onClick={() =>
                              void run(() =>
                                api(`personal/note/${item.id}`, "DELETE"),
                              )
                            }
                          >
                            Delete note
                          </button>
                        </div>
                      </article>
                    ))}
                  </Card>
                </div>
                <div className="stack">
                  <Card title="Spaced revision queue">
                    <p className="muted">
                      Intervals:{" "}
                      {strings(prefs.review_intervals).join(", ") ||
                        (Array.isArray(prefs.review_intervals)
                          ? prefs.review_intervals.join(", ")
                          : "1, 3, 7, 14, 30")}{" "}
                      days. Dates use UTC.
                    </p>
                    {empty(
                      personal.review ?? [],
                      "Low scores or confidence schedule your first review.",
                    )}
                    {(personal.review ?? []).map((review) => (
                      <div key={review.id} className="row">
                        <div>
                          <small>Due {text(review.due_date)}</small>
                          <p>
                            {text(
                              (catalog.question ?? []).find(
                                (item) => item.id === review.question_id,
                              )?.question,
                            )}
                          </p>
                          <div className="actions">
                            <button
                              onClick={() => {
                                setQuestion(
                                  (catalog.question ?? []).find(
                                    (item) => item.id === review.question_id,
                                  ) ?? {},
                                );
                                go("Interview Preparation");
                                setFilters({ mode: "revision" });
                              }}
                            >
                              Practice review
                            </button>
                            <button
                              onClick={() =>
                                void run(() =>
                                  api(`reviews/${review.id}`, "POST", {
                                    successful: true,
                                  }),
                                )
                              }
                            >
                              Successful recall
                            </button>
                            <button
                              onClick={() =>
                                void run(() =>
                                  api(`reviews/${review.id}`, "POST", {
                                    successful: false,
                                  }),
                                )
                              }
                            >
                              Repeat sooner
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </Card>
                  <Card title="Recently demonstrated skills">
                    {(personal.competency ?? [])
                      .filter((item) => num(item.level) >= 4)
                      .slice(0, 10)
                      .map((item) => (
                        <p key={item.id}>
                          {skillName(item.research_ref)} ·{" "}
                          {levels[num(item.level)]}
                        </p>
                      ))}
                  </Card>
                  <Card title="Weak areas">
                    <Content
                      value={rows(dashboard.weak_areas).map(
                        (item) =>
                          `${skillName(item.research_ref)}: ${levels[num(item.level)]}`,
                      )}
                    />
                  </Card>
                </div>
              </div>
            )}
            {section === "Settings" && (
              <div className="split">
                <div className="stack">
                  <Card title="Workspace preferences">
                    <Editor
                      key={`settings-${epoch}`}
                      fields={[
                        {
                          name: "theme",
                          label: "Theme",
                          type: "select",
                          options: choices(["dark", "light", "system"]),
                        },
                        {
                          name: "daily_minutes",
                          label: "Default daily minutes",
                          type: "number",
                          min: 180,
                          max: 240,
                        },
                        {
                          name: "priority_order",
                          label: "Track priority order",
                          hint: "Comma-separated track IDs in order.",
                        },
                        {
                          name: "intervals",
                          label: "Review intervals",
                          hint: "Unique ascending days, comma separated.",
                        },
                      ]}
                      initial={{
                        theme: prefs.theme,
                        daily_minutes: prefs.daily_minutes,
                        priority_order: strings(prefs.priorities).length
                          ? strings(prefs.priorities).join(", ")
                          : tracks.map((item) => item.id).join(", "),
                        intervals: Array.isArray(prefs.review_intervals)
                          ? prefs.review_intervals.join(", ")
                          : "1, 3, 7, 14, 30",
                      }}
                      onSave={async (data) => {
                        await api("settings", "PATCH", {
                          ...prefs,
                          theme: data.theme,
                          daily_minutes: data.daily_minutes,
                          priorities: text(data.priority_order)
                            .split(",")
                            .map((value) => value.trim())
                            .filter(Boolean),
                          review_intervals: text(data.intervals)
                            .split(",")
                            .map((value) => Number(value.trim())),
                        });
                        await reload();
                      }}
                    />
                    <p className="muted">
                      Track IDs: {tracks.map((item) => item.id).join(", ")}
                    </p>
                  </Card>
                  <Card title="Optional server-side integrations">
                    <Content value={boot.integrations} />
                    <p>
                      No API keys are entered into this browser or included in
                      exports. Configure the server&apos;s ignored .env file and
                      restart the backend. YouTube links, local rubrics and all
                      core features work without credentials. Provider calls
                      require explicit action; AI feedback additionally requires
                      consent and can incur charges.
                    </p>
                    <p>
                      YouTube metadata uses a 24-hour cache. Missing comments
                      stay unavailable; no sentiment is fabricated.
                    </p>
                  </Card>
                </div>
                <div className="stack">
                  <Card title="Export and backup">
                    <p>
                      Back up before updating or moving laptops. These exports
                      contain personal learning data, but no configured API
                      secrets.
                    </p>
                    <div className="actions">
                      <a href="/api/data/export" download>
                        Full JSON export
                      </a>
                      <a href="/api/data/backup" download>
                        SQLite snapshot
                      </a>
                      <a href="/api/data/export?kind=notes" download>
                        Markdown notes
                      </a>
                      <a href="/api/data/export?kind=research" download>
                        Research package
                      </a>
                    </div>
                  </Card>
                  <Card title="Validate and preview an import">
                    <label>
                      Import kind
                      <select
                        aria-label="Import kind"
                        value={importKind}
                        onChange={(event) => {
                          setImportKind(event.target.value);
                          setPreview({});
                        }}
                      >
                        <option value="research">
                          Research catalogue update
                        </option>
                        <option value="personal">
                          Personal JSON backup (merge)
                        </option>
                      </select>
                    </label>
                    <label>
                      JSON file
                      <input
                        aria-label="JSON import file"
                        type="file"
                        accept=".json,application/json"
                        onChange={(event) => {
                          const file = event.target.files?.[0];
                          if (!file) return;
                          void run(async () => {
                            if (file.size > 20 * 1024 * 1024)
                              throw new Error("Import exceeds 20 MB.");
                            const payload: unknown = JSON.parse(
                              await file.text(),
                            );
                            setPreview(
                              await api("data/preview", "POST", {
                                kind: importKind,
                                payload,
                              }),
                            );
                          }, "Validated preview created. Nothing has been imported yet.");
                        }}
                      />
                    </label>
                    {preview.id && (
                      <>
                        <Content
                          value={selected(preview, [
                            "counts",
                            "versions",
                            "warning",
                          ])}
                        />
                        <button
                          className="primary"
                          onClick={() =>
                            void run(async () => {
                              await api(`data/apply/${preview.id}`, "POST", {
                                confirm: true,
                              });
                              setPreview({});
                              const data = await Promise.all(
                                ["resource", "question", "project", "mock"].map(
                                  (kind) => catalogue(kind),
                                ),
                              );
                              setCatalog(
                                Object.fromEntries(
                                  [
                                    "resource",
                                    "question",
                                    "project",
                                    "mock",
                                  ].map((kind, index) => [
                                    kind,
                                    rows(data[index].items),
                                  ]),
                                ),
                              );
                            }, "Import applied atomically. Existing personal work is retained.")
                          }
                        >
                          Confirm and apply import
                        </button>
                      </>
                    )}
                  </Card>
                  <Card title="Restore a SQLite snapshot">
                    <p className="muted">
                      Restore replaces current learning data. A pre-restore
                      recovery copy is retained on disk. Only compatible
                      validated Academy snapshots are accepted.
                    </p>
                    <label>
                      <input id="confirm-restore" type="checkbox" /> I
                      understand this replaces the current database
                    </label>
                    <input
                      aria-label="SQLite restore file"
                      type="file"
                      accept=".sqlite3,.db"
                      onChange={(event) => {
                        const file = event.target.files?.[0];
                        if (!file) return;
                        void run(async () => {
                          if (
                            !(
                              document.getElementById(
                                "confirm-restore",
                              ) as HTMLInputElement
                            ).checked
                          )
                            throw new Error(
                              "Confirm database replacement first.",
                            );
                          if (file.size > 64 * 1024 * 1024)
                            throw new Error("Restore exceeds 64 MB.");
                          const response = await fetch("/api/data/restore", {
                            method: "POST",
                            headers: {
                              "Content-Type": "application/octet-stream",
                              "X-Academy-Client": "local-workspace",
                              "X-Academy-Confirm": "restore",
                            },
                            body: await file.arrayBuffer(),
                          });
                          const result: unknown = await response.json();
                          if (!response.ok)
                            throw new Error(text(obj(result).detail));
                          setNotice(
                            "Snapshot restored. Reload the workspace to re-open restored plans.",
                          );
                          setPlan({});
                          setLesson({});
                        }, "Database restored and validated.");
                      }}
                    />
                  </Card>
                </div>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
