# Runtime resource policy

Apply this policy whenever the pipeline runs a generator, validator, checker, oracle, brute force, accepted solution, partial solution, wrong solution, independent solution, or benchmark executable.

## Default stack limit

Set `stack_limit_mib` to `memory_limit_mib` by default. Treat the stack as part of the same memory budget: require a positive value no greater than `memory_limit_mib`. Use a smaller explicit value only when the frozen platform contract defines one; never inherit the operating system's small default stack silently.

Provision the limit consistently:

- On Windows, compile every pipeline-run C++ executable with a PE stack reserve equal to `stack_limit_mib`, using the supported compiler's linker option such as MinGW/Clang `-Wl,--stack,<bytes>` or MSVC `/STACK:<bytes>`. A parent process cannot reliably enlarge an already linked PE executable's stack, so reject an unsupported prebuilt executable or recompile its source under the pipeline instead of pretending the limit was applied.
- On POSIX, set `RLIMIT_STACK` in the child immediately before execution. If the requested value exceeds the process hard limit, fail before running and report the environment limitation; do not continue under a smaller unrecorded stack.

Record `stack_limit_mib`, the operating-system mechanism, and any linker option in the environment or manifest evidence. Apply the same value to generation, validation, answer production, differential tests, the candidate matrix, independent acceptance, and timing runs so verdicts are comparable.

## Correctness boundary

A large runtime stack prevents the host's small default from causing false `RE` results, but it does not waive stack-safety review. Newly written full and genuine partial solutions must still avoid recursion whose legal worst-case depth is unsafe or whose stack use can exceed the problem memory limit. Prefer an iterative traversal when the input admits a long chain.

If a program still overflows the configured release stack, record `RE` and fix the program or its supported-domain claim. Do not rerun one program with an ad hoc larger stack, and do not use a larger stack to hide memory usage beyond the frozen limit.
