from dataclasses import dataclass


@dataclass
class Context:
    today: str
    """ISO date (YYYY-MM-DD), injected per-run so the agent can resolve relative
    expressions like 'yesterday' or 'last 7 days' into concrete date ranges."""
