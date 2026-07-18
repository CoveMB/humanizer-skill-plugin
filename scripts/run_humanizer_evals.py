#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.helpers.output_contracts import validate_case_output  # noqa: E402
from tests.helpers.skill_artifacts import load_fixture_cases  # noqa: E402


DEFAULT_CASES_PATH = REPO_ROOT / "evals" / "humanizer_eval_cases.json"
DEFAULT_ARTIFACTS_DIR = REPO_ROOT / "evals" / "artifacts" / "latest"
DEFAULT_MODEL = "gpt-5.5"
DEFAULT_TIMEOUT_SECONDS = 300
PLUGIN_BOOTSTRAP_TIMEOUT_SECONDS = 60
EVAL_MARKETPLACE_PREFIX = "humanizer-eval"
LOCAL_PLUGIN_NAME = "humanizer-plugin"
PLUGIN_PACKAGE_DIRECTORIES = (".codex-plugin", "skills")
PLUGIN_PACKAGE_FILES = ("README.md", "NOTICE", "LICENSE")
PLUGIN_PROVENANCE_FILENAME = "plugin-provenance.json"
VALID_CATEGORIES = {"explicit", "implicit", "contextual", "negative"}
REQUIRED_CASE_KEYS = {"id", "category", "should_trigger", "prompt", "source"}
DEFAULT_TARGET_SKILL = "editorial-humanizer"
TARGET_SKILL_DISPLAY_NAMES = {
    "editorial-humanizer": "Editorial Humanizer",
    "faithful-humanizer": "Faithful Humanizer",
}
EDITORIAL_PATTERN_CATALOG_PATH = (
    "skills/editorial-humanizer/references/pattern-catalog.md"
)
SCIENTIFIC_REGISTER_PATH = "skills/references/registers/scientific-writing.md"
REFERENCE_TARGET_SKILLS = {
    EDITORIAL_PATTERN_CATALOG_PATH: {"editorial-humanizer"},
    SCIENTIFIC_REGISTER_PATH: set(TARGET_SKILL_DISPLAY_NAMES),
}
DEFAULT_FORBIDDEN_STDERR_TERMS = (
    'plugin="humanizer-plugin" error=invalid marketplace',
    'plugin="humanizer@humanizer-local"',
)
TRACE_METRIC_KEYS = (
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
)
RUBRIC_MAX_DIMENSION_SCORE = 10


@dataclass
class EvalPluginInstallation:
    plugin_id: str
    marketplace_name: str
    version: str
    installed_path: Path
    package_sha256: str
    environment: dict


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require_isolated_codex_home(environment=None):
    environment = os.environ if environment is None else environment
    configured_codex_home = environment.get("CODEX_HOME")
    if not configured_codex_home:
        raise ValueError(
            "CODEX_HOME is required for live evals and must point to an isolated directory"
        )

    user_home = Path(environment.get("HOME", Path.home())).expanduser().resolve()
    codex_home = Path(configured_codex_home).expanduser().resolve()
    if codex_home == user_home / ".codex":
        raise ValueError("CODEX_HOME must not use the default user Codex home")
    if not codex_home.is_dir():
        raise ValueError(f"CODEX_HOME does not exist or is not a directory: {codex_home}")
    return codex_home


def build_eval_environment(codex_home, isolated_home):
    environment = os.environ.copy()
    environment["CODEX_HOME"] = str(Path(codex_home).resolve())
    environment["HOME"] = str(Path(isolated_home).resolve())
    return environment


def stage_eval_marketplace(repo_root, marketplace_root, marketplace_name):
    repo_root = Path(repo_root)
    marketplace_root = Path(marketplace_root)
    plugin_root = marketplace_root / "plugins" / LOCAL_PLUGIN_NAME
    plugin_root.mkdir(parents=True, exist_ok=True)

    for directory_name in PLUGIN_PACKAGE_DIRECTORIES:
        shutil.copytree(
            repo_root / directory_name,
            plugin_root / directory_name,
        )
    for file_name in PLUGIN_PACKAGE_FILES:
        shutil.copy2(repo_root / file_name, plugin_root / file_name)

    marketplace_path = marketplace_root / ".agents" / "plugins" / "marketplace.json"
    marketplace_path.parent.mkdir(parents=True, exist_ok=True)
    marketplace = {
        "name": marketplace_name,
        "interface": {"displayName": "Humanizer Eval"},
        "plugins": [
            {
                "name": LOCAL_PLUGIN_NAME,
                "source": {
                    "source": "local",
                    "path": f"./plugins/{LOCAL_PLUGIN_NAME}",
                },
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_INSTALL",
                },
                "category": "Productivity",
            }
        ],
    }
    marketplace_path.write_text(
        json.dumps(marketplace, indent=2) + "\n",
        encoding="utf-8",
    )
    return plugin_root


def plugin_package_sha256(plugin_root):
    plugin_root = Path(plugin_root)
    digest = hashlib.sha256()
    for directory_name in PLUGIN_PACKAGE_DIRECTORIES:
        directory = plugin_root / directory_name
        for path in sorted(path for path in directory.rglob("*") if path.is_file()):
            relative_path = path.relative_to(plugin_root).as_posix()
            digest.update(relative_path.encode("utf-8"))
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
    return digest.hexdigest()


