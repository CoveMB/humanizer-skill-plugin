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

from scripts.editorial_diagnostics import analyze_text  # noqa: E402
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
    "plain-language-humanizer": "Plain Language Humanizer",
}
FAITHFUL_TARGET_SKILL = "faithful-humanizer"
VALID_FAITHFUL_MODES = ("structural", "conservative")
PLAIN_LANGUAGE_TARGET_SKILL = "plain-language-humanizer"
VALID_PLAIN_LANGUAGE_MODES = ("rewrite", "explain")
FAITHFUL_MODE_DIMENSIONS_KEY = "faithful_mode_dimensions"
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
            "Use Editorial Humanizer, Faithful Humanizer, and Plain Language "
            "Humanizer to rewrite this text.",
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


def validate_plain_language_mode(record_id, target_skill, plain_language_mode):
    if target_skill == PLAIN_LANGUAGE_TARGET_SKILL:
        if plain_language_mode not in VALID_PLAIN_LANGUAGE_MODES:
            raise ValueError(
                f"{record_id}: plain_language_mode must be one of "
                f"{', '.join(VALID_PLAIN_LANGUAGE_MODES)}"
            )
    elif plain_language_mode is not None:
        raise ValueError(
            f"{record_id}: plain_language_mode is only valid for "
            f"{PLAIN_LANGUAGE_TARGET_SKILL}"
        )


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
    require_optional_boolean(case, "activation_probe")
    require_string_list(case, "force_reference_file_reads")
    require_string_list(case, "expected_trace_terms")
    require_string_list(case, "forbidden_trace_terms")
    require_string_list(case, "expected_stderr_terms")
    require_string_list(case, "forbidden_stderr_terms")

    target_skill = case.get("target_skill", DEFAULT_TARGET_SKILL)
    if target_skill not in TARGET_SKILL_DISPLAY_NAMES:
        raise ValueError(f"{case['id']}: unsupported target_skill {target_skill!r}")
    faithful_mode = case.get("faithful_mode")
    if target_skill == FAITHFUL_TARGET_SKILL:
        if faithful_mode not in VALID_FAITHFUL_MODES:
            raise ValueError(
                f"{case['id']}: faithful_mode must be one of "
                f"{', '.join(VALID_FAITHFUL_MODES)}"
            )
    elif faithful_mode is not None:
        raise ValueError(
            f"{case['id']}: faithful_mode is only valid for {FAITHFUL_TARGET_SKILL}"
        )
    validate_plain_language_mode(
        case["id"],
        target_skill,
        case.get("plain_language_mode"),
    )
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


def validate_output_contract_modes(cases, output_contract_cases):
    mismatches_by_field = {
        "faithful_mode": [],
        "plain_language_mode": [],
    }
    for case in cases:
        output_contract_case_id = case.get("output_contract_case_id")
        if not output_contract_case_id:
            continue

        contract_case = output_contract_cases[output_contract_case_id]
        for mode_field in ("faithful_mode", "plain_language_mode"):
            contract_mode = contract_case.get(mode_field)
            if case.get(mode_field) != contract_mode:
                mismatches_by_field[mode_field].append(
                    f"{case['id']} -> {output_contract_case_id}"
                )

    for mode_field in ("faithful_mode", "plain_language_mode"):
        mismatches = mismatches_by_field[mode_field]
        if mismatches:
            raise ValueError(
                f"output contract {mode_field} mismatch: " + ", ".join(mismatches)
            )


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


def validate_rubric_dimension(rubric_id, dimension, label):
    if not isinstance(dimension, dict):
        raise ValueError(f"{rubric_id}: rubric {label} must be an object")

    name = dimension.get("name")
    question = dimension.get("question")
    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"{rubric_id}: rubric {label} missing name")
    if not isinstance(question, str) or not question.strip():
        raise ValueError(f"{rubric_id}: rubric dimension {name} missing question")
    return {"name": name, "question": question}


