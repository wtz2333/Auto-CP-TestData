# Polyhedron 项目 ZIP 生成实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 让 `build-cp-testdata` 在用户显式启用后，为通过验收的普通批处理题生成可复现的 `polyhedron.zip`。

**架构：** 新建独立 `scripts/package_polyhedron.py` 负责成员渲染、路径安全、确定性 ZIP 和原子替换。`scripts/run_pipeline.py` 仅负责校验开工契约、组装已验收输入、调用打包器并将证据写入报告。

**技术栈：** Python 3 标准库（`zipfile`、`tempfile`、`hashlib`、`json`、`pathlib`）、`unittest`、现有 JSON/YAML 文本契约。

---

## 文件结构

- 创建 `scripts/package_polyhedron.py`：纯打包逻辑与原子 ZIP 写入。
- 创建 `scripts/test_package_polyhedron.py`：打包器单元测试。
- 修改 `scripts/run_pipeline.py:93-212,391-613,1247-1386`：契约校验、打包协调、报告和 `package` 阶段。
- 修改 `scripts/test_pipeline.py`：配置匹配、禁止题型和流水线调用回归测试。
- 修改 `assets/intake-questionnaire.md`：增加显式 Polyhedron ZIP 选项与回复格式。
- 修改 `assets/task.example.json`：增加 `intake.preferences.polyhedron_zip`。
- 修改 `assets/pipeline.example.json`：增加 `polyhedron_package`。
- 创建 `references/polyhedron-package.md`：记录基准 ZIP 包络、映射、限制和验收。
- 修改 `SKILL.md`：把 ZIP 选择、生成顺序和发布门纳入核心流程。
- 修改 `README.md`：简述可选输出与命令。
- 修改 `agents/openai.yaml`：使默认提示包含用户选择的 Polyhedron ZIP。

### 任务 1：锁定开工契约与流水线配置

**文件：**
- 修改：`scripts/test_pipeline.py`
- 修改：`scripts/run_pipeline.py:93-212`
- 修改：`scripts/run_pipeline.py:391-613`

- [ ] **步骤 1：在测试 fixture 中声明新契约**

在 `base_task()` 的 `preferences` 中加入：

```python
"polyhedron_zip": {
    "value": False,
    "source": "user",
},
```

在 `base_config()` 中加入：

```python
"polyhedron_package": {
    "enabled": False,
    "path": "polyhedron.zip",
},
```

- [ ] **步骤 2：编写会失败的契约测试**

```python
def test_polyhedron_package_must_match_user_intake(self) -> None:
    config = self.base_config()
    config["polyhedron_package"]["enabled"] = True
    with self.assertRaisesRegex(PipelineError, "does not match"):
        self.load(config=config)

def test_polyhedron_package_path_is_fixed(self) -> None:
    config = self.base_config()
    config["polyhedron_package"]["path"] = "dist/problem.zip"
    with self.assertRaisesRegex(PipelineError, "must be polyhedron.zip"):
        self.load(config=config)

def test_polyhedron_package_rejects_unsupported_judge_mode(self) -> None:
    config = self.base_config()
    config["polyhedron_package"]["enabled"] = True
    task = self.base_task()
    task["intake"]["preferences"]["polyhedron_zip"]["value"] = True
    task["technical_facts"]["judge_mode"]["value"] = "custom-checker"
    with self.assertRaisesRegex(PipelineError, "standard batch"):
        self.load(config=config, task=task)
```

- [ ] **步骤 3：运行定向测试并确认正确失败**

运行：

```powershell
python -X utf8 scripts/test_pipeline.py
```

预期：新测试不能捕获预期 `PipelineError`，因为当前实现尚未读取 `polyhedron_zip` 和 `polyhedron_package`。

- [ ] **步骤 4：实现最小契约校验**

在 `Pipeline.__init__()` 中初始化：

```python
self.polyhedron_zip_requested = False
self.polyhedron_package_enabled = False
self.polyhedron_package_path = self.root / "polyhedron.zip"
self.polyhedron_package_metadata: dict[str, Any] | None = None
self.judge_mode = ""
```

在 `validate_task_contract()` 的 `required` 中增加 `polyhedron_zip`，校验并保存：