def run_cli_json(command, environment, label):
    try:
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
            timeout=PLUGIN_BOOTSTRAP_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise RuntimeError(f"{label} failed to run: {error}") from error

    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "no error details"
        raise RuntimeError(f"{label} failed: {detail}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"{label} returned invalid JSON") from error


def validate_eval_plugin_install(repo_root, codex_home, plugin_id, install_result):
    expected_manifest = read_json(Path(repo_root) / ".codex-plugin" / "plugin.json")
    expected_version = expected_manifest["version"]
    if install_result.get("pluginId") != plugin_id:
        raise RuntimeError("eval plugin installation returned the wrong plugin id")
    if install_result.get("version") != expected_version:
        raise RuntimeError(
            "eval plugin installation returned version "
            f"{install_result.get('version')!r}; expected {expected_version!r}"
        )

    installed_path_value = install_result.get("installedPath")
    if not isinstance(installed_path_value, str) or not installed_path_value:
        raise RuntimeError("eval plugin installation did not return an installed path")
    installed_path = Path(installed_path_value).resolve()
    if not installed_path.is_dir():
        raise RuntimeError(f"eval plugin install path does not exist: {installed_path}")
    try:
        installed_path.relative_to(Path(codex_home).resolve())
    except ValueError as error:
        raise RuntimeError("eval plugin was installed outside the isolated CODEX_HOME") from error

    checkout_digest = plugin_package_sha256(repo_root)
    installed_digest = plugin_package_sha256(installed_path)
    if installed_digest != checkout_digest:
        raise RuntimeError("installed eval plugin contents do not match the checkout")

    return {
        "pluginId": plugin_id,
        "version": expected_version,
        "installedPath": str(installed_path),
        "packageSha256": checkout_digest,
    }


def verify_eval_plugin_is_model_visible(
    codex_bin,
    plugin_id,
    installed_path,
    environment,
):
    prompt_input = run_cli_json(
        [
            codex_bin,
            "debug",
            "prompt-input",
            "-c",
            f'plugins."{plugin_id}".enabled=true',
            "Use Editorial Humanizer and Faithful Humanizer to rewrite this text.",
        ],
        environment,
        "eval plugin provenance check",
    )
    expected_skill_paths = [
        (Path(installed_path) / "skills" / target_skill / "SKILL.md").resolve()
        for target_skill in TARGET_SKILL_DISPLAY_NAMES
    ]
    prompt_input_json = json.dumps(prompt_input)
    missing_skill_paths = [
        str(skill_path)
        for skill_path in expected_skill_paths
        if str(skill_path) not in prompt_input_json
    ]
    if missing_skill_paths:
        raise RuntimeError(
            "installed checkout skill(s) are not present in the model-visible prompt input: "
            + ", ".join(missing_skill_paths)
        )
    return [str(skill_path) for skill_path in expected_skill_paths]


def cleanup_eval_plugin(
    codex_bin,
    installation,
    marketplace_added,
    plugin_installed,
):
    errors = []
    if plugin_installed:
        try:
            run_cli_json(
                [codex_bin, "plugin", "remove", installation.plugin_id, "--json"],
                installation.environment,
                "eval plugin removal",
            )
        except RuntimeError as error:
            errors.append(str(error))
    if marketplace_added:
        try:
            run_cli_json(
                [
                    codex_bin,
                    "plugin",
                    "marketplace",
                    "remove",
                    installation.marketplace_name,
                    "--json",
                ],
                installation.environment,
                "eval marketplace removal",
            )
        except RuntimeError as error:
            errors.append(str(error))
    return errors


@contextmanager
def installed_eval_plugin(codex_bin, repo_root, artifacts_dir, codex_home):
    marketplace_name = f"{EVAL_MARKETPLACE_PREFIX}-{uuid.uuid4().hex}"
    plugin_id = f"{LOCAL_PLUGIN_NAME}@{marketplace_name}"
    with tempfile.TemporaryDirectory(prefix="humanizer-eval-runtime-") as temporary_directory:
        temporary_root = Path(temporary_directory)
        isolated_home = temporary_root / "home"
        marketplace_root = temporary_root / "marketplace"
        isolated_home.mkdir()
        staged_plugin_root = stage_eval_marketplace(
            repo_root,
            marketplace_root,
            marketplace_name,
        )
        environment = build_eval_environment(codex_home, isolated_home)
        installation = EvalPluginInstallation(
            plugin_id=plugin_id,
            marketplace_name=marketplace_name,
            version=read_json(Path(repo_root) / ".codex-plugin" / "plugin.json")["version"],
            installed_path=Path(),
            package_sha256=plugin_package_sha256(staged_plugin_root),
            environment=environment,
        )
        marketplace_added = False
        plugin_installed = False
        try:
            marketplace_result = run_cli_json(
                [
                    codex_bin,
                    "plugin",
                    "marketplace",
                    "add",
                    str(marketplace_root),
                    "--json",
                ],
                environment,
                "eval marketplace installation",
            )
            marketplace_added = True
            if marketplace_result.get("marketplaceName") != marketplace_name:
                raise RuntimeError("eval marketplace installation returned the wrong name")

            install_result = run_cli_json(
                [codex_bin, "plugin", "add", plugin_id, "--json"],
                environment,
                "eval plugin installation",
            )
            plugin_installed = True
            provenance = validate_eval_plugin_install(
                repo_root,
                codex_home,
                plugin_id,
                install_result,
            )
            model_visible_skill_paths = verify_eval_plugin_is_model_visible(
                codex_bin,
                plugin_id,
                provenance["installedPath"],
                environment,
            )
            provenance.update(
                {
                    "checkoutPath": str(Path(repo_root).resolve()),
                    "modelVisibleSkillPaths": model_visible_skill_paths,
                }
            )
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            artifacts_dir.joinpath(PLUGIN_PROVENANCE_FILENAME).write_text(
                json.dumps(provenance, indent=2) + "\n",
                encoding="utf-8",
            )
            installation.installed_path = Path(provenance["installedPath"])
            installation.package_sha256 = provenance["packageSha256"]
            yield installation
        finally:
            cleanup_errors = cleanup_eval_plugin(
                codex_bin,
                installation,
                marketplace_added,
                plugin_installed,
            )
            if cleanup_errors:
                message = "; ".join(cleanup_errors)
                if sys.exc_info()[0] is None:
                    raise RuntimeError(message)
                print(f"warning: {message}", file=sys.stderr)


def positive_integer(value):
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be an integer") from error
    if number <= 0:
        raise argparse.ArgumentTypeError("must be greater than 0")
    return number


def require_string(case, key):
    value = case.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{case.get('id', '<unknown>')}: {key} must be a non-empty string")
    return value


def require_string_list(case, key):
    value = case.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{case['id']}: {key} must be a list of strings")
    return value


def require_optional_boolean(case, key):
    value = case.get(key, False)
    if not isinstance(value, bool):
        raise ValueError(f"{case['id']}: {key} must be a boolean")
    return value


def is_strict_integer(value):
    return type(value) is int


def is_positive_integer(value):
    return is_strict_integer(value) and value > 0


def validate_eval_case(case):
    missing_keys = REQUIRED_CASE_KEYS - set(case)
    if missing_keys:
        raise ValueError(f"{case.get('id', '<unknown>')}: missing keys {sorted(missing_keys)}")

    require_string(case, "id")
    require_string(case, "prompt")
    require_string(case, "source")

    if case["category"] not in VALID_CATEGORIES:
        raise ValueError(f"{case['id']}: unsupported category {case['category']!r}")

    if not isinstance(case["should_trigger"], bool):
        raise ValueError(f"{case['id']}: should_trigger must be a boolean")

    require_optional_boolean(case, "force_skill_file_read")
    require_optional_boolean(case, "force_reference_file_read")
    require_string_list(case, "force_reference_file_reads")
    require_string_list(case, "expected_trace_terms")
    require_string_list(case, "forbidden_trace_terms")
    require_string_list(case, "expected_stderr_terms")
    require_string_list(case, "forbidden_stderr_terms")

    target_skill = case.get("target_skill", DEFAULT_TARGET_SKILL)
    if target_skill not in TARGET_SKILL_DISPLAY_NAMES:
        raise ValueError(f"{case['id']}: unsupported target_skill {target_skill!r}")
    for reference_path in reference_paths_for_case(case):
        supported_targets = REFERENCE_TARGET_SKILLS.get(reference_path)
        if supported_targets is None:
            raise ValueError(
                f"{case['id']}: unsupported reference path {reference_path!r}"
            )
        if target_skill not in supported_targets:
            raise ValueError(
                f"{case['id']}: reference {reference_path!r} is not supported for "
                f"{target_skill}"
            )

    output_contract_case_id = case.get("output_contract_case_id")
    if output_contract_case_id is not None and not isinstance(output_contract_case_id, str):
        raise ValueError(f"{case['id']}: output_contract_case_id must be a string")

    rubric_id = case.get("rubric_id")
    if rubric_id is not None and not isinstance(rubric_id, str):
        raise ValueError(f"{case['id']}: rubric_id must be a string")

    return case


def unique_strings(strings):
    return list(dict.fromkeys(strings))


def with_default_forbidden_stderr_terms(case):
    return {
        **case,
        "forbidden_stderr_terms": unique_strings(
            [
                *DEFAULT_FORBIDDEN_STDERR_TERMS,
                *case.get("forbidden_stderr_terms", []),
            ]
        ),
    }


def validate_output_contract_references(cases, output_contract_cases):
    unknown_contract_ids = sorted(
        {
            case["output_contract_case_id"]
            for case in cases
            if case.get("output_contract_case_id")
            and case["output_contract_case_id"] not in output_contract_cases
        }
    )
    if unknown_contract_ids:
        raise ValueError(
            "unknown output contract case id(s): " + ", ".join(unknown_contract_ids)
        )


def normalize_contract_source(source):
    return " ".join(str(source).strip().split())


def validate_output_contract_sources(cases, output_contract_cases):
    mismatches = []
    for case in cases:
        output_contract_case_id = case.get("output_contract_case_id")
        if not output_contract_case_id:
            continue

        contract_case = output_contract_cases[output_contract_case_id]
        if normalize_contract_source(case["source"]) != normalize_contract_source(
            contract_case.get("source", "")
        ):
            mismatches.append(f"{case['id']} -> {output_contract_case_id}")

    if mismatches:
        raise ValueError("output contract source mismatch: " + ", ".join(mismatches))


def require_rubric_score_threshold(rubric_id, rubric, key):
    value = rubric.get(key)
    if not is_positive_integer(value):
        raise ValueError(f"{rubric_id}: rubric {key} must be a positive integer")
    return value


def validate_dimension_score_thresholds(
    rubric_id,
    rubric,
    dimension_names,
):
    thresholds = rubric.get("minimum_dimension_scores", {})
    if not isinstance(thresholds, dict):
        raise ValueError(
            f"{rubric_id}: rubric minimum_dimension_scores must be an object"
        )

    unknown_dimension_names = sorted(set(thresholds) - set(dimension_names))
    if unknown_dimension_names:
        raise ValueError(
            f"{rubric_id}: rubric minimum_dimension_scores has unknown dimension(s): "
            + ", ".join(unknown_dimension_names)
        )

    normalized_thresholds = {}
    for dimension_name, threshold in thresholds.items():
        if not is_positive_integer(threshold):
            raise ValueError(
                f"{rubric_id}: rubric minimum score for {dimension_name} "
                "must be a positive integer"
            )
        if threshold > RUBRIC_MAX_DIMENSION_SCORE:
            raise ValueError(
                f"{rubric_id}: rubric minimum score for {dimension_name} is too high"
            )
        normalized_thresholds[dimension_name] = threshold
    return normalized_thresholds


def validate_rubric_definition(rubric_id, rubric):
    if not isinstance(rubric, dict):
        raise ValueError(f"{rubric_id}: rubric must be an object")

    dimensions = rubric.get("dimensions")
    if not isinstance(dimensions, list) or not dimensions:
        raise ValueError(f"{rubric_id}: rubric dimensions must be a non-empty list")

    dimension_names = []
    normalized_dimensions = []
    for index, dimension in enumerate(dimensions):
        if not isinstance(dimension, dict):
            raise ValueError(f"{rubric_id}: rubric dimension {index} must be an object")

        name = dimension.get("name")
        question = dimension.get("question")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"{rubric_id}: rubric dimension {index} missing name")
        if not isinstance(question, str) or not question.strip():
            raise ValueError(f"{rubric_id}: rubric dimension {name} missing question")

        dimension_names.append(name)
        normalized_dimensions.append({"name": name, "question": question})

    if len(dimension_names) != len(set(dimension_names)):
        raise ValueError(f"{rubric_id}: rubric dimension names must be unique")

    minimum_total_score = require_rubric_score_threshold(
        rubric_id,
        rubric,
        "minimum_total_score",
    )
    minimum_dimension_score = require_rubric_score_threshold(
        rubric_id,
        rubric,
        "minimum_dimension_score",
    )
    if minimum_dimension_score > RUBRIC_MAX_DIMENSION_SCORE:
        raise ValueError(f"{rubric_id}: rubric minimum_dimension_score is too high")
    minimum_dimension_scores = validate_dimension_score_thresholds(
        rubric_id,
        rubric,
        dimension_names,
    )

    maximum_total_score = len(normalized_dimensions) * RUBRIC_MAX_DIMENSION_SCORE
    if minimum_total_score > maximum_total_score:
        raise ValueError(f"{rubric_id}: rubric minimum_total_score is too high")

    return {
        "minimum_total_score": minimum_total_score,
        "minimum_dimension_score": minimum_dimension_score,
        "minimum_dimension_scores": minimum_dimension_scores,
        "dimensions": normalized_dimensions,
    }


