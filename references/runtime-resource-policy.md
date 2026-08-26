# Runtime resource policy

Apply this policy whenever the pipeline runs a generator, validator, checker, oracle, brute force, accepted solution, partial solution, wrong solution, independent solution, or benchmark executable.

## Stack limit

Set `stack_limit_mib` equal to `memory_limit_mib`. Treat the stack as part of the same memory budget and reject a pipeline configuration when the two values differ. Never inherit the operating system's small default stack silently.

Provision the limit consistently:

- On Windows, compile every pipeline-run C++ executable with a PE stack reserve equal to `stack_limit_mib`, using the supported compiler's linker option such as MinGW/Clang `-Wl,--stack,<bytes>` or MSVC `/STACK:<bytes>`. A parent process cannot reliably enlarge an already linked PE executable's stack, so reject an unsupported prebuilt executable or recompile its source under the pipeline instead of pretending the limit was applied.
- On POSIX, set `RLIMIT_STACK` in the child immediately before execution. If the requested value exceeds the process hard limit, fail before running and report the environment limitation; do not continue under a smaller unrecorded stack.

Record `stack_limit_mib`, the operating-system mechanism, and any linker option in the environment or manifest evidence. Apply the same value to generation, validation, answer production, differential tests, the candidate matrix, independent acceptance, and timing runs so verdicts are comparable.

## Recursion and correctness boundary

Recursion is a normal implementation choice. Do not reject recursive code or mechanically convert it to an iterative traversal merely because the input admits a long chain. Estimate the legal worst-case depth and live bytes per frame, include that amount in the program's memory budget, and exercise maximum-depth profiles under the configured release stack. A recursive implementation is acceptable when the estimate fits the memory limit with appropriate runtime margin and the run succeeds under that same stack setting.

If a program still overflows the configured release stack or its proved live stack can exceed the memory limit, record `RE` and fix the program or its supported-domain claim; converting that implementation to an iterative traversal is one possible fix, not a default requirement. Do not rerun one program with an ad hoc larger stack, and do not use a larger stack to hide memory usage beyond the frozen limit.

## Candidate source resource preflight

Before compiling or running any accepted, partial, wrong, adaptive, or reviewer-supplied candidate, write a peak-resource budget. Include every simultaneously live component:

- global and stack arrays;
- `vector` size and capacity, nested-vector object overhead, per-row allocations, and allocator overhead;
- duplicated input, DP, graph, sorting, queue, heap, hash-table, and reconstruction buffers;
- recursion depth and bytes per frame;
- threads, child processes, open files, temporary files, and mapped files;
- maximum stdout/stderr volume and any in-memory capture performed by the harness.

Compute products such as `rows * columns * sizeof(T)` with checked wide arithmetic before allocation. Account for capacity rather than logical size when repeated growth can over-allocate. Do not assume that `vector` is automatically safe or that a memory-limit value is entirely available to payload data; reserve margin for the runtime, allocator, executable, streams, and harness.

When the candidate's intended defect is semantic or time complexity, keep memory comfortably below the frozen limit and the host-safe cap. Prefer flat bounded arrays, coordinate compression, rolling buffers, or sparse storage over a full dense `vector<vector<T>>` when storage is incidental to the attacked algorithm. This rewrite may preserve the candidate's algorithm and intended flaw, but must not repair that flaw.

For a genuine memory-complexity candidate, first prove the peak-memory formula. Execute a limit-crossing instance only when the runner enforces a hard per-process memory cap and the requested allocation remains safe for the host. If enforcement is unavailable or unreliable, do not attempt a giant allocation merely to provoke `bad_alloc`, page-file exhaustion, an operating-system dialog, or process creation failure. Use bounded scale-ladder measurements plus the formula, and mark the live MLE verdict unsupported in that environment rather than manufacturing a system error.

## System-error exclusion

Treat these as infrastructure or candidate-construction failures, not data-strength evidence:

- allocation or commit failure that destabilizes the host, invokes the OS out-of-memory handler, or prevents later processes from starting;
- excessive automatic arrays, uncontrolled recursion, stack overflow unrelated to the intended defect, or an oversized executable image;
- out-of-bounds access, use-after-free, invalid iterator use, signed size overflow, divide by zero, invalid shift, or other undefined behavior unless that exact implementation defect is the isolated target;
- unbounded thread/process creation, detached workers surviving the timeout, fork bombs, or child-process leaks;
- output or log floods, pipe deadlock, unbounded stderr, temporary-file explosion, disk exhaustion, or excessive open handles;
- missing `freopen` files, wrong working directory, interactive waits, GUI/system dialogs, shell-wrapper failure, antivirus quarantine, or process-launch failure;
- timeout cleanup failure that leaves the process tree, files, handles, or reserved resources alive.

Run a staged preflight: compile with warnings; perform sample and tiny oracle-checked smoke tests; test a bounded scale ladder while observing exit status, peak working set, output size, child processes, and cleanup; only then run formal maximum cases. Set output caps, wall-clock timeouts, process-tree termination, and temporary-directory quotas before launch. If any system-level failure occurs, preserve the log, discard the verdict, repair or replace the candidate, restore the environment, and rerun every affected measurement.