def validate_faithful_mode_dimensions(rubric_id, rubric, shared_dimension_names):
    mode_dimensions = rubric.get(FAITHFUL_MODE_DIMENSIONS_KEY)
    if mode_dimensions is None:
        return {}
    if not isinstance(mode_dimensions, dict):
        raise ValueError(
            f"{rubric_id}: rubric {FAITHFUL_MODE_DIMENSIONS_KEY} must be an object"
        )

    missing_modes = set(VALID_FAITHFUL_MODES) - set(mode_dimensions)
    unknown_modes = set(mode_dimensions) - set(VALID_FAITHFUL_MODES)
    if missing_modes or unknown_modes:
        raise ValueError(
            f"{rubric_id}: rubric {FAITHFUL_MODE_DIMENSIONS_KEY} must define "
            + ", ".join(VALID_FAITHFUL_MODES)
        )

    normalized_dimensions = {
        mode: validate_rubric_dimension(
            rubric_id,
            mode_dimensions[mode],
            f"{mode} mode dimension",
        )
        for mode in VALID_FAITHFUL_MODES
    }
    mode_dimension_names = [
        dimension["name"] for dimension in normalized_dimensions.values()
    ]
    if set(mode_dimension_names) & set(shared_dimension_names):
        raise ValueError(
            f"{rubric_id}: mode dimension names must differ from shared dimensions"
        )
    if len(mode_dimension_names) != len(set(mode_dimension_names)):
        raise ValueError(f"{rubric_id}: mode dimension names must be unique")
    return normalized_dimensions