def validate_rubrics(rubrics):
    if rubrics is None:
        return {}
    if not isinstance(rubrics, dict):
        raise ValueError("rubrics must be an object")
    return {
        rubric_id: validate_rubric_definition(rubric_id, rubric)
        for rubric_id, rubric in rubrics.items()
    }


def attach_case_rubric(case, rubrics):
    rubric_id = case.get("rubric_id")
    if not rubric_id:
        return case
    if rubric_id not in rubrics:
        raise ValueError(f"{case['id']}: unknown rubric id {rubric_id!r}")
    return {**case, "rubric": rubrics[rubric_id]}


def load_eval_cases(path=DEFAULT_CASES_PATH, output_contract_cases=None):
    data = read_json(Path(path))
    cases = data.get("cases")
    if not isinstance(cases, list):
        raise ValueError("eval case file must contain a cases list")
    rubrics = validate_rubrics(data.get("rubrics", {}))

    seen_case_ids = set()
    validated_cases = []
    for case in cases:
        validate_eval_case(case)
        case = with_default_forbidden_stderr_terms(case)
        case = attach_case_rubric(case, rubrics)
        case_id = case["id"]
        if case_id in seen_case_ids:
            raise ValueError(f"duplicate eval case id: {case_id}")
        seen_case_ids.add(case_id)
        validated_cases.append(case)

    contracts = (
        load_output_contract_cases()
        if output_contract_cases is None
        else output_contract_cases
    )
    validate_output_contract_references(validated_cases, contracts)
    validate_output_contract_sources(validated_cases, contracts)
    return validated_cases


