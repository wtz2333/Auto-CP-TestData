from __future__ import annotations

import decimal
import hashlib
import json
import tempfile
import unittest
import zipfile
from decimal import Decimal
from pathlib import Path, PurePosixPath
from unittest import mock

from package_polyhedron import PackageError, build_polyhedron_zip


class PolyhedronPackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.data_dir = self.root / "data"
        self.data_dir.mkdir()
        self.statement_path = self.root / "statement.md"
        self.statement_path.write_text(
            "# 加法测试\n\n输入两个整数。\n", encoding="utf-8", newline="\n"
        )
        self.standard_solution_path = self.root / "std.cpp"
        self.standard_solution_path.write_text(
            "#include <iostream>\n"
            "int main(){long long a,b;std::cin>>a>>b;std::cout<<a+b<<'\\n';}\n",
            encoding="utf-8",
            newline="\n",
        )
        for case_id, input_text, answer_text in (
            ("001", "1 2\n", "3\n"),
            ("002", "-4 9\n", "5\n"),
        ):
            (self.data_dir / f"{case_id}.in").write_text(
                input_text, encoding="utf-8", newline="\n"
            )
            (self.data_dir / f"{case_id}.ans").write_text(
                answer_text, encoding="utf-8", newline="\n"
            )
        self.units = [
            {
                "id": "base",
                "type": "case",
                "cases": ["001"],
                "points": 20,
                "depends_on": [],
            },
            {
                "id": "full",
                "type": "bundle",
                "cases": ["002"],
                "points": 80,
                "depends_on": ["base"],
            },
        ]

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def build(self, **overrides: object) -> dict[str, object]:
        arguments = {
            "root": self.root,
            "output_path": self.root / "polyhedron.zip",
            "statement_path": self.statement_path,
            "standard_solution_path": self.standard_solution_path,
            "data_dir": self.data_dir,
            "case_ids": ["001", "002"],
            "scoring_units": self.units,
            "memory_limit_mib": 512,
        }
        arguments.update(overrides)
        return build_polyhedron_zip(**arguments)

    def test_archive_matches_minimal_polyhedron_envelope(self) -> None:
        metadata = self.build()
        expected_members = [
            "polyhedron-export/",
            "polyhedron-export/problem.yaml",
            "polyhedron-export/problem_zh.md",
            "polyhedron-export/testdata/",
            "polyhedron-export/testdata/001.in",
            "polyhedron-export/testdata/001.out",
            "polyhedron-export/testdata/002.in",
            "polyhedron-export/testdata/002.out",
            "polyhedron-export/testdata/_solution_std.cc",
            "polyhedron-export/testdata/config.yaml",
            "polyhedron-export/testdata/polyhedron.metadata",
        ]
        with zipfile.ZipFile(self.root / "polyhedron.zip") as archive:
            self.assertEqual(archive.namelist(), expected_members)
            for member in archive.namelist():
                self.assertFalse(member.startswith("/"))
                self.assertNotIn("\\", member)
                self.assertNotIn("..", PurePosixPath(member).parts)
            self.assertEqual(
                archive.read("polyhedron-export/problem.yaml"),
                (
                    'title: "加法测试"\n'
                    "tag: []\n"
                    "nSubmit: 0\n"
                    "nAccept: 0\n"
                ).encode("utf-8"),
            )
            self.assertEqual(
                archive.read("polyhedron-export/problem_zh.md"),
                b"# \xe5\x8a\xa0\xe6\xb3\x95\xe6\xb5\x8b\xe8\xaf\x95\n\n"
                b"\xe8\xbe\x93\xe5\x85\xa5\xe4\xb8\xa4\xe4\xb8\xaa\xe6\x95\xb4\xe6\x95\xb0\xe3\x80\x82\n",
            )
            self.assertEqual(
                archive.read("polyhedron-export/testdata/001.out"), b"3\n"
            )
            self.assertEqual(
                archive.read("polyhedron-export/testdata/_solution_std.cc"),
                self.standard_solution_path.read_bytes(),
            )
            config = archive.read(
                "polyhedron-export/testdata/config.yaml"
            ).decode("utf-8")
            self.assertEqual(
                config,
                "type: default\n"
                "subtasks:\n"
                "- memory: 512MB\n"
                "  score: 20\n"
                "  if: []\n"
                "  id: 1\n"
                "  type: sum\n"
                "  cases:\n"
                "  - input: 001.in\n"
                "    output: 001.out\n"
                "- memory: 512MB\n"
                "  score: 80\n"
                "  if: [1]\n"
                "  id: 2\n"
                "  type: min\n"
                "  cases:\n"
                "  - input: 002.in\n"
                "    output: 002.out\n",
            )
            self.assertEqual(
                archive.read("polyhedron-export/testdata/polyhedron.metadata"),
                (
                    'title: "加法测试"\n'
                    "solutions:\n"
                    "  std.cc:\n"
                    "    language: cc\n"
                    "    expectScore: 100\n"
                    "    expectStatus: 1\n"
                ).encode("utf-8"),
            )
        self.assertEqual(metadata["path"], "polyhedron.zip")
        self.assertEqual(metadata["members"], expected_members)

    def test_archive_is_byte_reproducible(self) -> None:
        first_metadata = self.build()
        first = (self.root / "polyhedron.zip").read_bytes()
        first_hash = hashlib.sha256(first).hexdigest()

        second_metadata = self.build()
        second = (self.root / "polyhedron.zip").read_bytes()

        self.assertEqual(second, first)
        self.assertEqual(hashlib.sha256(second).hexdigest(), first_hash)
        self.assertEqual(first_metadata["sha256"], first_hash)
        self.assertEqual(second_metadata["sha256"], first_hash)

    def test_unicode_title_uses_reversible_yaml_string_escaping(self) -> None:
        title = '引号 "、反斜线 \\ 与雪人 ☃'
        statement = f"# {title}\n\n正文。\n".encode("utf-8")
        self.statement_path.write_bytes(statement)

        self.build()
        scalar = json.dumps(title, ensure_ascii=False)
        with zipfile.ZipFile(self.root / "polyhedron.zip") as archive:
            self.assertEqual(
                archive.read("polyhedron-export/problem_zh.md"), statement
            )
            problem = archive.read("polyhedron-export/problem.yaml").decode("utf-8")
            metadata = archive.read(
                "polyhedron-export/testdata/polyhedron.metadata"
            ).decode("utf-8")
        self.assertEqual(problem.splitlines()[0], f"title: {scalar}")
        self.assertEqual(metadata.splitlines()[0], f"title: {scalar}")
        self.assertNotIn("owner:", problem)

    def test_statement_and_solution_crlf_are_normalized_to_lf(self) -> None:
        statement = "# 加法测试\r\n\r\n输入两个整数。\r\n".encode("utf-8")
        solution = b"int main() {\r\n  return 0;\r\n}\r\n"
        self.statement_path.write_bytes(statement)
        self.standard_solution_path.write_bytes(solution)

        self.build()
        with zipfile.ZipFile(self.root / "polyhedron.zip") as archive:
            packaged_statement = archive.read("polyhedron-export/problem_zh.md")
            packaged_solution = archive.read(
                "polyhedron-export/testdata/_solution_std.cc"
            )
        self.assertEqual(
            packaged_statement, "# 加法测试\n\n输入两个整数。\n".encode("utf-8")
        )
        self.assertEqual(packaged_solution, b"int main() {\n  return 0;\n}\n")
        self.assertNotIn(b"\r", packaged_statement)
        self.assertNotIn(b"\r", packaged_solution)

    def test_statement_and_solution_reject_bad_utf8_and_bare_cr(self) -> None:
        original_statement = self.statement_path.read_bytes()
        original_solution = self.standard_solution_path.read_bytes()
        invalid_inputs = (
            (self.statement_path, b"\xff", "strict UTF-8"),
            (self.standard_solution_path, b"\xff", "strict UTF-8"),
            (
                self.statement_path,
                "# 加法测试\r正文\n".encode("utf-8"),
                "unsupported CR",
            ),
            (self.standard_solution_path, b"int main()\r{}\n", "unsupported CR"),
        )
        for path, content, message in invalid_inputs:
            with self.subTest(path=path.name, message=message):
                self.statement_path.write_bytes(original_statement)
                self.standard_solution_path.write_bytes(original_solution)
                path.write_bytes(content)
                with self.assertRaisesRegex(PackageError, message):
                    self.build()

    def test_missing_answer_is_rejected_without_replacing_old_zip(self) -> None:
        old = b"previous accepted archive"
        (self.root / "polyhedron.zip").write_bytes(old)
        (self.data_dir / "002.ans").unlink()

        with self.assertRaisesRegex(PackageError, "missing formal data"):
            self.build()

        self.assertEqual((self.root / "polyhedron.zip").read_bytes(), old)
        self.assertEqual(list(self.root.glob(".polyhedron-*.zip.tmp")), [])

    def test_duplicate_h1_is_rejected(self) -> None:
        self.statement_path.write_text(
            "# 题目一\n# 题目二\n", encoding="utf-8", newline="\n"
        )

        with self.assertRaisesRegex(
            PackageError, "exactly one level-1 heading"
        ):
            self.build()

    def test_output_path_must_be_package_root_polyhedron_zip(self) -> None:
        targets = (
            self.root / "other.zip",
            self.root.parent / f"{self.root.name}-polyhedron.zip",
        )
        for output_path in targets:
            self.addCleanup(output_path.unlink, missing_ok=True)
            with self.subTest(output_path=output_path):
                with self.assertRaisesRegex(
                    PackageError, "package-root polyhedron.zip"
                ):
                    build_polyhedron_zip(
                        root=self.root,
                        output_path=output_path,
                        statement_path=self.statement_path,
                        standard_solution_path=self.standard_solution_path,
                        data_dir=self.data_dir,
                        case_ids=["001", "002"],
                        scoring_units=self.units,
                        memory_limit_mib=512,
                    )

    def test_duplicate_case_id_is_rejected(self) -> None:
        with self.assertRaisesRegex(PackageError, "duplicate case id"):
            build_polyhedron_zip(
                root=self.root,
                output_path=self.root / "polyhedron.zip",
                statement_path=self.statement_path,
                standard_solution_path=self.standard_solution_path,
                data_dir=self.data_dir,
                case_ids=["001", "001"],
                scoring_units=self.units,
                memory_limit_mib=512,
            )

    def test_source_paths_must_resolve_within_package_root(self) -> None:
        with tempfile.TemporaryDirectory() as outside_name:
            outside = Path(outside_name)
            outside_statement = outside / "statement.md"
            outside_statement.write_bytes(self.statement_path.read_bytes())
            outside_solution = outside / "std.cpp"
            outside_solution.write_bytes(self.standard_solution_path.read_bytes())
            outside_data = outside / "data"
            outside_data.mkdir()
            for path in self.data_dir.iterdir():
                (outside_data / path.name).write_bytes(path.read_bytes())

            for field, value in (
                ("statement", outside_statement),
                ("standard solution", outside_solution),
                ("data directory", outside_data),
            ):
                with self.subTest(field=field):
                    with self.assertRaisesRegex(
                        PackageError, rf"{field}.*package root"
                    ):
                        overrides = {
                            "statement_path": self.statement_path,
                            "standard_solution_path": self.standard_solution_path,
                            "data_dir": self.data_dir,
                        }
                        key = {
                            "statement": "statement_path",
                            "standard solution": "standard_solution_path",
                            "data directory": "data_dir",
                        }[field]
                        overrides[key] = value
                        self.build(**overrides)

    def test_source_paths_must_exist_with_the_required_type(self) -> None:
        directory = self.root / "not-a-file"
        directory.mkdir()
        regular_file = self.root / "not-a-directory"
        regular_file.write_bytes(b"content")
        invalid_paths = (
            ({"root": regular_file}, "package root must be an existing directory"),
            (
                {"statement_path": directory},
                "statement must be an existing file",
            ),
            (
                {"standard_solution_path": directory},
                "standard solution must be an existing file",
            ),
            (
                {"data_dir": regular_file},
                "data directory must be an existing directory",
            ),
            (
                {"statement_path": self.root / "missing.md"},
                "statement path is unavailable",
            ),
        )
        for overrides, message in invalid_paths:
            with self.subTest(message=message):
                with self.assertRaisesRegex(PackageError, message):
                    self.build(**overrides)

    def test_formal_data_symlink_cannot_escape_package_root(self) -> None:
        old = b"previous accepted archive"
        (self.root / "polyhedron.zip").write_bytes(old)
        with tempfile.TemporaryDirectory() as outside_name:
            outside = Path(outside_name)
            for filename in ("001.in", "001.ans"):
                target = outside / filename
                target.write_bytes(b"external\n")
                link = self.data_dir / filename
                original = link.read_bytes()
                link.unlink()
                try:
                    link.symlink_to(target)
                except OSError as exc:
                    link.write_bytes(original)
                    self.skipTest(f"symlink creation unavailable: {exc}")
                try:
                    with self.subTest(filename=filename):
                        with self.assertRaisesRegex(
                            PackageError, "formal data.*inside package root"
                        ):
                            self.build()
                finally:
                    link.unlink(missing_ok=True)
                    link.write_bytes(original)

        self.assertEqual((self.root / "polyhedron.zip").read_bytes(), old)
        self.assertEqual(list(self.root.glob(".polyhedron-*.zip.tmp")), [])

    def test_formal_data_resolved_path_is_checked_within_root(self) -> None:
        with tempfile.TemporaryDirectory() as outside_name:
            outside_file = Path(outside_name) / "001.in"
            outside_file.write_bytes(b"external\n")
            formal_path = self.data_dir / "001.in"
            path_type = type(formal_path)
            original_resolve = path_type.resolve

            def controlled_resolve(path: Path, strict: bool = False) -> Path:
                if path.name == formal_path.name and path.parent.name == "data":
                    return outside_file
                return original_resolve(path, strict=strict)

            with mock.patch.object(
                path_type, "resolve", new=controlled_resolve
            ):
                with self.assertRaisesRegex(
                    PackageError, "formal data.*inside package root"
                ):
                    self.build()

    def test_case_ids_must_be_safe_single_path_segments(self) -> None:
        old = b"previous accepted archive"
        (self.root / "polyhedron.zip").write_bytes(old)
        invalid_case_ids = ("", ".", "..", "../x", "a/b", "a\\b", "C:\\x")
        for case_id in invalid_case_ids:
            with self.subTest(case_id=case_id):
                units = [
                    {
                        "id": "all",
                        "type": "case",
                        "cases": [case_id],
                        "points": 100,
                        "depends_on": [],
                    }
                ]
                with self.assertRaisesRegex(PackageError, "unsafe case id"):
                    self.build(case_ids=[case_id], scoring_units=units)

        self.assertEqual((self.root / "polyhedron.zip").read_bytes(), old)
        self.assertEqual(list(self.root.glob(".polyhedron-*.zip.tmp")), [])

    def test_scoring_shape_and_memory_limit_are_validated(self) -> None:
        invalid_arguments = (
            ({"scoring_units": []}, "nonempty sequence of mappings"),
            ({"scoring_units": "not-units"}, "nonempty sequence of mappings"),
            ({"scoring_units": [None]}, "scoring unit 1 must be a mapping"),
            ({"memory_limit_mib": 0}, "memory_limit_mib must be a positive integer"),
            ({"memory_limit_mib": -1}, "memory_limit_mib must be a positive integer"),
            ({"memory_limit_mib": 1.5}, "memory_limit_mib must be a positive integer"),
            ({"memory_limit_mib": True}, "memory_limit_mib must be a positive integer"),
        )
        for overrides, message in invalid_arguments:
            with self.subTest(overrides=overrides):
                with self.assertRaisesRegex(PackageError, message):
                    self.build(**overrides)

    def test_scoring_unit_ids_types_and_case_lists_are_validated(self) -> None:
        invalid_units = (
            ([{}], "scoring unit 1 id must be nonempty"),
            (
                [
                    {
                        "id": "same",
                        "type": "case",
                        "cases": ["001"],
                        "points": 20,
                        "depends_on": [],
                    },
                    {
                        "id": "same",
                        "type": "bundle",
                        "cases": ["002"],
                        "points": 80,
                        "depends_on": [],
                    },
                ],
                "duplicate scoring unit id",
            ),
            (
                [
                    {
                        "id": "all",
                        "type": "mixed",
                        "cases": ["001", "002"],
                        "points": 100,
                        "depends_on": [],
                    }
                ],
                "scoring unit all has invalid type",
            ),
            (
                [
                    {
                        "id": "all",
                        "type": "bundle",
                        "cases": [],
                        "points": 100,
                        "depends_on": [],
                    }
                ],
                "scoring unit all cases must be a nonempty list",
            ),
            (
                [
                    {
                        "id": "all",
                        "type": "bundle",
                        "cases": ("001", "002"),
                        "points": 100,
                        "depends_on": [],
                    }
                ],
                "scoring unit all cases must be a nonempty list",
            ),
            (
                [
                    {
                        "id": "all",
                        "type": "bundle",
                        "cases": ["001", "../002"],
                        "points": 100,
                        "depends_on": [],
                    }
                ],
                "unsafe case id",
            ),
        )
        for units, message in invalid_units:
            with self.subTest(message=message):
                with self.assertRaisesRegex(PackageError, message):
                    self.build(scoring_units=units)

    def test_case_scoring_unit_contains_exactly_one_case(self) -> None:
        units = [
            {
                "id": "invalid-case-unit",
                "type": "case",
                "cases": ["001", "002"],
                "points": 100,
                "depends_on": [],
            }
        ]

        with self.assertRaisesRegex(
            PackageError, "type case must contain exactly one case"
        ):
            self.build(scoring_units=units)

    def test_scoring_units_partition_every_formal_case_exactly_once(self) -> None:
        invalid_units = (
            (
                [
                    {
                        "id": "all",
                        "type": "bundle",
                        "cases": ["001", "003"],
                        "points": 100,
                        "depends_on": [],
                    }
                ],
                "unknown formal case id: 003",
            ),
            (
                [
                    {
                        "id": "first",
                        "type": "case",
                        "cases": ["001"],
                        "points": 20,
                        "depends_on": [],
                    },
                    {
                        "id": "all",
                        "type": "bundle",
                        "cases": ["001", "002"],
                        "points": 80,
                        "depends_on": [],
                    },
                ],
                "formal case appears more than once: 001",
            ),
            (
                [
                    {
                        "id": "partial",
                        "type": "case",
                        "cases": ["001"],
                        "points": 100,
                        "depends_on": [],
                    }
                ],
                "formal cases missing from scoring units: 002",
            ),
        )
        for units, message in invalid_units:
            with self.subTest(message=message):
                with self.assertRaisesRegex(PackageError, message):
                    self.build(scoring_units=units)

    def test_scoring_points_are_finite_nonnegative_with_positive_total(self) -> None:
        for points in (None, -1, float("nan"), float("inf"), "100", True):
            with self.subTest(points=points):
                units = [
                    {
                        "id": "all",
                        "type": "bundle",
                        "cases": ["001", "002"],
                        "points": points,
                        "depends_on": [],
                    }
                ]
                with self.assertRaisesRegex(
                    PackageError, "points must be a finite nonnegative number"
                ):
                    self.build(scoring_units=units)

        zero_total = [
            {
                "id": "base",
                "type": "case",
                "cases": ["001"],
                "points": 0,
                "depends_on": [],
            },
            {
                "id": "full",
                "type": "bundle",
                "cases": ["002"],
                "points": 0,
                "depends_on": ["base"],
            },
        ]
        with self.assertRaisesRegex(
            PackageError, "scoring points total must be finite and positive"
        ):
            self.build(scoring_units=zero_total)

    def test_zero_point_unit_is_allowed_when_total_is_positive(self) -> None:
        units = [
            {
                "id": "base",
                "type": "case",
                "cases": ["001"],
                "points": 0,
                "depends_on": [],
            },
            {
                "id": "full",
                "type": "bundle",
                "cases": ["002"],
                "points": 100,
                "depends_on": ["base"],
            },
        ]

        self.build(scoring_units=units)
        with zipfile.ZipFile(self.root / "polyhedron.zip") as archive:
            config = archive.read(
                "polyhedron-export/testdata/config.yaml"
            ).decode("utf-8")
        self.assertIn("  score: 0\n", config)
        self.assertIn("  score: 100\n", config)

    def test_arbitrary_positive_total_is_preserved_in_config_and_metadata(self) -> None:
        units = [
            {
                "id": "base",
                "type": "case",
                "cases": ["001"],
                "points": 10,
                "depends_on": [],
            },
            {
                "id": "full",
                "type": "bundle",
                "cases": ["002"],
                "points": 50,
                "depends_on": ["base"],
            },
        ]

        self.build(scoring_units=units)
        with zipfile.ZipFile(self.root / "polyhedron.zip") as archive:
            config = archive.read(
                "polyhedron-export/testdata/config.yaml"
            ).decode("utf-8")
            metadata = archive.read(
                "polyhedron-export/testdata/polyhedron.metadata"
            ).decode("utf-8")
        self.assertIn("  score: 10\n", config)
        self.assertIn("  score: 50\n", config)
        self.assertIn("    expectScore: 60\n", metadata)
        self.assertNotIn("    expectScore: 100\n", metadata)

    def test_scoring_points_preserve_full_deterministic_precision(self) -> None:
        (self.data_dir / "003.in").write_bytes(b"7 8\n")
        (self.data_dir / "003.ans").write_bytes(b"15\n")
        points = (33.333333333, 33.333333333, 33.333333334)
        units = [
            {
                "id": f"part-{index}",
                "type": "case",
                "cases": [case_id],
                "points": score,
                "depends_on": [],
            }
            for index, (case_id, score) in enumerate(
                zip(("001", "002", "003"), points), start=1
            )
        ]

        self.build(
            case_ids=["001", "002", "003"], scoring_units=units
        )
        with zipfile.ZipFile(self.root / "polyhedron.zip") as archive:
            config = archive.read(
                "polyhedron-export/testdata/config.yaml"
            ).decode("utf-8")
        rendered_scores = [
            line.removeprefix("  score: ")
            for line in config.splitlines()
            if line.startswith("  score: ")
        ]
        self.assertEqual(
            rendered_scores,
            ["33.333333333", "33.333333333", "33.333333334"],
        )
        self.assertEqual(sum(map(Decimal, rendered_scores)), Decimal(100))

    def test_global_decimal_precision_does_not_change_archive(self) -> None:
        (self.data_dir / "003.in").write_bytes(b"7 8\n")
        (self.data_dir / "003.ans").write_bytes(b"15\n")
        points = (33.333333333, 33.333333333, 33.333333334)
        units = [
            {
                "id": f"part-{index}",
                "type": "case",
                "cases": [case_id],
                "points": score,
                "depends_on": [],
            }
            for index, (case_id, score) in enumerate(
                zip(("001", "002", "003"), points), start=1
            )
        ]
        saved_context = decimal.getcontext().copy()
        try:
            self.build(
                case_ids=["001", "002", "003"], scoring_units=units
            )
            default_bytes = (self.root / "polyhedron.zip").read_bytes()
            with zipfile.ZipFile(self.root / "polyhedron.zip") as archive:
                default_metadata = archive.read(
                    "polyhedron-export/testdata/polyhedron.metadata"
                )

            decimal.getcontext().prec = 5
            self.build(
                case_ids=["001", "002", "003"], scoring_units=units
            )
            low_precision_bytes = (self.root / "polyhedron.zip").read_bytes()
            with zipfile.ZipFile(self.root / "polyhedron.zip") as archive:
                low_precision_metadata = archive.read(
                    "polyhedron-export/testdata/polyhedron.metadata"
                )
        finally:
            decimal.setcontext(saved_context)

        self.assertEqual(low_precision_bytes, default_bytes)
        self.assertEqual(low_precision_metadata, default_metadata)
        self.assertIn(b"    expectScore: 100\n", low_precision_metadata)

    def test_scoring_dependencies_are_valid_and_acyclic(self) -> None:
        def units(
            base_dependencies: object = None,
            full_dependencies: object = None,
        ) -> list[dict[str, object]]:
            return [
                {
                    "id": "base",
                    "type": "case",
                    "cases": ["001"],
                    "points": 20,
                    "depends_on": (
                        [] if base_dependencies is None else base_dependencies
                    ),
                },
                {
                    "id": "full",
                    "type": "bundle",
                    "cases": ["002"],
                    "points": 80,
                    "depends_on": (
                        ["base"] if full_dependencies is None else full_dependencies
                    ),
                },
            ]

        invalid_units = (
            (units(full_dependencies=("base",)), "depends_on must be a list"),
            (units(full_dependencies=["missing"]), "unknown scoring dependency"),
            (units(full_dependencies=["full"]), "cannot depend on itself"),
            (
                units(full_dependencies=["base", "base"]),
                "duplicate scoring dependency",
            ),
            (
                units(base_dependencies=["full"], full_dependencies=["base"]),
                "scoring dependency cycle",
            ),
        )
        for scoring_units, message in invalid_units:
            with self.subTest(message=message):
                with self.assertRaisesRegex(PackageError, message):
                    self.build(scoring_units=scoring_units)

    def test_case_id_input_order_does_not_change_archive_bytes(self) -> None:
        units = [
            {
                "id": "all",
                "type": "bundle",
                "cases": ["002", "001"],
                "points": 100,
                "depends_on": [],
            }
        ]
        first_metadata = self.build(
            case_ids=["001", "002"], scoring_units=units
        )
        first = (self.root / "polyhedron.zip").read_bytes()

        second_metadata = self.build(
            case_ids=["002", "001"], scoring_units=units
        )
        second = (self.root / "polyhedron.zip").read_bytes()

        self.assertEqual(second, first)
        self.assertEqual(second_metadata["sha256"], first_metadata["sha256"])
        self.assertEqual(second_metadata["members"], first_metadata["members"])
        with zipfile.ZipFile(self.root / "polyhedron.zip") as archive:
            config = archive.read(
                "polyhedron-export/testdata/config.yaml"
            ).decode("utf-8")
        self.assertLess(config.index("input: 002.in"), config.index("input: 001.in"))

    def test_replace_io_error_is_package_error_and_preserves_old_archive(self) -> None:
        old = b"previous accepted archive"
        (self.root / "polyhedron.zip").write_bytes(old)

        with mock.patch(
            "package_polyhedron.os.replace", side_effect=OSError("access denied")
        ):
            with self.assertRaisesRegex(PackageError, "package I/O failure"):
                self.build()

        self.assertEqual((self.root / "polyhedron.zip").read_bytes(), old)
        self.assertEqual(list(self.root.glob(".polyhedron-*.zip.tmp")), [])


if __name__ == "__main__":
    unittest.main()
