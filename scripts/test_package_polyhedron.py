from __future__ import annotations

import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path

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

    def build(self) -> dict[str, object]:
        return build_polyhedron_zip(
            root=self.root,
            output_path=self.root / "polyhedron.zip",
            statement_path=self.statement_path,
            standard_solution_path=self.standard_solution_path,
            data_dir=self.data_dir,
            case_ids=["001", "002"],
            scoring_units=self.units,
            memory_limit_mib=512,
        )

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
            self.assertEqual(
                archive.read("polyhedron-export/testdata/001.out"), b"3\n"
            )
            config = archive.read(
                "polyhedron-export/testdata/config.yaml"
            ).decode("utf-8")
            self.assertIn("output: 001.out", config)
            self.assertIn("type: min", config)
            self.assertIn("if: [1]", config)
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


if __name__ == "__main__":
    unittest.main()