def load_output_contract_cases():
    return {case["id"]: case for case in load_fixture_cases()}


def target_skill_for_case(case):
    return case.get("target_skill", DEFAULT_TARGET_SKILL)


def reference_paths_for_case(case):
    reference_paths = []
    if case.get("force_reference_file_read", False):
        reference_paths.append(EDITORIAL_PATTERN_CATALOG_PATH)
    reference_paths.extend(case.get("force_reference_file_reads", []))
    return unique_strings(reference_paths)


def target_skill_path(case, plugin_root=None):
    skill_path = Path("skills") / target_skill_for_case(case) / "SKILL.md"
    if plugin_root is not None:
        skill_path = Path(plugin_root) / skill_path
    return skill_path


def build_codex_prompt(case, plugin_root=None):
    prompt_lines = []
    target_skill = target_skill_for_case(case)
    target_skill_display_name = TARGET_SKILL_DISPLAY_NAMES[target_skill]
    if case.get("force_skill_file_read", False):
        skill_path = target_skill_path(case, plugin_root=plugin_root)
        prompt_lines.extend(
            [
                f"Read `{skill_path}` before answering.",
                "Reading the skill file is essential for this eval.",
                "",
            ]
        )
    for reference_path_value in reference_paths_for_case(case):
        reference_path = Path(reference_path_value)
        if plugin_root is not None:
            reference_path = Path(plugin_root) / reference_path
        prompt_lines.extend(
            [
                f"Read `{reference_path}` before answering.",
                "Reading this reference is essential for this eval.",
                "",
            ]
        )

    prompt_lines.extend(
        [
            case["prompt"].strip(),
            "",
            "<source>",
            case["source"].strip(),
            "</source>",
            "",
            "Do not edit repository files.",
            "Do not run shell commands unless they are essential to answer this prompt.",
        ]
    )

    if case["should_trigger"]:
        prompt_lines.append(
            f"Return only the final {target_skill_display_name} output, with no eval commentary."
        )
    else:
        prompt_lines.append("Return only the final answer, with no eval commentary.")

    return "\n".join(prompt_lines)


