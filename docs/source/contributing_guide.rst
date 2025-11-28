Contribution Guidelines
=======================

This page summarizes how to propose improvements to PathPay. See the root
``CONTRIBUTING.md`` for the canonical policy.

Workflow checklist
------------------

1. **Fork & branch**
   - Fork ``eunwooo0717/pathpay`` and create a topic branch from ``main``.
2. **Set up the environment**
   - Install dependencies (``pip install pandas requests``).
   - Export ``KAKAO_REST_API_KEY`` if you plan to call Kakao APIs.
3. **Make focused changes**
   - Keep commits small and descriptive.
   - Update or add documentation when you modify behaviors.
4. **Validate**
   - Run the CLI with representative arguments.
   - Capture sample output or screenshots for PR context.
5. **Submit a pull request**
   - Describe the problem, solution, and testing evidence.
   - Link related issues if applicable.

Coding standards
----------------

* Use 4-space indentation and keep modules free of trailing whitespace.
* Limit inline comments to nuanced logic (the code should otherwise be
  self-explanatory).
* Follow PEP 8 naming conventions; avoid cryptic abbreviations.

Documentation expectations
--------------------------

* Update ``README.md`` or the appropriate Sphinx page when CLI flags, external
  dependencies, or workflows change.
* Add release note entries when shipping user-visible features.
* Ensure any diagrams or tables degrade gracefully on mobile devices (use pure
  reStructuredText whenever possible).

Community conduct
-----------------

All contributors must follow the `Code of Conduct <https://github.com/eunwooo0717/pathpay/blob/main/CODE_OF_CONDUCT.md>`_
at the repository root. Be respectful in issues, pull requests, and community
forums.
