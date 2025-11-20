# Contributing to PathPay

Thanks for your interest in improving PathPay! The guidelines below explain how to propose changes and keep the project consistent.

## Getting Started
- Fork the repository and clone your fork locally.
- Install Python 3.9+ and the required packages: `pip install -r requirements.txt` (or `pip install pandas requests` for this minimal setup).
- Export your Kakao REST API key (`KAKAO_REST_API_KEY`) if you need to run the CLI against real data.

## Workflow
1. Create a feature branch from `main`: `git checkout -b feature/my-change`.
2. Make focused commits with clear messages.
3. Run the linter or basic checks before sending a pull request (see below).
4. Push your branch and open a pull request that describes:
   - What problem you solved.
   - How you tested the change.
   - Any follow-up work required.

## Testing & Validation
- For code changes, run any available unit tests or scripts you add. If the change affects the CLI flow, include example commands or outputs in the PR description.
- When touching documentation only, verify spelling and command accuracy.
- If you introduce dependencies or configuration steps, update `README.md` accordingly.

## Style Guidelines
- Keep Python code formatted with `black` or a consistent 4-space indentation.
- Include concise comments only when logic is non-obvious.
- Prefer descriptive variable and function names; avoid abbreviations that are unclear outside of this project.

## Reporting Issues
- Use GitHub Issues to report bugs or suggest features.
- Include reproduction steps, expected vs. actual behavior, and environment details (OS, Python version, etc.).

## Code Review
- Expect maintainers to review pull requests for correctness, readability, documentation, and test coverage.
- Be responsive to feedback—update the PR or discuss alternative solutions as needed.

Thank you for contributing and helping PathPay grow!
