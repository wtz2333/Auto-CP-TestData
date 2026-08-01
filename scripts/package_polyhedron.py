from __future__ import annotations

import hashlib
import json
import math
import os
import re
import stat
import tempfile
import zipfile
import zlib
from collections.abc import Mapping as MappingABC
from collections.abc import Sequence as SequenceABC
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping, Sequence

__all__ = ["PackageError", "build_polyhedron_zip"]


class PackageError(RuntimeError):
    pass


_ARCHIVE_ROOT = "polyhedron-export/"
_TESTDATA_ROOT = f"{_ARCHIVE_ROOT}testdata/"
_ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def _resolve_existing_path(
    path: Path, *, root: Path | None, label: str, directory: bool
) -> Path:
    try:
        resolved = Path(path).resolve(strict=True)
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        raise PackageError(f"{label} path is unavailable: {path}") from exc
    if root is not None:
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise PackageError(f"{label} path must be inside package root") from exc
    correct_type = resolved.is_dir() if directory else resolved.is_file()
    expected = "directory" if directory else "file"
    if not correct_type:
        raise PackageError(f"{label} must be an existing {expected}")
    return resolved


def _resolve_output_path(path: Path) -> Path:
    try:
        return Path(path).resolve(strict=False)
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        raise PackageError(f"output path is invalid: {path}") from exc


def _is_safe_case_id(value: object) -> bool:
    if not isinstance(value, str) or not value or value in {".", ".."}:
        return False
    if "/" in value or "\\" in value or "\x00" in value:
        return False
    try:
        path = Path(value)
    except (OSError, TypeError, ValueError):
        return False
    return not path.is_absolute() and not path.drive and path.name == value


def _validate_case_ids(case_ids: Sequence[str]) -> tuple[str, ...]:
    if isinstance(case_ids, (str, bytes)):
        raise PackageError("formal case_ids must be a nonempty sequence")
    try:
        normalized = tuple(case_ids)
    except TypeError as exc:
        raise PackageError("formal case_ids must be a nonempty sequence") from exc
    if not normalized:
        raise PackageError("formal case_ids must be a nonempty sequence")
    for case_id in normalized:
        if not _is_safe_case_id(case_id):
            raise PackageError(f"unsafe case id: {case_id!r}")
    if len(set(normalized)) != len(normalized):
        raise PackageError("duplicate case id")
    return normalized