def build_rubric_prompt(case, output_text):
    rubric = case["rubric"]
    minimum_scores_by_dimension = {
        dimension["name"]: rubric.get("minimum_dimension_scores", {}).get(
            dimension["name"],
            rubric["minimum_dimension_score"],
        )
        for dimension in rubric["dimensions"]
    }
    expected_schema = {
        "case_id": case["id"],
        "scores": {
            dimension["name"]: {
                "score": f"integer 1-{RUBRIC_MAX_DIMENSION_SCORE}",
                "rationale": "short reason",
            }
            for dimension in rubric["dimensions"]
        },
        "total_score": "sum of dimension scores",
        "passed": "boolean",
        "issues": ["short issue strings, empty if none"],
    }
    return "\n".join(
        [
            "Grade this Humanizer eval output against the rubric.",
            "Use only the source and output below. Do not infer outside facts.",
            f"Minimum total score: {rubric['minimum_total_score']}",
            f"Minimum dimension score: {rubric['minimum_dimension_score']}",
            "Minimum score by dimension: "
            + json.dumps(minimum_scores_by_dimension, sort_keys=True),
            "",
            "<rubric>",
            json.dumps(rubric["dimensions"], indent=2),
            "</rubric>",
            "",
            "<source>",
            case["source"].strip(),
            "</source>",
            "",
            "<output>",
            output_text.strip(),
            "</output>",
            "",
            "Return only JSON matching this schema:",
            json.dumps(expected_schema, indent=2),
        ]
    )


def parse_jsonl_events(jsonl_text):
    events = []
    for line_number, line in enumerate(jsonl_text.splitlines(), start=1):
        stripped_line = line.strip()
        if not stripped_line:
            continue
        try:
            events.append(json.loads(stripped_line))
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid JSONL on line {line_number}: {error}") from error
    if not events:
        raise ValueError("no JSONL events found in Codex trace")
    return events


def iter_trace_observation_strings(event):
    item = event.get("item") if isinstance(event, dict) else None
    if not isinstance(item, dict):
        return

    path = item.get("path")
    if isinstance(path, str):
        yield path

    if item.get("type") == "command_execution":
        for key in ("command", "aggregated_output"):
            value = item.get(key)
            if isinstance(value, str):
                yield value


def trace_contains_term(events, term):
    lowered_term = term.lower()
    return any(
        lowered_term in text.lower()
        for event in events
        for text in iter_trace_observation_strings(event)
    )


def empty_trace_metrics():
    return {
        "command_count": 0,
        **{metric_key: 0 for metric_key in TRACE_METRIC_KEYS},
    }


def collect_trace_metrics(events):
    metrics = empty_trace_metrics()
    for event in events:
        item = event.get("item") if isinstance(event, dict) else None
        if (
            isinstance(event, dict)
            and event.get("type") == "item.completed"
            and isinstance(item, dict)
            and item.get("type") == "command_execution"
        ):
            metrics["command_count"] += 1

        usage = event.get("usage") if isinstance(event, dict) else None
        if isinstance(usage, dict):
            for metric_key in TRACE_METRIC_KEYS:
                value = usage.get(metric_key, 0)
                if is_strict_integer(value):
                    metrics[metric_key] += value
    return metrics


