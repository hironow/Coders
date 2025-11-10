# Agent Chat

This file coordinates work between multiple AI agents to prevent conflicts.

## How to Use

1. **Before starting work**: Read the entire file to check if anyone is working on files you need
2. **Claim your work**: Add a section with a short, task-themed username as an XML tag
3. **List files**: Inside your tag, clearly list the files you expect to modify
4. **Update progress**: Keep running notes about your work inside your tag
5. **When done**: Remove ONLY your XML block - leave other agents' entries intact

## Guidelines

- Pick a short, descriptive username that reflects your task (e.g., `draggable-window`, `auth-fix`, `perf-optimization`)
- Use XML tags to wrap your section: `<your-username>...</your-username>`
- If another agent already claimed a file you need, wait until they remove their tag
- Keep notes concise and focused on what you're doing

## Example

```xml
<api-refactor>
## Task: Refactor API error handling

### Files being modified
- lib/api/client.ts
- lib/api/errors.ts
- tests/unit/api-client.test.ts

### Progress
- [x] Write failing tests
- [ ] Implement error wrapper
- [ ] Update all API calls
</api-refactor>
```

---

## Active Work

<!-- Agents: Add your work sections below this line -->

<pygmt-nanobind-impl>
## Task: Implement PyGMT with nanobind

### Files being modified
- pygmt_nanobind_benchmark/ (entire directory structure)
- justfile (add build, test, verify recipes)
- mise.toml (may add C++ tooling if needed)

### Progress
- [x] Read README.md and AGENTS.md
- [x] Create task plan
- [ ] Initialize git submodules
- [ ] Research PyGMT and GMT architecture
- [ ] Set up development environment
- [ ] Design nanobind interface
- [ ] Implement core bindings
- [ ] Create tests and benchmarks
</pygmt-nanobind-impl>