def _validate_scoring_units(
    scoring_units: Sequence[Mapping[str, Any]],
    memory_limit_mib: int,
    formal_case_ids: Sequence[str],
) -> tuple[tuple[dict[str, Any], ...], Decimal]:
    if (
        not isinstance(memory_limit_mib, int)
        or isinstance(memory_limit_mib, bool)
        or memory_limit_mib <= 0
    ):
        raise PackageError("memory_limit_mib must be a positive integer")
    if isinstance(scoring_units, (str, bytes)) or not isinstance(
        scoring_units, SequenceABC
    ):
        raise PackageError("scoring_units must be a nonempty sequence of mappings")
    try:
        normalized = tuple(scoring_units)
    except (TypeError, ValueError) as exc:
        raise PackageError(
            "scoring_units must be a nonempty sequence of mappings"
        ) from exc
    if not normalized:
        raise PackageError("scoring_units must be a nonempty sequence of mappings")
    for index, unit in enumerate(normalized, start=1):
        if not isinstance(unit, MappingABC):
            raise PackageError(f"scoring unit {index} must be a mapping")

    seen_ids: set[str] = set()
    formal_cases = set(formal_case_ids)
    assigned_cases: set[str] = set()
    point_total = Decimal(0)
    validated: list[dict[str, Any]] = []
    for index, unit in enumerate(normalized, start=1):
        unit_id = unit.get("id")
        if not isinstance(unit_id, str) or not unit_id.strip():
            raise PackageError(f"scoring unit {index} id must be nonempty")
        if unit_id in seen_ids:
            raise PackageError(f"duplicate scoring unit id: {unit_id}")
        seen_ids.add(unit_id)
        unit_type = unit.get("type")
        if not isinstance(unit_type, str) or unit_type not in {"case", "bundle"}:
            raise PackageError(f"scoring unit {unit_id} has invalid type")
        cases = unit.get("cases")
        if not isinstance(cases, list) or not cases:
            raise PackageError(
                f"scoring unit {unit_id} cases must be a nonempty list"
            )
        if unit_type == "case" and len(cases) != 1:
            raise PackageError(
                f"scoring unit {unit_id} type case must contain exactly one case"
            )
        for case_id in cases:
            if not _is_safe_case_id(case_id):
                raise PackageError(
                    f"unsafe case id in scoring unit {unit_id}: {case_id!r}"
                )
            if case_id not in formal_cases:
                raise PackageError(f"unknown formal case id: {case_id}")
            if case_id in assigned_cases:
                raise PackageError(f"formal case appears more than once: {case_id}")
            assigned_cases.add(case_id)
        points = unit.get("points")
        if (
            not isinstance(points, (int, float))
            or isinstance(points, bool)
            or points < 0
            or (isinstance(points, float) and not math.isfinite(points))
        ):
            raise PackageError(
                f"scoring unit {unit_id} points must be a finite nonnegative number"
            )
        point_total += (
            Decimal(points) if isinstance(points, int) else Decimal(repr(points))
        )
        dependencies = unit.get("depends_on")
        if not isinstance(dependencies, list) or not all(
            isinstance(dependency, str) and dependency
            for dependency in dependencies
        ):
            raise PackageError(
                f"scoring unit {unit_id} depends_on must be a list of nonempty ids"
            )
        if unit_id in dependencies:
            raise PackageError(f"scoring unit {unit_id} cannot depend on itself")
        if len(set(dependencies)) != len(dependencies):
            raise PackageError(
                f"duplicate scoring dependency in unit {unit_id}"
            )
        validated.append(
            {
                "id": unit_id,
                "type": unit_type,
                "cases": list(cases),
                "points": points,
                "depends_on": list(dependencies),
            }
        )
    missing_cases = [
        case_id for case_id in formal_case_ids if case_id not in assigned_cases
    ]
    if missing_cases:
        raise PackageError(
            "formal cases missing from scoring units: " + ", ".join(missing_cases)
        )
    if not point_total.is_finite() or point_total <= 0:
        raise PackageError("scoring points total must be finite and positive")

    graph = {unit["id"]: unit["depends_on"] for unit in validated}
    for unit_id, dependencies in graph.items():
        for dependency in dependencies:
            if dependency not in graph:
                raise PackageError(
                    f"unknown scoring dependency {dependency} in unit {unit_id}"
                )

    resolved: set[str] = set()
    while len(resolved) != len(graph):
        ready = [
            unit_id
            for unit_id, dependencies in graph.items()
            if unit_id not in resolved and set(dependencies) <= resolved
        ]
        if not ready:
            raise PackageError("scoring dependency cycle")
        resolved.update(ready)
    return tuple(validated), point_total


def _read_lf_utf8(path: Path, label: str) -> bytes:
    raw = _read_required_bytes(path, label)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PackageError(f"{label} must be strict UTF-8") from exc
    text = text.replace("\r\n", "\n")
    if "\r" in text:
        raise PackageError(f"{label} contains unsupported CR line endings")
    return text.encode("utf-8")


def _read_required_bytes(path: Path, label: str) -> bytes:
    if not path.is_file():
        raise PackageError(f"missing {label}: {path.name}")
    return path.read_bytes()


def _resolve_formal_data_path(path: Path, root: Path) -> Path:
    try:
        resolved = path.resolve(strict=True)
    except FileNotFoundError as exc:
        raise PackageError(f"missing formal data: {path.name}") from exc
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        raise PackageError(f"formal data path is unavailable: {path.name}") from exc
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise PackageError(
            f"formal data {path.name} path must be inside package root"
        ) from exc
    if not resolved.is_file():
        raise PackageError(f"formal data {path.name} must be an existing file")
    return resolved