def validate_rubric_definition(rubric_id, rubric):
    if not isinstance(rubric, dict):
        raise ValueError(f"{rubric_id}: rubric must be an object")

    dimensions = rubric.get("dimensions")
    if not isinstance(dimensions, list) or not dimensions:
        raise ValueError(f"{rubric_id}: rubric dimensions must be a non-empty list")

    dimension_names = []
    normalized_dimensions = []
    for index, dimension in enumerate(dimensions):
        normalized_dimension = validate_rubric_dimension(
            rubric_id,
            dimension,
            f"dimension {index}",
        )
        dimension_names.append(normalized_dimension["name"])
        normalized_dimensions.append(normalized_dimension)

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
    faithful_mode_dimensions = validate_faithful_mode_dimensions(
        rubric_id,
        rubric,
        dimension_names,
    )

    dimension_count = len(normalized_dimensions) + bool(faithful_mode_dimensions)
    maximum_total_score = dimension_count * RUBRIC_MAX_DIMENSION_SCORE
    if minimum_total_score > maximum_total_score:
        raise ValueError(f"{rubric_id}: rubric minimum_total_score is too high")

    return {
        "minimum_total_score": minimum_total_score,
        "minimum_dimension_score": minimum_dimension_score,
        "minimum_dimension_scores": minimum_dimension_scores,
        "dimensions": normalized_dimensions,
        FAITHFUL_MODE_DIMENSIONS_KEY: faithful_mode_dimensions,
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
    rubric = rubrics[rubric_id]
    mode_dimensions = rubric.get(FAITHFUL_MODE_DIMENSIONS_KEY, {})
    if not mode_dimensions:
        return {**case, "rubric": rubric}
    if target_skill_for_case(case) != FAITHFUL_TARGET_SKILL:
        raise ValueError(
            f"{case['id']}: rubric {rubric_id!r} requires a Faithful target"
        )
    faithful_mode = case["faithful_mode"]
    selected_rubric = {
        **rubric,
        "dimensions": [
            *rubric["dimensions"],
            mode_dimensions[faithful_mode],
        ],
        "faithful_mode": faithful_mode,
    }
    return {**case, "rubric": selected_rubric}


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
    validate_output_contract_modes(validated_cases, contracts)
    return validated_cases


def load_rubric_calibrations(path=DEFAULT_CASES_PATH):
    data = read_json(Path(path))
    rubrics = validate_rubrics(data.get("rubrics", {}))
    calibrations = data.get("rubric_calibrations")
    if not isinstance(calibrations, list) or not calibrations:
        raise ValueError("eval case file must contain rubric_calibrations")

    seen_ids = set()
    validated_calibrations = []
    for calibration in calibrations:
        calibration_id = require_string(calibration, "id")
        require_string(calibration, "source")
        require_string(calibration, "output")
        rubric_id = require_string(calibration, "rubric_id")
        if rubric_id not in rubrics:
            raise ValueError(
                f"{calibration_id}: unknown rubric id {rubric_id!r}"
            )
        if not isinstance(calibration.get("expected_pass"), bool):
            raise ValueError(f"{calibration_id}: expected_pass must be a boolean")
        if calibration_id in seen_ids:
            raise ValueError(f"duplicate rubric calibration id: {calibration_id}")
        seen_ids.add(calibration_id)
        rubric = rubrics[rubric_id]
        normalized_calibration = dict(calibration)
        if rubric.get(FAITHFUL_MODE_DIMENSIONS_KEY):
            faithful_mode = calibration.get("faithful_mode")
            if faithful_mode not in VALID_FAITHFUL_MODES:
                raise ValueError(
                    f"{calibration_id}: faithful_mode must be one of "
                    f"{', '.join(VALID_FAITHFUL_MODES)}"
                )
            normalized_calibration["target_skill"] = FAITHFUL_TARGET_SKILL
        target_skill = normalized_calibration.get(
            "target_skill",
            DEFAULT_TARGET_SKILL,
        )
        validate_plain_language_mode(
            calibration_id,
            target_skill,
            calibration.get("plain_language_mode"),
        )
        validated_calibrations.append(
            attach_case_rubric(normalized_calibration, rubrics)
        )
    return validated_calibrations


def load_output_contract_cases():
    return {case["id"]: case for case in load_fixture_cases()}


def target_skill_for_case(case):
    return case.get("target_skill", DEFAULT_TARGET_SKILL)


def faithful_mode_for_case(case):
    if target_skill_for_case(case) != FAITHFUL_TARGET_SKILL:
        return None
    return case.get("faithful_mode")


def plain_language_mode_for_case(case):
    if target_skill_for_case(case) != PLAIN_LANGUAGE_TARGET_SKILL:
        return None
    return case.get("plain_language_mode")


def editorial_diagnostics_for_case(case, text):
    if target_skill_for_case(case) != DEFAULT_TARGET_SKILL or not case["should_trigger"]:
        return None
    return analyze_text(text)


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
                "Read the complete skill file from its first line through EOF; "
                "if output is truncated or paginated, continue until EOF.",
                "Reading every section of the skill file is essential for this eval.",
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
                "Read the complete reference from its first line through EOF; "
                "if output is truncated or paginated, continue until EOF.",
                "Reading every section of this reference is essential for this eval.",
                "",
            ]
        )

    plain_language_mode = plain_language_mode_for_case(case)
    if plain_language_mode:
        prompt_lines.extend([f"Plain Language mode: {plain_language_mode}.", ""])

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

    if case.get("activation_probe", False):
        prompt_lines.append("Return only the final answer, with no eval commentary.")
    elif case["should_trigger"]:
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
    prompt_lines = [
            "Grade this Humanizer eval output against the rubric.",
            "Use only the user request, source, and output below. Do not infer outside facts.",
            "Evaluate rewritten prose against the source and evaluate explanatory or "
            "audit sections against the user request.",
            "Do not treat user-requested labels or audit explanations as added source "
            "propositions, broader rewriting, or a voice change. Do penalize any "
            "unsupported claim inside those sections.",
            f"Minimum total score: {rubric['minimum_total_score']}",
            f"Minimum dimension score: {rubric['minimum_dimension_score']}",
            "Minimum score by dimension: "
            + json.dumps(minimum_scores_by_dimension, sort_keys=True),
    ]
    faithful_mode = faithful_mode_for_case(case)
    if faithful_mode:
        prompt_lines.append(f"Faithful intervention mode: {faithful_mode}.")
    plain_language_mode = plain_language_mode_for_case(case)
    if plain_language_mode:
        prompt_lines.append(f"Plain Language mode: {plain_language_mode}.")
    prompt_lines.extend(
        [
            "",
            "<rubric>",
            json.dumps(rubric["dimensions"], indent=2),
            "</rubric>",
            "",
            "<user_request>",
            case.get(
                "prompt",
                "Rewrite the source faithfully while improving only its surface form.",
            ).strip(),
            "</user_request>",
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
    return "\n".join(prompt_lines)


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
        command = item.get("command")
        if isinstance(command, str):
            yield command


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
    working_directory,
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
        "--skip-git-repo-check",
        "--json",
        "--sandbox",
        "read-only",
        "--cd",
        str(working_directory),
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


def validate_rubric_grade(case, grade, require_pass=True):
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
    score_violations = []
    for name, score in dimension_scores.items():
        minimum_score = minimum_dimension_scores.get(
            name,
            rubric["minimum_dimension_score"],
        )
        if score < minimum_score:
            score_violations.append(
                f"{case_id}: {name} score {score} below minimum {minimum_score}"
            )
    if total_score < rubric["minimum_total_score"]:
        score_violations.append(
            f"{case_id}: total_score {total_score} below minimum {rubric['minimum_total_score']}"
        )

    computed_passed = not score_violations
    schema_violations = []
    if grade.get("passed") is not computed_passed:
        schema_violations.append(
            f"{case_id}: rubric passed flag does not match scores"
        )

    issues = grade.get("issues")
    if not isinstance(issues, list) or not all(isinstance(issue, str) for issue in issues):
        schema_violations.append(
            f"{case_id}: rubric issues must be a list of strings"
        )

    validation_violations = (
        [*score_violations, *schema_violations]
        if require_pass
        else schema_violations
    )
    if validation_violations:
        raise AssertionError("\n".join(validation_violations))
    return {
        "rubric_passed": computed_passed,
        "rubric_total_score": total_score,
        "rubric_dimension_scores": dimension_scores,
        "rubric_score_violations": score_violations,
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
    artifact_stem=None,
    require_pass=True,
):
    artifact_stem = case["id"] if artifact_stem is None else artifact_stem
    rubric_prompt_path = artifact_dirs["rubric_prompts"] / f"{artifact_stem}.txt"
    rubric_output_path = artifact_dirs["rubric_outputs"] / f"{artifact_stem}.json"
    rubric_trace_path = artifact_dirs["rubric_traces"] / f"{artifact_stem}.jsonl"
    rubric_stderr_path = artifact_dirs["rubric_stderr"] / f"{artifact_stem}.stderr"
    prompt = build_rubric_prompt(case, output_text)

    rubric_prompt_path.write_text(prompt, encoding="utf-8")
    remove_file_if_exists(rubric_output_path)
    command = build_codex_command(
        codex_bin,
        artifact_dirs["rubric_prompts"].parent.resolve(),
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
        **validate_rubric_grade(case, grade, require_pass=require_pass),
    }


def run_rubric_calibration_suite(
    calibrations,
    artifacts_dir,
    codex_bin,
    model=None,
    timeout_seconds=DEFAULT_TIMEOUT_SECONDS,
):
    require_isolated_codex_home()
    artifact_dirs = ensure_artifact_dirs(artifacts_dir)
    summaries = []
    for calibration in calibrations:
        summary = {
            "id": calibration["id"],
            "target_skill": "rubric-calibration",
            "expected_pass": calibration["expected_pass"],
            "passed": False,
            "error": None,
            "failure_stage": "rubric_calibration",
        }
        try:
            grade_summary = run_rubric_grade(
                calibration,
                calibration["output"],
                artifact_dirs,
                codex_bin=codex_bin,
                model=model,
                timeout_seconds=timeout_seconds,
                environment=os.environ.copy(),
                artifact_stem=calibration["id"],
                require_pass=False,
            )
            summary.update(grade_summary)
            actual_pass = grade_summary["rubric_passed"]
            if actual_pass != calibration["expected_pass"]:
                raise AssertionError(
                    f"{calibration['id']}: rubric returned passed={actual_pass}; "
                    f"expected {calibration['expected_pass']}"
                )
        except (AssertionError, OSError, ValueError, subprocess.TimeoutExpired) as error:
            summary["error"] = str(error)
        else:
            summary["passed"] = True
            summary["failure_stage"] = None
        summaries.append(summary)

    summary_path = write_summary(
        artifacts_dir,
        summaries,
        metadata={"model": model, "rubric_calibration": True},
    )
    return summaries, summary_path


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
    rubric_model=None,
    artifact_stem=None,
    trial=1,
):
    artifact_stem = case["id"] if artifact_stem is None else artifact_stem
    prompt = build_codex_prompt(case, plugin_root=plugin_root)
    output_path = artifact_dirs["outputs"] / f"{artifact_stem}.txt"
    trace_path = artifact_dirs["traces"] / f"{artifact_stem}.jsonl"
    stderr_path = artifact_dirs["stderr"] / f"{artifact_stem}.stderr"
    prompt_path = artifact_dirs["prompts"] / f"{artifact_stem}.txt"

    summary = {
        "id": case["id"],
        "category": case["category"],
        "target_skill": target_skill_for_case(case),
        "faithful_mode": faithful_mode_for_case(case),
        "plain_language_mode": plain_language_mode_for_case(case),
        "activation_probe": case.get("activation_probe", False),
        "trial": trial,
        "model": model,
        "rubric_model": rubric_model or model,
        "returncode": None,
        "trace_path": str(trace_path),
        "output_path": str(output_path),
        "stderr_path": str(stderr_path),
        "prompt_path": str(prompt_path),
        "passed": False,
        "error": None,
        "failure_stage": "execution",
        "rubric_passed": None,
        "rubric_error": None,
        "rubric_total_score": None,
        "editorial_source_diagnostics": editorial_diagnostics_for_case(
            case,
            case["source"],
        ),
        "editorial_output_diagnostics": None,
        **empty_trace_metrics(),
    }

    prompt_path.write_text(prompt, encoding="utf-8")
    remove_file_if_exists(output_path)
    command = build_codex_command(
        codex_bin,
        artifact_dirs["prompts"].parent.resolve(),
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

        summary["failure_stage"] = "trace"
        events = parse_jsonl_events(result.stdout)
        metrics = collect_trace_metrics(events)
        summary.update(metrics)
        check_trace_expectations(case, events)
        check_stderr_expectations(case, result.stderr)

        summary["failure_stage"] = "output_contract"
        output_text = read_final_output(case, output_path)
        summary["editorial_output_diagnostics"] = editorial_diagnostics_for_case(
            case,
            output_text,
        )
        validate_case_output_contract(case, output_text, output_contract_cases)
        if grade_rubric and case.get("rubric"):
            summary["failure_stage"] = "rubric"
            try:
                summary.update(
                    run_rubric_grade(
                        case,
                        output_text,
                        artifact_dirs,
                        codex_bin=codex_bin,
                        model=rubric_model or model,
                        timeout_seconds=timeout_seconds,
                        environment=environment,
                        artifact_stem=artifact_stem,
                    )
                )
            except (AssertionError, OSError, ValueError, subprocess.TimeoutExpired) as error:
                summary["rubric_error"] = str(error)
                raise
    except (AssertionError, OSError, ValueError, subprocess.TimeoutExpired) as error:
        summary["error"] = str(error)
        return summary

    summary["passed"] = True
    summary["failure_stage"] = None
    return summary


def select_cases(
    cases,
    filters,
    target_skills=None,
    faithful_modes=None,
    plain_language_modes=None,
):
    selected_ids = set(filters)
    if selected_ids:
        selected_cases = [case for case in cases if case["id"] in selected_ids]
        missing_ids = selected_ids - {case["id"] for case in selected_cases}
        if missing_ids:
            raise ValueError(f"unknown eval case id(s): {', '.join(sorted(missing_ids))}")
    else:
        selected_cases = list(cases)

    selected_target_skills = set(target_skills or [])
    if selected_target_skills:
        selected_cases = [
            case
            for case in selected_cases
            if target_skill_for_case(case) in selected_target_skills
        ]
        if not selected_cases:
            raise ValueError("no eval cases match the selected target skill(s)")

    selected_faithful_modes = set(faithful_modes or [])
    if selected_faithful_modes:
        selected_cases = [
            case
            for case in selected_cases
            if faithful_mode_for_case(case) in selected_faithful_modes
        ]
        if not selected_cases:
            raise ValueError("no eval cases match the selected Faithful mode(s)")

    selected_plain_language_modes = set(plain_language_modes or [])
    if selected_plain_language_modes:
        selected_cases = [
            case
            for case in selected_cases
            if plain_language_mode_for_case(case) in selected_plain_language_modes
        ]
        if not selected_cases:
            raise ValueError(
                "no eval cases match the selected Plain Language mode(s)"
            )
    return selected_cases


def summarize_pass_rate(summaries):
    run_count = len(summaries)
    passed_count = sum(1 for summary in summaries if summary.get("passed"))
    return {
        "runs": run_count,
        "passed": passed_count,
        "pass_rate": passed_count / run_count if run_count else 0,
    }


def aggregate_summaries(summaries):
    grouped_summaries = {}
    faithful_mode_summaries = {}
    plain_language_mode_summaries = {}
    failure_stages = {}
    for summary in summaries:
        target_skill = summary.get("target_skill", "unknown")
        grouped_summaries.setdefault(target_skill, []).append(summary)
        faithful_mode = summary.get("faithful_mode")
        if faithful_mode:
            faithful_mode_summaries.setdefault(faithful_mode, []).append(summary)
        plain_language_mode = summary.get("plain_language_mode")
        if plain_language_mode:
            plain_language_mode_summaries.setdefault(
                plain_language_mode,
                [],
            ).append(summary)
        failure_stage = summary.get("failure_stage")
        if failure_stage:
            failure_stages[failure_stage] = failure_stages.get(failure_stage, 0) + 1

    by_target_skill = {}
    for target_skill, skill_summaries in sorted(grouped_summaries.items()):
        dimension_scores = {}
        for summary in skill_summaries:
            for dimension, score in (
                summary.get("rubric_dimension_scores") or {}
            ).items():
                dimension_scores.setdefault(dimension, []).append(score)
        by_target_skill[target_skill] = {
            **summarize_pass_rate(skill_summaries),
            "minimum_rubric_dimension_scores": {
                dimension: min(scores)
                for dimension, scores in sorted(dimension_scores.items())
            },
        }

    by_faithful_mode = {
        faithful_mode: summarize_pass_rate(mode_summaries)
        for faithful_mode, mode_summaries in sorted(faithful_mode_summaries.items())
    }
    by_plain_language_mode = {
        plain_language_mode: summarize_pass_rate(mode_summaries)
        for plain_language_mode, mode_summaries in sorted(
            plain_language_mode_summaries.items()
        )
    }
    return {
        **summarize_pass_rate(summaries),
        "failure_stages": dict(sorted(failure_stages.items())),
        "by_target_skill": by_target_skill,
        "by_faithful_mode": by_faithful_mode,
        "by_plain_language_mode": by_plain_language_mode,
    }


def write_summary(artifacts_dir, summaries, metadata=None):
    summary_path = artifacts_dir / "summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "metadata": metadata or {},
                "aggregate": aggregate_summaries(summaries),
                "results": summaries,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return summary_path


def run_eval_suite(
    cases,
    artifacts_dir,
    codex_bin,
    model=None,
    timeout_seconds=DEFAULT_TIMEOUT_SECONDS,
    grade_rubric=False,
    rubric_model=None,
    trials=1,
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
        summaries = []
        for case in cases:
            for trial in range(1, trials + 1):
                artifact_stem = (
                    case["id"]
                    if trials == 1
                    else f"{case['id']}.trial-{trial:02d}"
                )
                summaries.append(
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
                        rubric_model=rubric_model,
                        artifact_stem=artifact_stem,
                        trial=trial,
                    )
                )
    summary_path = write_summary(
        artifacts_dir,
        summaries,
        metadata={
            "model": model,
            "rubric_model": rubric_model or model,
            "rubric_grade": grade_rubric,
            "trials": trials,
        },
    )
    return summaries, summary_path


def print_dry_run(cases, trials=1):
    print(
        f"would run {len(cases)} Humanizer eval case(s) "
        f"across {trials} trial(s) ({len(cases) * trials} total run(s))"
    )
    for case in cases:
        trigger_label = "trigger" if case["should_trigger"] else "no-trigger"
        mode = faithful_mode_for_case(case) or plain_language_mode_for_case(case)
        mode_label = f", {mode}" if mode else ""
        print(
            f"- {case['id']} "
            f"[{target_skill_for_case(case)}{mode_label}, "
            f"{case['category']}, {trigger_label}]"
        )


def print_summary(summaries, summary_path):
    passed_count = sum(1 for summary in summaries if summary["passed"])
    print(f"passed {passed_count}/{len(summaries)} Humanizer eval case(s)")
    print(f"summary: {summary_path}")

    aggregate = aggregate_summaries(summaries)
    for target_skill, skill_summary in aggregate["by_target_skill"].items():
        print(
            f"- {target_skill}: {skill_summary['passed']}/{skill_summary['runs']} passed"
        )

    for summary in summaries:
        if not summary["passed"]:
            print(f"- {summary['id']}: {summary['error']}", file=sys.stderr)


def build_parser():
    parser = argparse.ArgumentParser(description="Run live Codex evals for Humanizer skills.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES_PATH)
    parser.add_argument("--artifacts-dir", type=Path, default=DEFAULT_ARTIFACTS_DIR)
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--rubric-model")
    parser.add_argument(
        "--timeout-seconds",
        type=positive_integer,
        default=DEFAULT_TIMEOUT_SECONDS,
    )
    parser.add_argument("--filter", action="append", default=[])
    parser.add_argument(
        "--target-skill",
        action="append",
        choices=sorted(TARGET_SKILL_DISPLAY_NAMES),
        default=[],
    )
    parser.add_argument(
        "--faithful-mode",
        action="append",
        choices=VALID_FAITHFUL_MODES,
        default=[],
    )
    parser.add_argument(
        "--plain-language-mode",
        action="append",
        choices=VALID_PLAIN_LANGUAGE_MODES,
        default=[],
    )
    parser.add_argument("--trials", type=positive_integer, default=1)
    parser.add_argument("--rubric-grade", action="store_true")
    parser.add_argument("--calibrate-rubric", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv):
    parser = build_parser()
    args = parser.parse_args(argv[1:])

    if args.calibrate_rubric:
        try:
            calibrations = load_rubric_calibrations(args.cases)
        except (OSError, ValueError) as error:
            print(str(error), file=sys.stderr)
            return 2
        if args.dry_run:
            print(f"would run {len(calibrations)} rubric calibration(s)")
            for calibration in calibrations:
                print(
                    f"- {calibration['id']} "
                    f"[expected_pass={calibration['expected_pass']}]"
                )
            return 0
        try:
            summaries, summary_path = run_rubric_calibration_suite(
                calibrations,
                artifacts_dir=args.artifacts_dir,
                codex_bin=args.codex_bin,
                model=args.rubric_model or args.model,
                timeout_seconds=args.timeout_seconds,
            )
        except (OSError, RuntimeError, ValueError) as error:
            print(str(error), file=sys.stderr)
            return 2
        print_summary(summaries, summary_path)
        return 0 if all(summary["passed"] for summary in summaries) else 1

    try:
        cases = select_cases(
            load_eval_cases(args.cases),
            args.filter,
            target_skills=args.target_skill,
            faithful_modes=args.faithful_mode,
            plain_language_modes=args.plain_language_mode,
        )
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2

    if args.dry_run:
        print_dry_run(cases, trials=args.trials)
        return 0

    try:
        summaries, summary_path = run_eval_suite(
            cases,
            artifacts_dir=args.artifacts_dir,
            codex_bin=args.codex_bin,
            model=args.model,
            timeout_seconds=args.timeout_seconds,
            grade_rubric=args.rubric_grade,
            rubric_model=args.rubric_model,
            trials=args.trials,
        )
    except (OSError, RuntimeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    print_summary(summaries, summary_path)
    return 0 if all(summary["passed"] for summary in summaries) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
