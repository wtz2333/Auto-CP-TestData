# Polyhedron 项目 ZIP 生成设计

## 目标

扩展 `build-cp-testdata` 技能：用户在开工确认单中显式选择后，普通批处理题完成现有的生成、校验、答案、计分和候选程序验收后，在题包根目录同时产出 `polyhedron.zip`。

兼容包络以 `E:\Desktop\题\project-3SUr4VlN0e-rev3.zip` 的 `polyhedron-export/` 目录结构为基准。该样例中残缺的数据对、混入的其他题数据、占位程序、非确定生成器和账户绑定的 `owner` 值不属于要复制的格式契约。

## 已确认的范围

- 仅支持标准输入输出的普通批处理题，输出比较方式为 `tokens` 或 `exact`。
- 不支持交互题、输出题、浮点误差、多答案或自定义 checker；遇到时明确拒绝打包。
- ZIP 只收录最小可导入内容：中文题面、题目元信息、正式输入输出、标准程序和保留计分结构所必需的配置。
- 不收录生成器、校验器、暴力程序、错误程序、部分分程序、题解、日志、构建产物或审查记录。
- 不由 Codex 上传网站；用户手动上传。本次验收仅覆盖本地结构、内容和可复现性。

## 方案选择

新增独立的 `scripts/package_polyhedron.py`，由 `scripts/run_pipeline.py` 调用。

不把 ZIP 生成细节直接堆入现有流水线，也不只用 `SKILL.md` 中的自然语言指令让每次调用临时拼包。独立脚本提供可导入的纯函数接口，由流水线的 `all` 和 `package` 命令共用，便于单元测试。

## 开工契约与配置

### 开工确认单

在固定开工确认单末尾新增一项“Polyhedron ZIP”，选项为：

- 不生成；
- 验收通过后同时生成 `polyhedron.zip`。

选择必须记录到 `task.json` 的 `intake.preferences.polyhedron_zip`，不允许从题包内容静默推断。

### `task.json`

```json
"polyhedron_zip": {
  "value": true,
  "source": "user"
}
```

### `pipeline.json`

```json
"polyhedron_package": {
  "enabled": true,
  "path": "polyhedron.zip"
}
```

`polyhedron_package.enabled` 必须与 `task.json` 的确认结果一致。`path` 在第一版必须精确为题包根目录下的 `polyhedron.zip`，不支持输出到其他目录或自定义文件名。

## ZIP 内部结构

```text
polyhedron.zip
└─ polyhedron-export/
   ├─ problem.yaml
   ├─ problem_zh.md
   └─ testdata/
      ├─ config.yaml
      ├─ 001.in
      ├─ 001.out
      ├─ ...
      ├─ _solution_std.cc
      └─ polyhedron.metadata
```

除目录条目外，ZIP 中不得出现此清单之外的文件。`config.yaml` 是为保留已冻结的独立、捆绑或混合计分结构而增加的包内配置；其他包络和命名遵循基准 ZIP。

## 文件映射

| 已验收题包 | ZIP 内路径 | 处理 |
|---|---|---|
| `statement.md` | `polyhedron-export/problem_zh.md` | 保持 UTF-8，强制 LF |
| `data/NNN.in` | `polyhedron-export/testdata/NNN.in` | 字节保持，已由上游保证 LF |
| `data/NNN.ans` | `polyhedron-export/testdata/NNN.out` | 只改扩展名，字节保持 |
| `std.cpp` | `polyhedron-export/testdata/_solution_std.cc` | 保持源码字节，强制 LF |
| `scoring.units` | `polyhedron-export/testdata/config.yaml` | 重新渲染，`output` 引用 `.out` |
| 最终题名 | `problem.yaml` 和 `polyhedron.metadata` | 从 `statement.md` 唯一的一级标题取值 |

一级标题缺失、重复或为空时拒绝打包，不从目录名或原题名猜测。

## 元信息

### `problem.yaml`

按固定字段与顺序生成：

```yaml
title: "示例题名"
tag: []
nSubmit: 0
nAccept: 0
```

题名使用可逆的 YAML 字符串引号和转义。不生成基准包中的 `owner: 31`：该值属于 Polyhedron 账户，不能由本地题包推断或复制。

### `polyhedron.metadata`

按基准包的标准程序格式生成最小内容：

```yaml
title: "示例题名"
solutions:
  std.cc:
    language: cc
    expectScore: 100
    expectStatus: 1
```

不写入 `generators`、`validators` 或 `gen`。

## 计分配置

包内 `config.yaml` 必须直接由已冻结的 `scoring.units` 生成，不对现有 `data/config.yaml` 做无结构的文本替换。

- `case` 计分单元映射为 `type: sum`。
- `bundle` 计分单元映射为 `type: min`。
- 保留分值和无环依赖。
- 每个正式测试在且仅在一个计分单元中出现。
- `input` 使用 `NNN.in`，`output` 使用 `NNN.out`。
- 计分总和必须与 `total_points` 相等。

