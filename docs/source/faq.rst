Frequently Asked Questions
==========================

Do I have to share my Kakao REST API key?
   No. The project never stores API keys in git. Each user exports their own
   ``KAKAO_REST_API_KEY`` locally.

Can I analyze regions outside Gwangjin/Songpa?
   Yes. Update the regex in ``load_and_prepare`` to include additional district
   names, or remove the filter entirely.

What if my CSV columns differ from the expected schema?
   Rename your columns to match the required Korean labels or adjust the loader
   to map your custom headers to ``지역``, ``상호``, ``주소``, and price columns.

How accurate are the route estimates?
   Kakao Mobility provides reliable driving estimates, but PathPay compares only
   the primary route vs. one detour route. If your path is highly dynamic,
   consider fetching multiple alternative routes.

Can I automate daily reports?
   Absolutely. Wrap the CLI in a cron job or call its functions from another
   script. Store results in a database or send them via chat as needed.

Why does the app sleep between requests?
   To respect Kakao’s rate limits. You can adjust or remove the ``time.sleep``
   calls at your own risk, but be mindful of API quotas.

Is there a GUI?
   Not yet. The map script outputs Folium HTML, which you can embed in a simple
   web page or integrate into a dashboard.

How do I share bugs or features?
   File a GitHub Issue with steps to reproduce, or start a discussion in the
   community forum listed on the project website.