```python
polyhedron_zip = values["polyhedron_zip"]
if preferences["polyhedron_zip"]["source"] != "user":
    raise PipelineError("preference polyhedron_zip must be confirmed by the user")
if not isinstance(polyhedron_zip, bool):
    raise PipelineError("preference polyhedron_zip must be boolean")
self.polyhedron_zip_requested = polyhedron_zip

self.judge_mode = str(technical_values["judge_mode"])
```

在 `validate_config()` 末尾调用下列方法：

```python
def validate_polyhedron_package(self) -> None:
    package = self.config.get("polyhedron_package")
    if not isinstance(package, dict):
        raise PipelineError("polyhedron_package must be an object")
    enabled = package.get("enabled")
    if not isinstance(enabled, bool):
        raise PipelineError("polyhedron_package.enabled must be boolean")
    path_value = package.get("path")
    if path_value != "polyhedron.zip":
        raise PipelineError("polyhedron_package.path must be polyhedron.zip")
    if enabled != self.polyhedron_zip_requested:
        raise PipelineError(
            "polyhedron_package.enabled does not match task polyhedron_zip"
        )
    if enabled and not self.judge_mode.lower().startswith("batch-"):
        raise PipelineError(
            "Polyhedron packaging supports only standard batch judge modes"
        )
    if enabled and self.compare_mode not in {"tokens", "exact"}:
        raise PipelineError(
            "Polyhedron packaging supports only tokens or exact comparison"
        )
    self.polyhedron_package_enabled = enabled
    self.polyhedron_package_path = self.root / "polyhedron.zip"
```

- [ ] **步骤 5：运行测试验证通过**

运行：`python -X utf8 scripts/test_pipeline.py`

预期：全部 `OK`，现有计分与开工契约测试无回归。

- [ ] **步骤 6：Commit**

```powershell
git add scripts/run_pipeline.py scripts/test_pipeline.py
git commit -m "feat: validate Polyhedron package contract"
```

### 任务 2：实现确定性 Polyhedron 打包器

**文件：**
- 创建：`scripts/test_package_polyhedron.py`
- 创建：`scripts/package_polyhedron.py`

- [ ] **步骤 1：编写失败的成员、计分与可复现性测试**

`scripts/test_package_polyhedron.py` 使用真实临时文件，不 mock ZIP 写入：

```python
#!/usr/bin/env python3
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
        (self.root / "data").mkdir()
        (self.root / "statement.md").write_text(
            "# 加法测试\n\n输入两个整数。\n", encoding="utf-8", newline="\n"
        )
        (self.root / "std.cpp").write_text(
            "#include <iostream>\nint main(){long long a,b;std::cin>>a>>b;std::cout<<a+b<<'\\n';}\n",
            encoding="utf-8",
            newline="\n",
        )
        for case_id, input_text, answer_text in (
            ("001", "1 2\n", "3\n"),
            ("002", "-4 9\n", "5\n"),
        ):
            (self.root / "data" / f"{case_id}.in").write_text(
                input_text, encoding="utf-8", newline="\n"
            )
            (self.root / "data" / f"{case_id}.ans").write_text(
                answer_text, encoding="utf-8", newline="\n"
            )
        self.units = [
            {"id": "base", "type": "case", "cases": ["001"], "points": 20, "depends_on": []},
            {"id": "full", "type": "bundle", "cases": ["002"], "points": 80, "depends_on": ["base"]},
        ]

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def build(self) -> dict[str, object]:
        return build_polyhedron_zip(
            root=self.root,
            output_path=self.root / "polyhedron.zip",
            statement_path=self.root / "statement.md",
            standard_solution_path=self.root / "std.cpp",
            data_dir=self.root / "data",
            case_ids=["001", "002"],
            scoring_units=self.units,
            memory_limit_mib=512,
        )

    def test_archive_matches_minimal_polyhedron_envelope(self) -> None:
        metadata = self.build()
        with zipfile.ZipFile(self.root / "polyhedron.zip") as archive:
            self.assertEqual(
                archive.namelist(),
                [
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
                ],
            )
            self.assertEqual(
                archive.read("polyhedron-export/testdata/001.out"), b"3\n"
            )
            config = archive.read("polyhedron-export/testdata/config.yaml").decode()
            self.assertIn("output: 001.out", config)
            self.assertIn("type: min", config)
            self.assertIn("if: [1]", config)
        self.assertEqual(metadata["path"], "polyhedron.zip")

    def test_archive_is_byte_reproducible(self) -> None:
        self.build()
        first = (self.root / "polyhedron.zip").read_bytes()
        first_hash = hashlib.sha256(first).hexdigest()
        self.build()
        second = (self.root / "polyhedron.zip").read_bytes()
        self.assertEqual(second, first)
        self.assertEqual(hashlib.sha256(second).hexdigest(), first_hash)

    def test_missing_answer_is_rejected_without_replacing_old_zip(self) -> None:
        old = b"previous accepted archive"
        (self.root / "polyhedron.zip").write_bytes(old)
        (self.root / "data" / "002.ans").unlink()
        with self.assertRaisesRegex(PackageError, "missing formal data"):
            self.build()
        self.assertEqual((self.root / "polyhedron.zip").read_bytes(), old)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **步骤 2：运行测试并确认导入失败**

运行：`python -X utf8 scripts/test_package_polyhedron.py`

预期：`ModuleNotFoundError: No module named 'package_polyhedron'`。

- [ ] **步骤 3：实现打包器公开接口与确定性写入**

`scripts/package_polyhedron.py` 定义且只导出下列稳定接口：

```python
class PackageError(RuntimeError):
    pass


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
```

实现顺序：

```python
root = root.resolve()
output_path = output_path.resolve()
if output_path != root / "polyhedron.zip":
    raise PackageError("output path must be the package-root polyhedron.zip")