def check_trace_expectations(case, events):
    for expected_term in case.get("expected_trace_terms", []):
        if not trace_contains_term(events, expected_term):
            raise AssertionError(f"{case['id']}: missing trace term {expected_term!r}")

    for forbidden_term in case.get("forbidden_trace_terms", []):
        if trace_contains_term(events, forbidden_term):
            raise AssertionError(f"{case['id']}: forbidden trace term present {forbidden_term!r}")


def check_stderr_expectations(case, stderr_text):
    lowered_stderr = stderr_text.lower()

    for expected_term in case.get("expected_stderr_terms", []):
        expanded_expected_term = expected_term.format(repo_root=REPO_ROOT)
        if expanded_expected_term.lower() not in lowered_stderr:
            raise AssertionError(f"{case['id']}: missing stderr term {expected_term!r}")

    for forbidden_term in case.get("forbidden_stderr_terms", []):
        expanded_forbidden_term = forbidden_term.format(repo_root=REPO_ROOT)
        if expanded_forbidden_term.lower() in lowered_stderr:
            raise AssertionError(f"{case['id']}: forbidden stderr term present {forbidden_term!r}")


def build_codex_command(
    codex_bin,
    repo_root,
    output_path,
    prompt,
    model=None,
    plugin_id=None,
):
    command = [
        codex_bin,
        "exec",
        "--ignore-user-config",
        "--ignore-rules",
        "--ephemeral",
        "--json",
        "--sandbox",
        "read-only",
        "--cd",
        str(repo_root),
        "--output-last-message",
        str(output_path),
    ]

    if plugin_id:
        command.extend(
            [
                "-c",
                f'plugins."{plugin_id}".enabled=true',
            ]
        )

    if model:
        command.extend(["--model", model])

    command.append(prompt)
    return command


def process_output_text(output):
    if output is None:
        return ""
    if isinstance(output, bytes):
        return output.decode("utf-8", errors="replace")
    return str(output)


def run_codex_process(
    command,
    trace_path,
    stderr_path,
    timeout_seconds,
    case_id,
    label,
    environment=None,
):
    try:
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout_seconds,
            env=environment,
        )
    except subprocess.TimeoutExpired as error:
        trace_path.write_text(
            process_output_text(getattr(error, "stdout", None) or error.output),
            encoding="utf-8",
        )
        stderr_path.write_text(process_output_text(error.stderr), encoding="utf-8")
        raise AssertionError(
            f"{case_id}: {label} timed out after {timeout_seconds} seconds"
        ) from error
    except OSError as error:
        trace_path.write_text("", encoding="utf-8")
        stderr_path.write_text(str(error), encoding="utf-8")
        raise AssertionError(f"{case_id}: failed to start {label}: {error}") from error

    trace_path.write_text(result.stdout, encoding="utf-8")
    stderr_path.write_text(result.stderr, encoding="utf-8")
    return result


def ensure_artifact_dirs(artifacts_dir):
    traces_dir = artifacts_dir / "traces"
    outputs_dir = artifacts_dir / "outputs"
    stderr_dir = artifacts_dir / "stderr"
    prompts_dir = artifacts_dir / "prompts"
    rubric_traces_dir = artifacts_dir / "rubric-traces"
    rubric_outputs_dir = artifacts_dir / "rubric-outputs"
    rubric_stderr_dir = artifacts_dir / "rubric-stderr"
    rubric_prompts_dir = artifacts_dir / "rubric-prompts"
    for directory in (
        traces_dir,
        outputs_dir,
        stderr_dir,
        prompts_dir,
        rubric_traces_dir,
        rubric_outputs_dir,
        rubric_stderr_dir,
        rubric_prompts_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)
    return {
        "traces": traces_dir,
        "outputs": outputs_dir,
        "stderr": stderr_dir,
        "prompts": prompts_dir,
        "rubric_traces": rubric_traces_dir,
        "rubric_outputs": rubric_outputs_dir,
        "rubric_stderr": rubric_stderr_dir,
        "rubric_prompts": rubric_prompts_dir,
    }


def validate_case_output_contract(eval_case, output_text, output_contract_cases):
    contract_case_id = eval_case.get("output_contract_case_id")
    if not contract_case_id:
        return

    if contract_case_id not in output_contract_cases:
        raise AssertionError(
            f"{eval_case['id']}: unknown output contract case {contract_case_id!r}"
        )

    validate_case_output(output_contract_cases[contract_case_id], output_text)


def remove_file_if_exists(path):
    try:
        path.unlink()
    except FileNotFoundError:
        return


def read_final_output(case, output_path):
    if not output_path.exists():
        raise AssertionError(f"{case['id']}: missing final output file {output_path}")
    return output_path.read_text(encoding="utf-8")


