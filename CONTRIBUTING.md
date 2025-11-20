# Contributing to PathPay

Thanks for your interest in improving PathPay! Because the project is a single Python CLI script (`fuel_route_recommender.py`), contributions stay lightweight. Follow the steps below for a smooth review.

## Getting Started
- Fork the repository and clone it locally.
- Use Python 3.9+.
- Install dependencies manually: `pip install pandas requests`.
- Export your Kakao REST API key (`export KAKAO_REST_API_KEY=...`) if you need to run the script with real data.

## Workflow
1. Create a topic branch from `main`: `git checkout -b feature/my-change`.
2. Make focused commits with descriptive messages.
3. Test the CLI (see below) before sending a pull request.
4. Open a PR explaining:
   - What problem you solved or feature you added.
   - How you validated the change (commands, sample output, screenshots, etc.).
   - Any follow-up work or limitations.

## Testing & Validation
- Run the script with representative arguments, e.g.:
  ```bash
  python fuel_route_recommender.py \
    --csv_dir price_csv \
    --fuel 휘발유 \
    --liters 40 --eff 12.5 --alpha 600 \
    --origin "서울 광진구 ..." --dest "서울 송파구 ..."
  ```
- Mock or stub Kakao API calls when writing automated tests; do not commit actual keys.
- For documentation-only changes, proofread commands/links carefully.
- Update `README.md` if you add new options, dependencies, or setup steps.

## Style Guidelines
- Keep 4-space indentation and follow standard Python readability practices.
- Add short comments only where logic is non-obvious.
- Use descriptive names; avoid abbreviations that can confuse new contributors.

## Reporting Issues
- File GitHub Issues for bugs or feature requests.
- Include steps to reproduce, expected vs. actual results, logs (if any), and environment info (OS, Python version).

## Code Review
- Maintainers review PRs for correctness, documentation, and tests.
- Please respond to review feedback promptly and update the branch as needed.

Thank you for helping PathPay improve!
