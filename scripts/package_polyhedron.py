from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import tempfile
import zipfile
import zlib
from pathlib import Path
from typing import Any, Mapping, Sequence

__all__ = ["PackageError", "build_polyhedron_zip"]


class PackageError(RuntimeError):
    pass


_ARCHIVE_ROOT = "polyhedron-export/"
_TESTDATA_ROOT = f"{_ARCHIVE_ROOT}testdata/"
_ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


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


def _render_metadata(title: str) -> bytes:
    scalar = json.dumps(title, ensure_ascii=False)
    return (
        f"title: {scalar}\n"
        "solutions:\n"
        "  std.cc:\n"
        "    language: cc\n"
        "    expectScore: 100\n"
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
        score = f"{points:g}" if isinstance(points, (int, float)) else str(points)
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
    root = root.resolve()
    output_path = output_path.resolve()
    if output_path != root / "polyhedron.zip":
        raise PackageError("output path must be the package-root polyhedron.zip")
    if len(set(case_ids)) != len(case_ids):
        raise PackageError("duplicate case id")
    statement = _read_lf_utf8(statement_path, "statement")
    title = _extract_title(statement)
    standard_solution = _read_lf_utf8(
        standard_solution_path, "standard solution"
    )

    case_members: list[tuple[str, bytes, bool]] = []
    for case_id in case_ids:
        input_bytes = _read_required_bytes(
            data_dir / f"{case_id}.in", "formal data"
        )
        output_bytes = _read_required_bytes(
            data_dir / f"{case_id}.ans", "formal data"
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
        (f"{_TESTDATA_ROOT}polyhedron.metadata", _render_metadata(title), False),
    ]

    temporary_path = _write_and_verify_temporary_zip(root, members)
    try:
        os.replace(temporary_path, output_path)
    finally:
        temporary_path.unlink(missing_ok=True)

    archive_bytes = output_path.read_bytes()
    return {
        "path": "polyhedron.zip",
        "sha256": hashlib.sha256(archive_bytes).hexdigest(),
        "members": [name for name, _, _ in members],
    }
