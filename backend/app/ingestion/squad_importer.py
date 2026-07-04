from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
OFFICIAL_SQUAD_PDF = PROJECT_ROOT / "data" / "raw" / "SquadLists-English.pdf"
CURATED_PLAYER_CSV = PROJECT_ROOT / "data" / "seed" / "player_profiles.csv"


BOOL_FIELDS = {"penalty_taker", "set_piece_taker", "aerial_threat", "creative_threat"}
FLOAT_FIELDS = {
    "expected_minutes",
    "starting_probability",
    "goals_per_90",
    "shots_per_90",
    "xg_per_90",
    "mvp_rating_base",
}


def _coerce_row(row: dict[str, str]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {key: value.strip() for key, value in row.items() if key is not None}
    for field in FLOAT_FIELDS:
        cleaned[field] = float(cleaned.get(field, 0) or 0)
    for field in BOOL_FIELDS:
        cleaned[field] = str(cleaned.get(field, "")).lower() in {"true", "1", "yes", "y"}
    return cleaned


def load_curated_player_profiles(csv_path: Path = CURATED_PLAYER_CSV) -> list[dict[str, Any]]:
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing curated player profile CSV: {csv_path}")
    with csv_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return [_coerce_row(row) for row in reader]


def try_load_official_squad_pdf(pdf_path: Path = OFFICIAL_SQUAD_PDF) -> list[dict[str, Any]]:
    """Best-effort official PDF hook.

    FIFA squad-list PDFs change layout between competitions and are brittle to
    parse reliably without a dedicated extraction pass. This hook exists so a
    future implementation can replace the curated CSV without changing the
    demo-data layer. For now, the app falls back to the curated CSV.
    """

    if not pdf_path.exists():
        return []
    try:
        import pypdf  # type: ignore[import-not-found]
    except ImportError:
        return []

    try:
        reader = pypdf.PdfReader(str(pdf_path))
        _ = "\n".join(page.extract_text() or "" for page in reader.pages[:2])
    except Exception:
        return []
    return []


def load_player_profiles() -> list[dict[str, Any]]:
    official_profiles = try_load_official_squad_pdf()
    if official_profiles:
        return official_profiles
    return load_curated_player_profiles()
