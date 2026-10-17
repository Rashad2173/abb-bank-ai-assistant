"""Analytics service: every question and answer with its timestamp, and the statistics for the dashboard.

* ``POST /v1/interactions`` — record one interaction (sent by the chat service),
* ``GET  /v1/interactions`` — browse them (newest first, filter by status),
* ``GET  /v1/stats``        — aggregates for the dashboard charts.
"""

__version__ = "1.0.0"
