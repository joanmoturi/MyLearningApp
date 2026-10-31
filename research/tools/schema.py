"""Explicit Draft 2020-12 schemas, independent of generated data values."""

import json
from pathlib import Path

S = {"type": "string", "minLength": 1}
I = {"type": "integer", "minimum": 0}
N = {"type": "number", "minimum": 0}
B = {"type": "boolean"}
NULL = {"type": "null"}
DATE = {"type": "string", "format": "date"}
URI = {"type": "string", "format": "uri"}
ID = {"type": "string", "pattern": "^[a-z][a-z0-9-]+$"}


def nullable(value):
    return {"anyOf": [value, NULL]}


def arr(value, minimum=0, unique=False):
    return {"type": "array", "items": value, "minItems": minimum, "uniqueItems": unique}


def obj(**props):
    return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}


def enum(*values):
    return {"enum": list(values)}


IDS = arr(ID, unique=True)
STRINGS = arr(S)
POINT = {"type": "integer", "minimum": 0, "maximum": 100}
TRACK = obj(
    id=ID, name=S, target_role_categories=STRINGS, priority=I,
    baseline_assessment=S, skill_ids=IDS,
)
SCORE = obj(
    technical_correctness=nullable({"type": "integer", "minimum": 0, "maximum": 25}),
    role_relevance=nullable({"type": "integer", "minimum": 0, "maximum": 20}),
    depth_completeness=nullable({"type": "integer", "minimum": 0, "maximum": 15}),
    practical_implementation=nullable({"type": "integer", "minimum": 0, "maximum": 15}),
    publisher_credibility=nullable({"type": "integer", "minimum": 0, "maximum": 10}),
    community_feedback=nullable({"type": "integer", "minimum": 0, "maximum": 10}),
    recency=nullable({"type": "integer", "minimum": 0, "maximum": 5}),
)
SCORE_RATIONALE = obj(**{key: S for key in SCORE["properties"]})
RESOURCE = obj(
    id=ID, title=S, resource_type=enum("official_documentation", "free_course", "youtube_video"),
    provider=S, creator=S, url=URI, track_ids=IDS, skill_ids=IDS, difficulty=S,
    duration_minutes=nullable(N), duration_status=enum("publisher_stated", "unavailable"),
    free_status=enum("fully_free", "free_audit", "free_documentation", "free_introductory", "free_optional_paid_certification", "paid"),
    free_evidence=S, execution_cost=S, published_at=nullable(DATE), last_verified_at=DATE,
    verification_scope=S, view_count=nullable(I), like_count=nullable(I),
    comment_count=nullable(I), playlist_size=nullable(I),
    community_feedback_summary=S, technical_quality_score=nullable(POINT), relevance_score=nullable(POINT),
    public_metadata_observations=obj(observed_at=DATE, view_count_display=nullable(S), like_count_display=nullable(S), published_age_display=nullable(S), interpretation=S),
    overall_score=POINT, score_upper_bound=POINT, score_breakdown=SCORE, score_rationale=SCORE_RATIONALE,
    confidence=enum("low", "medium", "high"), selection_reason=S, technical_relevance=S,
    implementation_demonstration=S, limitations=STRINGS, verification_sources=IDS,
    verified_chapters=arr(obj(start_seconds=I, label=S, verification=S)),
)
SOURCE = obj(
    id=ID, url=URI, title=S, source_type=S, collection_date=DATE, published_at=nullable(DATE),
    method=S, content_status=S, http_status=nullable(I), final_url=nullable(URI),
    url_last_checked_at=nullable(DATE), findings_summary=S, limitations=S,
)
JOB = obj(
    id=ID, employer_id=ID, title=S, primary_role_category=enum("senior", "cloud", "devops", "platform", "ai", "agent"),
    url=URI, source_id=ID, source_authority=enum("primary", "secondary"), collected_at=DATE,
    posted_at=nullable(DATE), closes_at=nullable(DATE), status=enum("live_description", "expired"),
    location_and_remote_policy=S, kenya_remote_eligibility=S, minimum_years=nullable(N),
    maximum_years=nullable(N), required_skill_ids=IDS, preferred_skill_ids=IDS,
    requirements_summary=S, coding_notes=S, seniority_basis=S, interview_evidence=S,
)
EMPLOYER = obj(
    id=ID, name=S, enabled=B, career_url=URI, watch_keywords=STRINGS, target_locations=STRINGS,
    research_status=S, portal_content_last_verified_at=nullable(DATE), job_ids=IDS,
    source_ids=IDS, observed_requirements=STRINGS, limitations=S,
)
RUBRIC = arr(obj(criterion=S, max_points=I, full_credit=S), minimum=1)
QUESTION = obj(
    id=ID, track_id=ID, skill_ids=IDS, difficulty=enum("foundational", "intermediate", "advanced", "senior"),
    category=S, question=S, expected_answer_elements=STRINGS, detailed_explanation=S,
    follow_up_questions=STRINGS, evaluation_rubric=RUBRIC, common_mistakes=STRINGS,
    source_ids=IDS, authorship=S,
)
PROJECT = obj(
    id=ID, track_ids=IDS, level=enum("exercise", "intermediate", "advanced", "capstone"),
    title=S, problem_statement=S, architecture=S, technologies=STRINGS, skill_ids=IDS,
    engineering_requirements=STRINGS, acceptance_criteria=STRINGS,
    milestones=arr(obj(id=ID, title=S, deliverables=STRINGS, estimated_hours=N), minimum=1),
    estimated_hours=N, testing_strategy=STRINGS, security_considerations=STRINGS,
    deployment_requirements=STRINGS, github_deliverables=STRINGS,
    interview_discussion_points=STRINGS, resource_ids=IDS, cross_track_extensions=S,
    curriculum_scope_note=S,
)
LESSON = obj(
    id=ID, day={"type": "integer", "minimum": 1, "maximum": 60}, track_id=ID, topic=S,
    knowledge_unit_id=ID, skill_ids=IDS, learning_objectives=STRINGS, why_it_matters=S,
    prerequisites=obj(lesson_ids=IDS, skill_ids=IDS, baseline_knowledge=STRINGS, knowledge_to_check=STRINGS, gap_policy=S),
    recommended_youtube_resource_id=ID, video_duration_minutes=nullable(N),
    planned_video_minutes={"type": "integer", "minimum": 0, "maximum": 45},
    video_selection=obj(selection_method=S, focus=S, verified_timestamp_seconds=nullable(I), timestamp_status=S, coverage_limit=S),
    supplementary_reading_resource_ids=IDS, reading_focus=S, practical_implementation_exercise=S,
    interview_question_ids=IDS, revision_exercise=S,
    study_guide=obj(
        before_video=STRINGS, during_video=STRINGS,
        after_video=obj(comprehension_questions=STRINGS, practice=S, validate_understanding=STRINGS),
    ),
    time_budget_minutes=obj(preparation=I, video=I, reading=I, implementation=I, interview=I, revision=I),
    estimated_total_study_minutes={"type": "integer", "minimum": 180, "maximum": 240},
    expected_outcome=S, completion_criteria=STRINGS, project_id=ID,
    phase=enum("concept_and_slice", "comparative_implementation", "failure_and_revision", "capstone_integration"),
    assessment_status=enum("authored_plan_not_learner_executed"),
)
CURRICULUM = obj(
    id=ID, track_id=ID, duration_days=enum(14, 30, 60),
    daily_minutes={"type": "integer", "minimum": 180, "maximum": 240}, total_hours=N,
    scope=S, deliverable_project_id=ID, capstone_completion_level=S,
    adjustment_policy=obj(**{"180_minutes": S, "240_minutes": S, "unfinished_work": S, "waiver": S}),
    lessons=arr(LESSON, minimum=14),
)
SKILL = obj(
    id=ID, name=S, track_ids=IDS, topic_concepts=STRINGS, sample_required_count=I,
    sample_preferred_count=I, sample_mention_count=I, sample_job_ids=IDS,
    learner_leverage=S, practice_requirement=S,
)


