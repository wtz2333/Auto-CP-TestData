# Polyhedron 项目 ZIP

本参考定义可选的离线 Polyhedron 项目包。它只支持 ordinary standard batch 题目和 `tokens` / `exact` 输出比较；遇到 interactive、output-only、custom-checker、floating 或其他 custom 判题方式时必须拒绝生成。Skill 只创建离线 ZIP，不上传；用户需要手动上传并在目标平台完成后续检查。

## 最小包络

归档的固定根目录是 `polyhedron-export/`，首版只生成以下最小树：

```text
polyhedron-export/
├── problem.yaml
├── problem_zh.md
└── testdata/
    ├── NNN.in
    ├── NNN.out
    ├── _solution_std.cc
    ├── config.yaml
    └── polyhedron.metadata
```

每个正式测试点各有一对同名的 `NNN.in` / `NNN.out`。映射规则如下：

- `statement.md` 映射为 `problem_zh.md`。
- `data/*.ans` 映射为对应的 `*.out`。
- 流水线声明的 oracle（通常是 `std.cpp`）映射为 `_solution_std.cc`。
- `problem.yaml` 只写下列字段，不复制账户 owner 字段：

  ```yaml
  title: "<题面一级标题>"
  tag: []
  nSubmit: 0
  nAccept: 0
  ```

- `polyhedron.metadata` 使用下列结构，其中 `expectScore` 是冻结 scoring units 的实际总分：

  ```yaml
  title: "<题面一级标题>"
  solutions:
    std.cc:
      language: cc
      expectScore: <实际总分>
      expectStatus: 1
  ```

- `config.yaml` 逐个保留 scoring unit 的顺序、`points` 和 `depends_on`：`case` 映射为 `type: sum`，`bundle` 映射为 `type: min`，依赖映射为生成后的数字 id，并在 `cases` 中引用同名 `.in` / `.out`。每个 unit 使用下列形状；无依赖时必须写 `if: []`：

  ```yaml
  type: default
  subtasks:
  - memory: <memory_limit_mib>MB
    score: <points>
    if: [<生成后的依赖 id>]
    id: <生成后的 unit id>
    type: <case 用 sum；bundle 用 min>
    cases:
    - input: NNN.in
      output: NNN.out
  ```

基准样例项目 ZIP 只用于确认上述包络。不要复制其中的账户字段、generator、validator、错误解或脏数据；首版坚持最小包。

## 构建与发布语义

输出路径固定为题包根目录下的 `polyhedron.zip`。归档必须使用确定性的成员排序、固定时间戳、固定权限和 DEFLATE 压缩。先写临时 ZIP，回读检查成员顺序、CRC 和内容，再以原子替换发布。构建失败时保留旧 ZIP，但报告必须把它标为 stale，明确它不是本次运行的成果。

成功构建时，报告必须记录包路径、SHA-256、成员清单和 `built` 状态。失败、跳过或未启用时，只记录相应状态及旧包未由本次运行更新，不引用旧包的 SHA-256 或成员。生成前仍需通过完整数据验收；包内总分、分组、依赖和成员必须与冻结的 scoring units 一致，不得绕过任何 gate。

## 命令

当 `task.json` 中用户来源的 `polyhedron_zip.value` 为 `true`，且 `pipeline.json` 中 `polyhedron_package.enabled` 为 `true`、路径为 `polyhedron.zip` 时：

```text
python scripts/run_pipeline.py pipeline.json package
python scripts/run_pipeline.py pipeline.json all
```

显式 `package` 会执行完整的 build、generate、evaluate 后再打包；未启用时必须失败。`all` 在启用时自动生成 ZIP，在未启用时正常完成但不得把遗留 ZIP 报告为本次成果。
