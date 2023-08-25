"""Tools to dedupe collection."""

from __future__ import annotations

from collection_keeper.dedupe.images import mark_duplicates, update_phashes

__all__: list[str] = ["update_phashes", "mark_duplicates"]