statement = read_lf_utf8(statement_path, "statement")
title = extract_unique_h1(statement)
standard_solution = read_lf_utf8(standard_solution_path, "standard solution")

members: dict[str, bytes] = {
    "polyhedron-export/problem.yaml": render_problem_yaml(title),
    "polyhedron-export/problem_zh.md": statement,
    "polyhedron-export/testdata/_solution_std.cc": standard_solution,
    "polyhedron-export/testdata/config.yaml": render_scoring_config(
        scoring_units, memory_limit_mib
    ),
    "polyhedron-export/testdata/polyhedron.metadata": render_metadata(title),
}
for case_id in case_ids:
    members[f"polyhedron-export/testdata/{case_id}.in"] = read_required_bytes(
        data_dir / f"{case_id}.in", "formal input"
    )
    members[f"polyhedron-export/testdata/{case_id}.out"] = read_required_bytes(
        data_dir / f"{case_id}.ans", "formal answer"
    )

temporary_path = write_and_verify_temporary_zip(root, members)
try:
    os.replace(temporary_path, output_path)
finally:
    temporary_path.unlink(missing_ok=True)

archive_bytes = output_path.read_bytes()
return {
    "path": "polyhedron.zip",
    "sha256": hashlib.sha256(archive_bytes).hexdigest(),
    "members": archive_member_names(members),
}
```

辅助函数必须满足：

- `read_lf_utf8()` 严格解码 UTF-8，将 CRLF 规范为 LF，拒绝剩余 `\r`。
- `extract_unique_h1()` 要求恰有一行 `# <title>`。
- YAML 字符串使用 `json.dumps(value, ensure_ascii=False)` 生成可逆双引号标量。
- `render_scoring_config()` 复用现有计分语义，但输出扩展名为 `.out`。
- ZIP 成员按设计文档的固定顺序写入；时间戳 `(1980, 1, 1, 0, 0, 0)`，文件权限 `0644`，目录权限 `0755`，压缩方式 `ZIP_DEFLATED`，级别 `9`。
- 回读临时 ZIP，精确比对成员顺序、CRC 和字节内容后才 `os.replace()`。

- [ ] **步骤 4：补充失败路径测试**

在 `PolyhedronPackageTests` 中增加以下测试，每个测试使用 `assertRaisesRegex` 确认精确原因：