def _extract_title(statement: bytes) -> str:
    headings = []
    for line in statement.decode("utf-8").splitlines():
        match = re.fullmatch(r"# (.+)", line)
        if match is not None and match.group(1).strip():
            headings.append(match.group(1).strip())
    if len(headings) != 1:
        raise PackageError("statement must contain exactly one level-1 heading")
    return headings[0]


def _render_problem_yaml(title: str) -> bytes:
    scalar = json.dumps(title, ensure_ascii=False)
    return (
        f"title: {scalar}\n"
        "tag: []\n"
        "nSubmit: 0\n"
        "nAccept: 0\n"
    ).encode("utf-8")


def _render_metadata(title: str, total_score: Decimal) -> bytes:
    scalar = json.dumps(title, ensure_ascii=False)
    rendered_total = format(total_score.normalize(), "f")
    return (
        f"title: {scalar}\n"
        "solutions:\n"
        "  std.cc:\n"
        "    language: cc\n"
        f"    expectScore: {rendered_total}\n"
        "    expectStatus: 1\n"
    ).encode("utf-8")


def _render_scoring_config(
    scoring_units: Sequence[Mapping[str, Any]], memory_limit_mib: int
) -> bytes:
    lines = ["type: default", "subtasks:"]
    generated_ids = {
        str(unit["id"]): index
        for index, unit in enumerate(scoring_units, start=1)
    }
    for index, unit in enumerate(scoring_units, start=1):
        dependencies = ", ".join(
            str(generated_ids[str(dependency)])
            for dependency in unit["depends_on"]
        )
        unit_type = "min" if unit["type"] == "bundle" else "sum"
        points = unit["points"]
        score = str(points) if isinstance(points, int) else repr(points)
        lines.extend(
            [
                f"- memory: {memory_limit_mib}MB",
                f"  score: {score}",
                f"  if: [{dependencies}]",
                f"  id: {index}",
                f"  type: {unit_type}",
                "  cases:",
            ]
        )
        for case_id in unit["cases"]:
            lines.extend(
                [
                    f"  - input: {case_id}.in",
                    f"    output: {case_id}.out",
                ]
            )
    lines.append("")
    return "\n".join(lines).encode("utf-8")


def _zip_info(name: str, *, directory: bool) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=_ZIP_TIMESTAMP)
    info.create_system = 3
    if directory:
        info.external_attr = ((stat.S_IFDIR | 0o755) << 16) | 0x10
    else:
        info.external_attr = (stat.S_IFREG | 0o644) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    return info


