Maintenance and Troubleshooting
===============================

Routine tasks
-------------

1. **Update CSV data** – Pull the latest price files regularly and store them
   locally (not in git). Verify the schema stays consistent.
2. **Rotate Kakao keys** – Monitor API usage and rotate REST keys if they are
   compromised or near quota limits.
3. **Refresh dependencies** – Periodically upgrade ``pandas`` and ``requests``
   to benefit from security patches. Re-run the CLI smoke test afterward.
4. **Tag releases** – Create annotated git tags (e.g., ``v0.0.1``) whenever you
   ship notable changes so release notes stay accurate.

Common issues
-------------

``RuntimeError: KAKAO_REST_API_KEY not set``
   The environment variable is missing. Export it in the same shell session or
   configure it via a `.env`/login script.

``지오코딩 성공한 주유소가 없습니다.``
   Kakao Local could not geocode any addresses. Check for typos in the CSV,
   ensure the API key has Local permissions, and confirm there is no firewall
   blocking outbound HTTPS requests.

``후보 주유소가 없습니다(버퍼 기준).``
   All stations were filtered out during ``preselect_candidates``. Increase
   ``ROUTE_BUFFER_KM`` or confirm the CSV actually contains entries for the
   specified corridor.

``requests.exceptions.HTTPError`` from Kakao Mobility
   Usually indicates an invalid request or exhausted quota. Inspect the
   ``--debug`` logs for the failing station and verify origin/destination
   coordinates are valid.

Slow performance
   Excessive API calls can slow down evaluation. Reduce ``TOPK_BY_PRICE`` or
   implement result caching if you run the tool continuously.

Support channels
----------------

* File a GitHub Issue with reproduction details and logs.
* Start a GitHub Discussion if you have general questions or feature ideas.
* Join the community chat (see project website) for interactive help.

Operational checklist
---------------------

* [ ] Confirm Kakao API status pages before large-scale runs.
* [ ] Monitor for HTTP 429 responses indicating rate limiting.
* [ ] Back up local CSV archives in case data sources change.
* [ ] Keep ReadTheDocs documentation in sync with the latest CLI options.