```python
def test_duplicate_h1_is_rejected(self) -> None:
    (self.root / "statement.md").write_text(
        "# 题目一\n# 题目二\n", encoding="utf-8", newline="\n"
    )
    with self.assertRaisesRegex(PackageError, "exactly one level-1 heading"):
        self.build()

def test_output_path_outside_root_is_rejected(self) -> None:
    with self.assertRaisesRegex(PackageError, "package-root polyhedron.zip"):
        build_polyhedron_zip(
            root=self.root,
            output_path=self.root.parent / "polyhedron.zip",
            statement_path=self.root / "statement.md",
            standard_solution_path=self.root / "std.cpp",
            data_dir=self.root / "data",
            case_ids=["001", "002"],
            scoring_units=self.units,
            memory_limit_mib=512,
        )

def test_duplicate_case_id_is_rejected(self) -> None:
    with self.assertRaisesRegex(PackageError, "duplicate case id"):
        build_polyhedron_zip(
            root=self.root,
            output_path=self.root / "polyhedron.zip",
            statement_path=self.root / "statement.md",
            standard_solution_path=self.root / "std.cpp",
            data_dir=self.root / "data",
            case_ids=["001", "001"],
            scoring_units=self.units,
            memory_limit_mib=512,
        )
```

- [ ] **步骤 5：运行打包器测试与全量回归**

运行：

```powershell
python -X utf8 -m unittest discover -s scripts -p "test_*.py" -v
```

预期：全部 `OK`，两次 ZIP 哈希一致。

- [ ] **步骤 6：Commit**

```powershell
git add scripts/package_polyhedron.py scripts/test_package_polyhedron.py
git commit -m "feat: build deterministic Polyhedron package"
```

### 任务 3：把打包器接入 `all` 和 `package`

**文件：**
- 修改：`scripts/test_pipeline.py`
- 修改：`scripts/run_pipeline.py:93-212`
- 修改：`scripts/run_pipeline.py:1247-1386`

- [ ] **步骤 1：编写失败的协调与报告测试**

在 fixture 中写入真实题面和数据，然后验证 `Pipeline.package_polyhedron()`：

```python
def enable_polyhedron(self, config: dict[str, Any], task: dict[str, Any]) -> None:
    config["polyhedron_package"]["enabled"] = True
    task["intake"]["preferences"]["polyhedron_zip"]["value"] = True

def write_packaging_artifacts(self, pipeline: Any) -> None:
    (self.root / "statement.md").write_text(
        "# 测试题\n", encoding="utf-8", newline="\n"
    )
    pipeline.data_dir.mkdir(parents=True)
    for case_id in pipeline.case_ids:
        (pipeline.data_dir / f"{case_id}.in").write_bytes(b"1 2\n")
        (pipeline.data_dir / f"{case_id}.ans").write_bytes(b"3\n")
    pipeline.write_testdata_config()

def test_package_polyhedron_writes_report_metadata(self) -> None:
    config = self.base_config()
    task = self.base_task()
    self.enable_polyhedron(config, task)
    pipeline = self.load(config, task)
    self.write_packaging_artifacts(pipeline)
    metadata = pipeline.package_polyhedron()
    pipeline.write_report({}, "polyhedron-package")
    self.assertTrue((self.root / "polyhedron.zip").is_file())
    self.assertEqual(metadata["path"], "polyhedron.zip")
    report = (self.root / "report.md").read_text(encoding="utf-8")
    self.assertIn("Polyhedron package: `polyhedron.zip`", report)
    self.assertIn(metadata["sha256"], report)

def test_package_polyhedron_rejects_failed_upstream_gate(self) -> None:
    config = self.base_config()
    task = self.base_task()
    self.enable_polyhedron(config, task)
    pipeline = self.load(config, task)
    pipeline.gate_errors.append("candidate survived")
    with self.assertRaisesRegex(PipelineError, "upstream gate"):
        pipeline.package_polyhedron()
```

- [ ] **步骤 2：运行测试并确认 `package_polyhedron` 缺失**

运行：`python -X utf8 scripts/test_pipeline.py`

预期：`AttributeError: 'Pipeline' object has no attribute 'package_polyhedron'`。

- [ ] **步骤 3：实现协调方法**

