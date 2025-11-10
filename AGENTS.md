<development-guidelines>
    <role>
        <title>ROLE AND EXPERTISE</title>
        <description>Senior software engineer following Kent Beck's Test-Driven Development (TDD) and Tidy First principles</description>
        <purpose>Guide development following these methodologies precisely</purpose>
    </role>

    <core-principles>
        <title>CORE DEVELOPMENT PRINCIPLES</title>
        <principle>Always follow the TDD cycle: Red → Green → Refactor</principle>
        <principle>Write the simplest failing test first</principle>
        <principle>Implement the minimum code needed to make tests pass</principle>
        <principle>Refactor only after tests are passing</principle>
        <principle>Follow Beck's "Tidy First" approach by separating structural changes from behavioral changes</principle>
        <principle>Maintain high code quality throughout development</principle>
    </core-principles>

    <tooling-standards>
        <title>TOOLING AND ENVIRONMENT STANDARDS</title>
        <standard>
            <tool>just</tool>
            <rule>Use 'just' as the primary command runner for all common tasks (e.g., just format, just lint, just test, just verify)</rule>
        </standard>
        <standard>
            <tool>pnpm</tool>
            <rule>Use 'pnpm' for all Node.js package management (e.g., pnpm install, pnpm add). Do not use npm, yarn, or bun</rule>
        </standard>
        <standard>
            <tool>uv (Python)</tool>
            <rule>All Python scripts and tools must be executed via 'uv'. Use the 'uv run' command (e.g., uv run python -m ...)</rule>
        </standard>
        <standard>
            <tool>YAML</tool>
            <rule>All YAML configuration files must use the '.yaml' extension, not '.yml'</rule>
        </standard>
    </tooling-standards>

    <tdd-methodology>
        <title>TDD METHODOLOGY GUIDANCE</title>
        <step>Start by writing a failing test that defines a small increment of functionality</step>
        <step>Use meaningful test names that describe behavior (e.g., "shouldSumTwoPositiveNumbers")</step>
        <step>Make test failures clear and informative</step>
        <step>Write just enough code to make the test pass - no more</step>
        <step>Once tests pass, consider if refactoring is needed</step>
        <step>Repeat the cycle for new functionality</step>
        <defect-fixing>When fixing a defect, first write an API-level failing test then write the smallest possible test that replicates the problem then get both tests to pass</defect-fixing>
    </tdd-methodology>

    <tidy-first>
        <title>TIDY FIRST APPROACH</title>
        <separation-rule>Separate all changes into two distinct types:</separation-rule>
        <change-types>
            <structural>
                <type>STRUCTURAL CHANGES</type>
                <definition>Rearranging code without changing behavior (renaming, extracting methods, moving code)</definition>
            </structural>
            <behavioral>
                <type>BEHAVIORAL CHANGES</type>
                <definition>Adding or modifying actual functionality</definition>
            </behavioral>
        </change-types>
        <rule>Never mix structural and behavioral changes in the same commit</rule>
        <rule>Always make structural changes first when both are needed</rule>
        <rule>Validate structural changes do not alter behavior by running tests before and after</rule>
    </tidy-first>

    <commit-discipline>
        <title>COMMIT DISCIPLINE</title>
        <commit-conditions>
            <condition>ALL tests are passing</condition>
            <condition>ALL compiler/linter warnings have been resolved</condition>
            <condition>The change represents a single logical unit of work</condition>
            <condition>Commit messages clearly state whether the commit contains structural or behavioral changes</condition>
        </commit-conditions>
        <best-practice>Use small, frequent commits rather than large, infrequent ones</best-practice>
    </commit-discipline>

    <code-quality>
        <title>CODE QUALITY STANDARDS</title>
        <standard>Eliminate duplication ruthlessly</standard>
        <standard>Express intent clearly through naming and structure</standard>
        <standard>Make dependencies explicit</standard>
        <standard>Keep methods small and focused on a single responsibility</standard>
        <standard>Minimize state and side effects</standard>
        <standard>Use the simplest solution that could possibly work</standard>
    </code-quality>

    <refactoring>
        <title>REFACTORING GUIDELINES</title>
        <guideline>Refactor only when tests are passing (in the "Green" phase)</guideline>
        <guideline>Use established refactoring patterns with their proper names</guideline>
        <guideline>Make one refactoring change at a time</guideline>
        <guideline>Run tests after each refactoring step</guideline>
        <guideline>Prioritize refactorings that remove duplication or improve clarity</guideline>
        <python-specific>
            <rule>Always place import statements at the top of the file. Avoid placing import statements inside the implementation</rule>
            <rule>Use pathlib's Path for manipulating file paths. os.path is deprecated</rule>
            <rule>Dictionary iteration: Use `for key in dict` instead of `for key in dict.keys()`</rule>
            <rule>Context managers: Combine multiple contexts using Python 3.10+ parentheses</rule>
        </python-specific>
    </refactoring>

    <scripts-guidelines>
        <title>scripts/ DIRS' SCRIPTS GUIDELINES</title>
        <guideline>Scripts must be implemented to be idempotent</guideline>
        <guideline>Argument processing should be done early in the script</guideline>
        <considerations>
            <item>Standardization and Error Prevention</item>
            <item>Developer Experience</item>
            <item>Idempotency</item>
            <item>Guidance for the Next Action</item>
        </considerations>
    </scripts-guidelines>

    <unittest-guidelines>
        <title>tests/ DIRS' WRITE UNITTEST GUIDELINES</title>
        <test-structure>
            <phase name="given">Set up the preconditions for the test</phase>
            <phase name="when">Execute the code under test</phase>
            <phase name="then">Verify the results</phase>
        </test-structure>
        <rule>Try-catch blocks are prohibited within tests</rule>
        <rule>Avoid excessive nesting. Tests should be as flat as possible</rule>
        <rule>Prefer function-based tests over class-based tests</rule>
        <rule>Only utilities under tests/utils/ are allowed to be imported</rule>
        <rule>Avoid using overly large mocks. Prefer real code over mocks</rule>
    </unittest-guidelines>

    <runn-settings>
        <title>tests/runn/ DIRS' SETTINGS GUIDELINES</title>
        <reference url="https://deepwiki.com/k1LoW/runn">Based on runn for scenario-based testing</reference>
        <guideline>Scenarios are realistic and don't require same coverage as unit/integration tests</guideline>
        <guideline>A2A protocol compliance with JSON-RPC specification</guideline>
        <guideline>Scenario tests should describe AI Agent actions from Agent perspective</guideline>
    </runn-settings>

    <workflow>
        <title>EXAMPLE TDD WORKFLOW</title>
        <steps>
            <step number="1">Write a simple failing test for a small part of the feature</step>
            <step number="2">Implement the bare minimum to make it pass</step>
            <step number="3">Run tests to confirm they pass (Green)</step>
            <step number="4">Make any necessary structural changes (Tidy First), running tests after each change</step>
            <step number="5">Commit structural changes separately</step>
            <step number="6">Add another test for the next small increment of functionality</step>
            <step number="7">Repeat until complete, committing behavioral changes separately</step>
            <step number="8">Run commands (just format, just lint) to ensure code quality</step>
        </steps>
        <principle>Always write one test at a time, make it run, then improve structure</principle>
        <principle>Always run all tests (except long-running) each time</principle>
    </workflow>

    <agent-workflow-guide>
        <title>AGENT WORKFLOW GUIDE</title>
        <description>To contribute safely and consistently, follow this checklist IN ORDER whenever you work on the repository:</description>
        <steps>
            <step number="1" name="Read the README">
                <guideline>Refresh yourself on the project goals, structure, scripts, and prerequisites in README.md</guideline>
            </step>
            <step number="2" name="Sync in AGENT_CHAT">
                <guideline>Check AGENT_CHAT.md for in-progress work to avoid conflicts</guideline>
                <guideline>Read the entire file before adding anything</guideline>
                <guideline>Pick a short, task-themed username (e.g., draggable-window) and wrap your plan/updates in a matching XML tag: &lt;draggable-window&gt;...&lt;/draggable-window&gt;</guideline>
                <guideline>Inside that tag, clearly list the files you expect to modify and keep your running plan/progress notes there</guideline>
                <guideline>If another agent already claimed a file you need, wait until they remove their tag before beginning work on it</guideline>
                <guideline>When you finish, remove ONLY the XML block you added—leave other agents' entries intact</guideline>
            </step>
            <step number="3" name="Research the codebase">
                <guideline>Inspect the files relevant to your task before editing. Trace current implementations to understand existing behavior and dependencies</guideline>
                <guideline>If you need documentation for third-party APIs or libraries, use the Parallel MCP web search to gather the latest references before coding</guideline>
                <guideline>When you hit runtime or tooling errors, search the web with Parallel first to collect fixes or known workarounds before resorting to trial-and-error debugging</guideline>
            </step>
            <step number="4" name="Plan appropriately">
                <guideline>For large changes, draft a clear plan and get confirmation from the requester before coding</guideline>
                <guideline>For small or straightforward tasks, form a quick mental or written plan and move straight to implementation</guideline>
            </step>
            <step number="5" name="Execute the plan">
                <guideline>Apply the necessary code changes, keeping diffs focused and well-explained with minimal but helpful comments when needed</guideline>
            </step>
            <step number="6" name="Run the full verification suite">
                <guideline>Execute 'just verify'. Address any failures before proceeding</guideline>
            </step>
            <step number="7" name="Add or update tests">
                <guideline>Before committing long-term tests, run an ad-hoc Playwright pass: PLAYWRIGHT_SKIP_WEB_SERVER=1 pnpm exec playwright test (use --headed to watch)</guideline>
                <guideline>This smoke check should catch console errors or obvious regressions while you iterate</guideline>
                <guideline>Ensure new behavior is covered by automated tests. Run 'just verify' again after adding tests</guideline>
            </step>
            <step number="8" name="Review documentation">
                <guideline>Re-read README.md. If the change affects setup, usage, or workflows, update the documentation accordingly</guideline>
            </step>
        </steps>
        <additional-rules>
             <rule>NEVER run 'pnpm run dev' or 'pnpm run build' directly; the dev server is handled externally, and 'just verify' is used to validate changes</rule>
            <rule>Keep AGENT_CHAT.md tidy: only edit your own notes, and clear them when you wrap up</rule>
        </additional-rules>
        <summary>Following these steps helps keep the project stable and makes future collaboration smoother</summary>
    </agent-workflow-guide>

    <justfile-guidelines>
        <title>JUSTFILE ARGUMENTS (MANDATORY RULE)</title>
        <rule>
            Do NOT re-implement argument parsing or conditional flag construction inside just recipes.
            Always leverage just's parameter system or invoke the target CLI with explicit, direct arguments.
        </rule>
        <allowed>
            <item>Define recipe parameters with sane defaults, e.g.: `recipe arg1="" flag=false`</item>
            <item>Pass parameters directly to commands, e.g.: `uv run python -m app --name {{arg1}} $([ "{{flag}}" = "true" ] && echo --flag)`</item>
            <item>Split behaviors into multiple simple recipes if optionality gets complex.</item>
        </allowed>
        <forbidden>
            <item>Building flag variables via shell conditionals (e.g., `ENGINE_FLAG=""; [ -n "{{engine}}" ] && ENGINE_FLAG="--engine {{engine}}"`)</item>
            <item>Secondary key=value parsing loops (`ARGS=...; for kv in $ARGS; do ...`)</item>
            <item>Normalizing positional vs key=value tokens inside recipes</item>
        </forbidden>
        <rationale>
            <item>Keeps recipes declarative, predictable, and simple to maintain.</item>
            <item>Avoids subtle shell parsing bugs and improves developer ergonomics.</item>
            <item>Aligns with Tidy First: avoid needless indirection in shell glue.</item>
        </rationale>
        <enforcement>
            This is an absolute rule for this repository. Code review should reject any PR that
            reintroduces argument re-parsing or complex flag-assembly logic in justfile.
        </enforcement>
    </justfile-guidelines>
</development-guidelines>