def branch(kind, **fields):
    return obj(**{
        "$schema": {"const": "schemas/package.schema.json"},
        "dataset_type": {"const": kind},
        "research_version": {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$"},
        "research_date": DATE,
        **fields,
    })


def make_schema():
    branches = [
        branch("learner",
               profile=obj(
                   professional_experience_years=obj(minimum=N, maximum=N, evidence=S),
                   professional_context=S, existing_exposure=STRINGS, assess_before_skipping=STRINGS,
                   target_roles=STRINGS, target_markets=STRINGS,
                   daily_study_minutes=obj(minimum=I, default=I, maximum=I),
                   learning_preferences=STRINGS, assessment_gate=S, privacy=S,
               ),
               tracks=arr(TRACK, minimum=5),
               active_track_configuration=obj(active_track_id=ID, allow_track_switching=B, default_plan_days=I, completion_storage_design=S),
               recommendation=obj(priority_order=IDS, status=S, rationale=S)),
        branch("employers", employers=arr(EMPLOYER), job_postings=arr(JOB),
               configuration_contract=obj(operation=S, add_employer=S, add_job_description=S, refresh_interval_days=I, eligibility_policy=S)),
        branch("resources", resources=arr(RESOURCE),
               topic_rankings=arr(obj(skill_id=ID, resource_ids_in_order=IDS, interpretation=S))),
        branch("sources", sources=arr(SOURCE), verification_policy=S),
        branch("skills", skills=arr(SKILL),
               track_analyses=arr(obj(
                   track_id=ID, sample_size=I, job_ids=IDS,
                   frequency_rows=arr(obj(skill_id=ID, mention_count=I, required_count=I, preferred_only_count=I, denominator=I)),
                   core_skills_in_sample=IDS, senior_expectations=S, emerging_skills=IDS,
                   emerging_evidence_status=S, niche_skills=IDS, niche_interpretation=S,
                   declining_skills=IDS, decline_status=S, overlapping_skill_ids=IDS,
                   leverage_skill_ids=IDS, new_practice_skill_ids=IDS, limitations=S,
               )),
               methodology=obj(
                   sample_size=I, collection_start=DATE, collection_end=DATE, posting_date_range=S,
                   sampling=S, coding=S, denominator_policy=S, geographic_limits=S, trend_limits=S, refresh_policy=S,
               )),
        branch("projects", projects=arr(PROJECT)),
        branch("questions", questions=arr(QUESTION),
               mock_interviews=arr(obj(
                   id=ID, track_id=ID, duration_minutes=I, scenario=S,
                   stages=arr(obj(minutes=I, task=S)), question_ids=IDS, rubric=S,
               ))),
        branch("curricula", plan_days=enum(14, 30, 60), curricula=arr(CURRICULUM, minimum=5)),
        branch("dependencies",
               skill_dependencies=arr(obj(skill_id=ID, requires_skill_ids=IDS)),
               lesson_dependencies=arr(obj(lesson_id=ID, requires_lesson_ids=IDS)),
               sequencing_policy=S, external_prerequisites=STRINGS, reentry_policy=S),
        branch("shared",
               knowledge_units=arr(obj(id=ID, skill_id=ID, track_ids=IDS, canonical_lesson_id=ID, lesson_ids=IDS, waiver_criteria=S, reuse_boundary=S)),
               shared_core_priority=IDS, equivalence_policy=S,
               provider_comparison=arr(obj(concept=S, azure=S, aws=S, gcp=S, transfer=S, source_ids=IDS))),
    ]
    result = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://engineering-academy.invalid/research/package.schema.json",
        "title": "Engineering Academy research datasets",
        "description": "Explicit structural contracts; semantic IDs, ordering, counts and evidence checks are enforced by tools/validate.py. No remote schema resolution needed.",
        "oneOf": branches,
        "$defs": {
            "Resource": RESOURCE, "Lesson": LESSON, "Project": PROJECT, "Question": QUESTION,
            "Job": JOB, "Source": SOURCE, "Skill": SKILL, "Employer": EMPLOYER,
            "ValidationResult": obj(
                status=enum("passed", "failed"), research_date=DATE, research_version=S,
                validated_dataset_files=I,
                counts=obj(track=I, resource=I, skill=I, employer=I, job=I, project=I, question=I, source=I, knowledge=I, lesson=I),
                curriculum_count=I, schema_draft=S, checks=STRINGS, limitations=STRINGS, errors=STRINGS,
            ),
            "URLCheckResults": obj(
                checked_at={"type": "string", "format": "date-time"}, unique_requests=I,
                method=S, content_verification=S, reachable_count=I, unavailable_count=I,
                results=arr(obj(
                    entity_id=ID, verification_target=URI, url=URI, http_status=nullable(I),
                    final_url=nullable(URI), access_status=enum("reachable", "blocked_or_unavailable", "network_error"),
                    error=nullable(S),
                )),
            ),
        },
    }
    path = Path(__file__).resolve().parents[1] / "schemas"
    path.mkdir(exist_ok=True)
    (path / "package.schema.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    make_schema()