```python
def package_polyhedron(self) -> dict[str, Any]:
    if not self.polyhedron_package_enabled:
        raise PipelineError("Polyhedron packaging was not enabled by the intake contract")
    if self.gate_errors:
        raise PipelineError("cannot package while an upstream gate has failed")
    self.write_testdata_config(check_only=True)
    try:
        metadata = build_polyhedron_zip(
            root=self.root,
            output_path=self.polyhedron_package_path,
            statement_path=self.root / "statement.md",
            standard_solution_path=self.source_path(
                str(self.config["sources"]["oracle"])
            ),
            data_dir=self.data_dir,
            case_ids=self.case_ids,
            scoring_units=self.scoring_units,
            memory_limit_mib=self.memory_limit_mib,
        )
    except PackageError as exc:
        raise PipelineError(f"Polyhedron package failed: {exc}") from exc
    self.polyhedron_package_metadata = metadata
    return metadata
```

为保证 `import package_polyhedron` 在直接执行和 `importlib` 测试两种场景下都可用，在 `scripts/test_pipeline.py` 加载 `run_pipeline.py` 前将 `MODULE_PATH.parent` 插入 `sys.path`。

- [ ] **步骤 4：接入命令与报告**

将 argparse 选择改为：

```python
choices=("build", "config", "generate", "evaluate", "package", "all")
```

`package` 和 `all` 都先执行下列验收顺序：

```python
pipeline.build(include_solutions=True)
pipeline.generate()
verdicts = pipeline.evaluate()
```

`package` 分支在验收无错误时无条件调用 `pipeline.package_polyhedron()`，因此未启用时会明确报错。`all` 分支只在 `pipeline.polyhedron_package_enabled` 为真且验收无错误时调用打包器：

```python
if args.stage == "package":
    if not pipeline.gate_errors:
        pipeline.package_polyhedron()
else:
    if not pipeline.gate_errors and pipeline.polyhedron_package_enabled:
        pipeline.package_polyhedron()

completed_gate = (
    "build-generation-evaluation-package"
    if pipeline.polyhedron_package_metadata
    else "build-generation-evaluation"
)
pipeline.write_report(verdicts, completed_gate)
```

`write_report()` 在打包成功时加入：

```python
if self.polyhedron_package_metadata:
    lines.extend(
        [
            "- Polyhedron package: `polyhedron.zip`",
            f"- Polyhedron package SHA-256: `{self.polyhedron_package_metadata['sha256']}`",
        ]
    )
```

- [ ] **步骤 5：运行全量回归测试**

运行：`python -X utf8 -m unittest discover -s scripts -p "test_*.py" -v`

预期：全部 `OK`，报告包含 ZIP 路径与 SHA-256。

- [ ] **步骤 6：Commit**

```powershell
git add scripts/run_pipeline.py scripts/test_pipeline.py
git commit -m "feat: integrate Polyhedron packaging stage"
```

### 任务 4：更新技能契约、示例和渐进参考

**文件：**
- 创建：`references/polyhedron-package.md`
- 修改：`assets/intake-questionnaire.md`
- 修改：`assets/task.example.json`
- 修改：`assets/pipeline.example.json`
- 修改：`SKILL.md`
- 修改：`README.md`
- 修改：`agents/openai.yaml`
- 测试：`scripts/test_pipeline.py`

- [ ] **步骤 1：先让示例同步测试失败**

扩展 `test_shipped_examples_validate_together()`：

```python
self.assertTrue(task["intake"]["preferences"]["polyhedron_zip"]["value"])
self.assertTrue(config["polyhedron_package"]["enabled"])
self.assertEqual(config["polyhedron_package"]["path"], "polyhedron.zip")
```

运行：`python -X utf8 scripts/test_pipeline.py`

预期：因示例尚未声明新字段而 `KeyError: 'polyhedron_zip'`。

- [ ] **步骤 2：更新固定开工确认单和 JSON 示例**

- 将回复示例扩展到第 11 项。
- 新增“11. Polyhedron ZIP”：`A. 不生成`，`B. 验收通过后同时生成 polyhedron.zip`。
- `task.example.json` 选择 `true` 且标记 `source: user`。
- `pipeline.example.json` 增加已启用的固定路径配置。