## 流水线集成

`run_pipeline.py` 新增 `package` 阶段以及 `Pipeline.package_polyhedron()` 协调方法。

### `all`

1. 执行现有 build、generate 和 evaluate。
2. 若任何验收门失败，不调用打包器。
3. 若 `polyhedron_package.enabled` 为 `true`，生成 ZIP 并将路径、SHA-256 与成员列表写入外部报告。
4. 若未启用，保持现有行为，不创建 ZIP。

### `package`

`python scripts/run_pipeline.py pipeline.json package` 重新执行 build、generate 和 evaluate，全部通过后生成 ZIP。该命令要求开工契约和 `pipeline.json` 都已启用 Polyhedron ZIP，避免将显式命令当作绕过用户选择的通道。

## 失败与原子性

以下任一情况中止打包：

- 开工契约与流水线启用值不一致；
- 非支持的判题或输出比较模式；
- 上游验收门未通过；
- 题名无法唯一确定；
- 题面、标准程序、正式数据对或计分配置缺失、多余或过期；
- 文本不是 UTF-8/LF；
- ZIP 目标、源文件或成员路径越出题包根目录；
- ZIP 成员重名、包含反斜杠或包含绝对路径、`..` 等不安全成分。

打包器首先在 `polyhedron.zip` 同目录创建唯一临时文件，完成写入、回读和成员验证后再原子替换目标。失败时删除本次临时文件，不覆盖旧的已验收 ZIP；报告必须明确旧文件未更新，不得将其当作当前成果。

## 可复现 ZIP

对每个成员固定：

- 按 UTF-8 路径字节序排序；
- 时间戳为 ZIP 支持的固定时间；
- 普通文件权限为 `0644`；
- 路径分隔符为 `/`；
- 压缩方式和级别固定；
- 元信息字段顺序和换行固定；
- 目录条目是否写入也固定。

在同一 Python/zlib 环境中，输入字节、契约和配置不变时，两次产出的 `polyhedron.zip` 必须字节完全相同。

## 测试驱动实现

实现前先在现有测试体系中增加会失败的回归测试，并确认失败原因是缺少打包功能。

### 打包器单元测试

- 精确比对 ZIP 成员清单，确认不包含禁止的开发产物。
- 确认 `.ans` 映射为 `.out` 且内容不变。
- 确认题面、`problem.yaml`、`polyhedron.metadata` 和标准程序的路径与内容。
- 分别验证独立、捆绑和混合计分，包括依赖关系和 `.out` 引用。
- 连续两次打包，比较 ZIP 字节和 SHA-256。
- 验证含 YAML 特殊字符和非 ASCII 字符的中文题名。
- 验证路径穿越、重名成员、缺失数据对、题名异常、非 UTF-8/LF 和非支持判题类型会失败。

### 流水线集成测试

- 未启用时，`all` 不生成 ZIP。
- 启用且所有验收门通过时，`all` 生成 ZIP。
- 启用值不一致时在初始配置验证阶段失败。
- 任一上游验收门失败时不调用打包器。
- `package` 命令会重跑验收并生成 ZIP。
- 现有所有回归测试保持通过。

### 技能验证

- 在修改前用独立测试任务记录基线失败：原技能不会产出 Polyhedron ZIP。修改后用同类任务前向测试新行为。
- 更新 `SKILL.md`、固定开工确认单、`task.example.json`、`pipeline.example.json` 和 `agents/openai.yaml`。
- 新增 Polyhedron 包络与限制的单层参考文档，避免让 `SKILL.md` 继续膨胀。
- 运行 `scripts/test_pipeline.py` 及新增打包器测试。
- 运行技能结构校验器。
- 扫描未完成标记、占位符、绝对路径泄漏和已知样例的账户值。

## 实现边界

- 不修改 Polyhedron 网站，不自动上传。
- 不试图从基准 ZIP 的脏数据推导题目语义。
- 不在第一版支持比赛级 ZIP、多语题面、附件、自定义 checker 或非 C++ 标准程序。
- 不覆盖或删除题包中与打包无关的文件。
- 不在本功能中放宽现有的题面、数据、标准程序或发布验收门。

## 验收标准

- 开工确认单可显式选择是否生成 ZIP，选择已持久化并与流水线配置一致。
- 未选择时现有流程不变；选择后 `all` 成功产出题包根目录下的 `polyhedron.zip`。
- ZIP 包络和元信息命名与基准包一致，内容只包含已批准的最小交付集。
- 正式数据对数量与 `pipeline.json` 完全一致，每个 `.in` 恰有一个 `.out`。
- 包内计分单元、分值、依赖和成员与已冻结契约一致，输出引用为 `.out`。
- ZIP 成员路径安全，所有文本为 UTF-8/LF，相同输入可复现为字节相同的 ZIP。
- 上游验收未通过时不生成新 ZIP，也不将旧 ZIP 报告为当前成果。
- 新增测试、原回归测试与技能结构校验全部通过。