def require_rubric_grade_score(case_id, dimension_name, score_entry):
    if not isinstance(score_entry, dict):
        raise AssertionError(f"{case_id}: rubric score {dimension_name} must be an object")

    score = score_entry.get("score")
    if (
        not is_strict_integer(score)
        or score < 1
        or score > RUBRIC_MAX_DIMENSION_SCORE
    ):
        raise AssertionError(f"{case_id}: rubric score {dimension_name} is invalid")

    rationale = score_entry.get("rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        raise AssertionError(f"{case_id}: rubric score {dimension_name} missing rationale")
    return score


def validate_rubric_grade(case, grade):
    case_id = case["id"]
    rubric = case["rubric"]
    if not isinstance(grade, dict):
        raise AssertionError(f"{case_id}: rubric grade must be an object")
    if grade.get("case_id") != case_id:
        raise AssertionError(f"{case_id}: rubric grade has wrong case_id")

    scores = grade.get("scores")
    if not isinstance(scores, dict):
        raise AssertionError(f"{case_id}: rubric grade scores must be an object")

    expected_names = [dimension["name"] for dimension in rubric["dimensions"]]
    if set(scores) != set(expected_names):
        raise AssertionError(f"{case_id}: rubric grade dimensions do not match rubric")

    dimension_scores = {
        name: require_rubric_grade_score(case_id, name, scores[name])
        for name in expected_names
    }
    total_score = sum(dimension_scores.values())
    if grade.get("total_score") != total_score:
        raise AssertionError(f"{case_id}: rubric total_score does not match scores")

    minimum_dimension_scores = rubric.get("minimum_dimension_scores", {})
    violations = []
    for name, score in dimension_scores.items():
        minimum_score = minimum_dimension_scores.get(
            name,
            rubric["minimum_dimension_score"],
        )
        if score < minimum_score:
            violations.append(
                f"{case_id}: {name} score {score} below minimum {minimum_score}"
            )
    if total_score < rubric["minimum_total_score"]:
        violations.append(
            f"{case_id}: total_score {total_score} below minimum {rubric['minimum_total_score']}"
        )

    computed_passed = not violations
    if grade.get("passed") is not computed_passed:
        violations.append(f"{case_id}: rubric passed flag does not match scores")

    issues = grade.get("issues")
    if not isinstance(issues, list) or not all(isinstance(issue, str) for issue in issues):
        violations.append(f"{case_id}: rubric issues must be a list of strings")

    if violations:
        raise AssertionError("\n".join(violations))
    return {
        "rubric_passed": True,
        "rubric_total_score": total_score,
        "rubric_dimension_scores": dimension_scores,
    }


def read_rubric_grade(case, rubric_output_path):
    if not rubric_output_path.exists():
        raise AssertionError(f"{case['id']}: missing rubric output file {rubric_output_path}")
    try:
        return json.loads(rubric_output_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise AssertionError(f"{case['id']}: invalid rubric JSON: {error}") from error


def run_rubric_grade(
    case,
    output_text,
    artifact_dirs,
    codex_bin,
    model=None,
    timeout_seconds=DEFAULT_TIMEOUT_SECONDS,
    environment=None,
):
    rubric_prompt_path = artifact_dirs["rubric_prompts"] / f"{case['id']}.txt"
    rubric_output_path = artifact_dirs["rubric_outputs"] / f"{case['id']}.json"
    rubric_trace_path = artifact_dirs["rubric_traces"] / f"{case['id']}.jsonl"
    rubric_stderr_path = artifact_dirs["rubric_stderr"] / f"{case['id']}.stderr"
    prompt = build_rubric_prompt(case, output_text)

    rubric_prompt_path.write_text(prompt, encoding="utf-8")
    remove_file_if_exists(rubric_output_path)
    command = build_codex_command(
        codex_bin,
        REPO_ROOT,
        rubric_output_path,
        prompt,
        model=model,
    )
    result = run_codex_process(
        command,
        rubric_trace_path,
        rubric_stderr_path,
        timeout_seconds,
        case["id"],
        "rubric grader",
        environment=environment,
    )
    if result.returncode != 0:
        raise AssertionError(f"{case['id']}: rubric grader exited with {result.returncode}")

    grade = read_rubric_grade(case, rubric_output_path)
    return {
        "rubric_prompt_path": str(rubric_prompt_path),
        "rubric_output_path": str(rubric_output_path),
        "rubric_trace_path": str(rubric_trace_path),
        "rubric_stderr_path": str(rubric_stderr_path),
        **validate_rubric_grade(case, grade),
    }


def run_eval_case(
    case,
    artifact_dirs,
    codex_bin,
    output_contract_cases,
    model=None,
    timeout_seconds=DEFAULT_TIMEOUT_SECONDS,
    grade_rubric=False,
    plugin_id=None,
    plugin_root=None,
    environment=None,
):
    prompt = build_codex_prompt(case, plugin_root=plugin_root)
    output_path = artifact_dirs["outputs"] / f"{case['id']}.txt"
    trace_path = artifact_dirs["traces"] / f"{case['id']}.jsonl"
    stderr_path = artifact_dirs["stderr"] / f"{case['id']}.stderr"
    prompt_path = artifact_dirs["prompts"] / f"{case['id']}.txt"

    summary = {
        "id": case["id"],
        "category": case["category"],
        "target_skill": target_skill_for_case(case),
        "returncode": None,
        "trace_path": str(trace_path),
        "output_path": str(output_path),
        "stderr_path": str(stderr_path),
        "prompt_path": str(prompt_path),
        "passed": False,
        "error": None,
        "rubric_passed": None,
        "rubric_error": None,
        "rubric_total_score": None,
        **empty_trace_metrics(),
    }

    prompt_path.write_text(prompt, encoding="utf-8")
    remove_file_if_exists(output_path)
    command = build_codex_command(
        codex_bin,
        REPO_ROOT,
        output_path,
        prompt,
        model=model,
        plugin_id=plugin_id,
    )
    try:
        result = run_codex_process(
            command,
            trace_path,
            stderr_path,
            timeout_seconds,
            case["id"],
            "codex",
            environment=environment,
        )
    except AssertionError as error:
        summary["error"] = str(error)
        return summary

    summary["returncode"] = result.returncode

    try:
        if result.returncode != 0:
            raise AssertionError(f"{case['id']}: codex exited with {result.returncode}")

        events = parse_jsonl_events(result.stdout)
        metrics = collect_trace_metrics(events)
        summary.update(metrics)
        check_trace_expectations(case, events)
        check_stderr_expectations(case, result.stderr)

        output_text = read_final_output(case, output_path)
        validate_case_output_contract(case, output_text, output_contract_cases)
        if grade_rubric and case.get("rubric"):
            try:
                summary.update(
                    run_rubric_grade(
                        case,
                        output_text,
                        artifact_dirs,
                        codex_bin=codex_bin,
                        model=model,
                        timeout_seconds=timeout_seconds,
                        environment=environment,
                    )
                )
            except (AssertionError, OSError, ValueError, subprocess.TimeoutExpired) as error:
                summary["rubric_error"] = str(error)
                raise
    except (AssertionError, OSError, ValueError, subprocess.TimeoutExpired) as error:
        summary["error"] = str(error)
        return summary

    summary["passed"] = True
    return summary


def select_cases(cases, filters):
    if not filters:
        return cases

    selected_ids = set(filters)
    selected_cases = [case for case in cases if case["id"] in selected_ids]
    missing_ids = selected_ids - {case["id"] for case in selected_cases}
    if missing_ids:
        raise ValueError(f"unknown eval case id(s): {', '.join(sorted(missing_ids))}")
    return selected_cases


def write_summary(artifacts_dir, summaries):
    summary_path = artifacts_dir / "summary.json"
    summary_path.write_text(json.dumps({"results": summaries}, indent=2), encoding="utf-8")
    return summary_path


def run_eval_suite(
    cases,
    artifacts_dir,
    codex_bin,
    model=None,
    timeout_seconds=DEFAULT_TIMEOUT_SECONDS,
    grade_rubric=False,
):
    artifact_dirs = ensure_artifact_dirs(artifacts_dir)
    remove_file_if_exists(artifacts_dir / PLUGIN_PROVENANCE_FILENAME)
    output_contract_cases = load_output_contract_cases()
    codex_home = require_isolated_codex_home()
    with installed_eval_plugin(
        codex_bin,
        REPO_ROOT,
        artifacts_dir,
        codex_home,
    ) as installation:
        summaries = [
            run_eval_case(
                case,
                artifact_dirs,
                codex_bin=codex_bin,
                output_contract_cases=output_contract_cases,
                model=model,
                timeout_seconds=timeout_seconds,
                grade_rubric=grade_rubric,
                plugin_id=installation.plugin_id,
                plugin_root=installation.installed_path,
                environment=installation.environment,
            )
            for case in cases
        ]
    summary_path = write_summary(artifacts_dir, summaries)
    return summaries, summary_path


def print_dry_run(cases):
    print(f"would run {len(cases)} Humanizer eval case(s)")
    for case in cases:
        trigger_label = "trigger" if case["should_trigger"] else "no-trigger"
        print(
            f"- {case['id']} "
            f"[{target_skill_for_case(case)}, {case['category']}, {trigger_label}]"
        )


def print_summary(summaries, summary_path):
    passed_count = sum(1 for summary in summaries if summary["passed"])
    print(f"passed {passed_count}/{len(summaries)} Humanizer eval case(s)")
    print(f"summary: {summary_path}")

    for summary in summaries:
        if not summary["passed"]:
            print(f"- {summary['id']}: {summary['error']}", file=sys.stderr)


def build_parser():
    parser = argparse.ArgumentParser(description="Run live Codex evals for Humanizer skills.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES_PATH)
    parser.add_argument("--artifacts-dir", type=Path, default=DEFAULT_ARTIFACTS_DIR)
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument(
        "--timeout-seconds",
        type=positive_integer,
        default=DEFAULT_TIMEOUT_SECONDS,
    )
    parser.add_argument("--filter", action="append", default=[])
    parser.add_argument("--rubric-grade", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv):
    parser = build_parser()
    args = parser.parse_args(argv[1:])

    try:
        cases = select_cases(load_eval_cases(args.cases), args.filter)
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2

    if args.dry_run:
        print_dry_run(cases)
        return 0

    try:
        summaries, summary_path = run_eval_suite(
            cases,
            artifacts_dir=args.artifacts_dir,
            codex_bin=args.codex_bin,
            model=args.model,
            timeout_seconds=args.timeout_seconds,
            grade_rubric=args.rubric_grade,
        )
    except (OSError, RuntimeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    print_summary(summaries, summary_path)
    return 0 if all(summary["passed"] for summary in summaries) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