- [ ] **步骤 3：写入单层 Polyhedron 参考**

`references/polyhedron-package.md` 必须包含：

1. 基准包络 `polyhedron-export/`。
2. `statement.md → problem_zh.md`、`.ans → .out`、`std.cpp → _solution_std.cc` 映射。
3. `problem.yaml`、`polyhedron.metadata` 和 `.out` 版 `config.yaml` 的精确格式。
4. 普通批处理限制、原子写入和可复现规则。
5. `all` 与 `package` 命令。
6. 明确说明不复制基准 ZIP 的账户 `owner` 值和脏数据。

- [ ] **步骤 4：精简更新 `SKILL.md` 和 UI 元数据**

- 在 frontmatter description 的触发场景中加入 Polyhedron 项目 ZIP。
- 在 Required contract 中要求显式解决 `polyhedron_zip`。
- 在数据验收和流水线命令后链接 `references/polyhedron-package.md`，只保留核心时序，不在 `SKILL.md` 重复格式细节。
- 在 Exit criteria 中要求已选择时 ZIP 存在、哈希已记录且包内计分契约一致。
- 修改 `README.md` 的能力与输入列表。
- 修改 `agents/openai.yaml` 的 `short_description` 和 `default_prompt`，默认提示仍保持一句且显式使用 `$build-cp-testdata`。

- [ ] **步骤 5：运行示例与全量回归测试**

运行：`python -X utf8 -m unittest discover -s scripts -p "test_*.py" -v`

预期：全部 `OK`，示例 `task.json` 与 `pipeline.json` 同步启用 ZIP。

- [ ] **步骤 6：Commit**

```powershell
git add SKILL.md README.md agents/openai.yaml assets references/polyhedron-package.md scripts/test_pipeline.py
git commit -m "docs: add Polyhedron package workflow"
```

### 任务 5：完整验证与前向测试

**文件：**
- 检查：本计划所有已创建和已修改文件

- [ ] **步骤 1：运行 Python 语法检查**

```powershell
python -X utf8 -m py_compile scripts/run_pipeline.py scripts/package_polyhedron.py scripts/test_pipeline.py scripts/test_package_polyhedron.py
```

预期：退出码 `0`，无输出。

- [ ] **步骤 2：运行全量回归测试**

```powershell
python -X utf8 -m unittest discover -s scripts -p "test_*.py" -v
```

预期：全部测试 `OK`。

- [ ] **步骤 3：运行技能结构校验**

```powershell
python -X utf8 "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .
```

预期：校验器返回成功，frontmatter、名称和目录结构合法。

- [ ] **步骤 4：审计发布内容**

```powershell
$productionText = Get-ChildItem -Path SKILL.md,README.md,agents,assets,references,scripts -Recurse -File | Where-Object { $_.Extension -in '.md','.json','.yaml','.py','.cpp' }
$productionText | Select-String -Pattern 'TO[D]O:|TB[D]:|owner:\s*31|project-3SUr4VlN0e-rev3'
Get-ChildItem -Path docs -Recurse -File -Filter '*.md' | Select-String -Pattern 'E:[\\]Desktop[\\]题|C:[\\]Users[\\]VictorYuan'
git diff --check
git status --short
```

预期：生产技能文本中无显式占位标记、账户值或已知样例归档名，设计和计划文档中无上述本机路径；`git diff --check` 无输出；只有本功能的预期改动。

- [ ] **步骤 5：使用原技能记录基线失败，再用新技能前向验证**

基线任务使用未修改的技能版本，提示为：

```text
Use $build-cp-testdata to make a verified ordinary batch problem package and also produce a deterministic Polyhedron-importable polyhedron.zip. Do not upload it.
```

记录原技能没有 Polyhedron 契约、打包器或 ZIP 验收的基线失败。新技能使用同类任务时，必须读取新增参考、显式解决开工选项，并调用可执行打包器。

- [ ] **步骤 6：检查最终差异和提交**

```powershell
git diff --stat origin/main...HEAD
git log --oneline --decorate origin/main..HEAD
git status --short
```

预期：差异只包含 Polyhedron 打包功能、测试、契约和相关文档，工作树干净。