def _write_and_verify_temporary_zip(
    root: Path, members: Sequence[tuple[str, bytes, bool]]
) -> Path:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=".polyhedron-", suffix=".zip.tmp", dir=root
    )
    os.close(descriptor)
    temporary_path = Path(temporary_name)
    verified = False
    try:
        with zipfile.ZipFile(
            temporary_path,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as archive:
            for name, content, directory in members:
                archive.writestr(
                    _zip_info(name, directory=directory),
                    content,
                    compress_type=zipfile.ZIP_DEFLATED,
                    compresslevel=9,
                )

        expected_names = [name for name, _, _ in members]
        with zipfile.ZipFile(temporary_path, mode="r") as archive:
            if archive.namelist() != expected_names:
                raise PackageError("temporary ZIP member list verification failed")
            if archive.testzip() is not None:
                raise PackageError("temporary ZIP CRC verification failed")
            for name, expected, _ in members:
                info = archive.getinfo(name)
                actual = archive.read(name)
                if actual != expected:
                    raise PackageError(f"temporary ZIP content mismatch: {name}")
                if info.CRC != (zlib.crc32(expected) & 0xFFFFFFFF):
                    raise PackageError(f"temporary ZIP CRC mismatch: {name}")
        verified = True
        return temporary_path
    finally:
        if not verified:
            temporary_path.unlink(missing_ok=True)


def _build_polyhedron_zip(
    *,
    root: Path,
    output_path: Path,
    statement_path: Path,
    standard_solution_path: Path,
    data_dir: Path,
    case_ids: Sequence[str],
    scoring_units: Sequence[Mapping[str, Any]],
    memory_limit_mib: int,
) -> dict[str, Any]:
    """Validate accepted artifacts and atomically write a deterministic ZIP."""
    root = _resolve_existing_path(
        root, root=None, label="package root", directory=True
    )
    output_path = _resolve_output_path(output_path)
    if output_path != root / "polyhedron.zip":
        raise PackageError("output path must be the package-root polyhedron.zip")
    statement_path = _resolve_existing_path(
        statement_path, root=root, label="statement", directory=False
    )
    standard_solution_path = _resolve_existing_path(
        standard_solution_path,
        root=root,
        label="standard solution",
        directory=False,
    )
    data_dir = _resolve_existing_path(
        data_dir, root=root, label="data directory", directory=True
    )
    case_ids = _validate_case_ids(case_ids)
    scoring_units, total_score = _validate_scoring_units(
        scoring_units, memory_limit_mib, case_ids
    )
    statement = _read_lf_utf8(statement_path, "statement")
    title = _extract_title(statement)
    standard_solution = _read_lf_utf8(
        standard_solution_path, "standard solution"
    )

    case_members: list[tuple[str, bytes, bool]] = []
    for case_id in sorted(case_ids, key=lambda value: value.encode("utf-8")):
        input_path = _resolve_formal_data_path(
            data_dir / f"{case_id}.in", root
        )
        output_path_for_case = _resolve_formal_data_path(
            data_dir / f"{case_id}.ans", root
        )
        input_bytes = _read_required_bytes(
            input_path, "formal data"
        )
        output_bytes = _read_required_bytes(
            output_path_for_case, "formal data"
        )
        case_members.extend(
            [
                (f"{_TESTDATA_ROOT}{case_id}.in", input_bytes, False),
                (f"{_TESTDATA_ROOT}{case_id}.out", output_bytes, False),
            ]
        )

    members = [
        (_ARCHIVE_ROOT, b"", True),
        (f"{_ARCHIVE_ROOT}problem.yaml", _render_problem_yaml(title), False),
        (f"{_ARCHIVE_ROOT}problem_zh.md", statement, False),
        (_TESTDATA_ROOT, b"", True),
        *case_members,
        (f"{_TESTDATA_ROOT}_solution_std.cc", standard_solution, False),
        (
            f"{_TESTDATA_ROOT}config.yaml",
            _render_scoring_config(scoring_units, memory_limit_mib),
            False,
        ),
        (
            f"{_TESTDATA_ROOT}polyhedron.metadata",
            _render_metadata(title, total_score),
            False,
        ),
    ]

    temporary_path = _write_and_verify_temporary_zip(root, members)
    try:
        archive_bytes = temporary_path.read_bytes()
        os.replace(temporary_path, output_path)
    finally:
        temporary_path.unlink(missing_ok=True)

    return {
        "path": "polyhedron.zip",
        "sha256": hashlib.sha256(archive_bytes).hexdigest(),
        "members": [name for name, _, _ in members],
    }


def build_polyhedron_zip(
    *,
    root: Path,
    output_path: Path,
    statement_path: Path,
    standard_solution_path: Path,
    data_dir: Path,
    case_ids: Sequence[str],
    scoring_units: Sequence[Mapping[str, Any]],
    memory_limit_mib: int,
) -> dict[str, Any]:
    """Validate accepted artifacts and atomically write a deterministic ZIP."""
    try:
        return _build_polyhedron_zip(
            root=root,
            output_path=output_path,
            statement_path=statement_path,
            standard_solution_path=standard_solution_path,
            data_dir=data_dir,
            case_ids=case_ids,
            scoring_units=scoring_units,
            memory_limit_mib=memory_limit_mib,
        )
    except PackageError:
        raise
    except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
        raise PackageError(f"Polyhedron package I/O failure: {exc}") from exc
