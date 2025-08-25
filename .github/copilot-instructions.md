## 1. Greeting
- Always start each response with "Hi Boss Huân."

## 2. Package Management
- Use npm as the default package manager.

## 3. File Placement
- Ensure that generated files are placed in the correct directories according to the project structure.

## 4. Code Comments
- Do not generate comments in the source code by default. Provide documentation or comments only for complex parts (e.g., APIs, algorithms) when necessary.

## 5. Mock Data Separation
- Keep mock data separate from the main source code.

## 6. Clean Codebase
- Maintain a clean project by eliminating redundant or unnecessary code.

## 7. Best Practices
- Apply optimal solutions and best practices to complete tasks.

## 8. Task Summary
- Before concluding a task, summarize what has been accomplished and what remains to be done.

## 9. Clean Code Principles
- **Constants Over Magic Numbers**: Use named constants instead of hard-coded values. Place constants at the top of files or in dedicated constant files.
- **Meaningful Names**: Use descriptive names for variables, functions, and classes that clearly indicate their purpose and usage. Avoid abbreviations unless they are universally understood.
- **Smart Comments**: Use comments to explain "why" something is done, not "what." Document APIs, complex algorithms, or non-obvious side effects.
- **Single Responsibility**: Each function should perform exactly one task and be small (ideally under 50 LOC).
- **File Size**: Keep files under 300 LOC with a cognitive complexity of ≤15.
- **Functional Programming**: Prefer functional/declarative patterns; avoid classes unless necessary.
- **DRY (Don't Repeat Yourself)**: Extract repeated code into reusable functions and maintain a single source of truth.
- **Clear Structure**: Organize code logically with consistent naming conventions.
- **Encapsulation**: Hide implementation details and expose clear interfaces.
- **Early Error Handling**: Use guard clauses to handle errors early; avoid deep nesting. Validate external inputs at module boundaries.
- **TypeScript**: Use strict mode when applicable; prefer interfaces over types.
- **Code Quality**: Refactor continuously and address technical debt early.
- **Testing**: Write tests before fixing bugs, ensure tests are readable and cover edge cases.
- **Version Control**: Write clear commit messages, make small focused commits, and use meaningful branch names.

## 10. Documentation Reminders
- **Update Documentation**: When making significant changes to architecture, APIs, or schemas, remind to update `docs/architecture.md`.
- **Record Decisions**: Log important decisions in `docs/decisions.md`.
- **Update Diagrams**: Generate or update diagrams when data flows or architecture change significantly.
- **Dependency Management**: Vet new dependencies, pin critical versions, and avoid committing sensitive information.

## 11. Task Support
- Provide structured feedback and maintain context to ensure continuity.

## 12. Clarification
- If uncertain about an implementation (less than 80% confidence), ask for clarification.

## 13. Specific References
- When discussing changes, reference specific files or code snippets.

## 14. Planning for Major Changes
- For changes affecting multiple files, suggest planning before implementation.

## 15. Language
- Always respond in Vietnamese.