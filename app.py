from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd
from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

DATA_FILE = Path(__file__).with_name("Loldle Data.xlsx")

COLUMNS = ["Gender", "Position", "Species", "Resource", "Range", "Region", "Year"]


def load_data() -> pd.DataFrame:
    df = pd.read_excel(DATA_FILE)
    df["Year"] = df["Year"].astype(int)
    return df.reset_index(drop=True)


BASE_DF = load_data()


def split_values(value: object, separator: str) -> list[str]:
    if pd.isna(value):
        return []
    return [part.strip() for part in str(value).split(separator) if part.strip()]


def has_overlap(candidate_value: object, guess_value: object, separator: str) -> bool:
    candidate_set = set(split_values(candidate_value, separator))
    guess_set = set(split_values(guess_value, separator))
    return bool(candidate_set & guess_set)


def is_partial_match(candidate_value: object, guess_value: object, separator: str) -> bool:
    """Yellow: candidate shares at least one value, but is not exactly the same."""
    candidate_parts = split_values(candidate_value, separator)
    guess_parts = split_values(guess_value, separator)
    if not candidate_parts or not guess_parts:
        return False
    return bool(set(candidate_parts) & set(guess_parts)) and set(candidate_parts) != set(guess_parts)


def filter_single_choice(df: pd.DataFrame, column: str, guess_value: object, result: str) -> pd.DataFrame:
    if result == "green":
        return df[df[column] == guess_value]
    if result == "red":
        return df[df[column] != guess_value]
    # Yellow normally does not apply to Gender/Resource; keep df unchanged if selected.
    return df


def filter_multi_choice(df: pd.DataFrame, column: str, guess_value: object, result: str) -> pd.DataFrame:
    separator = ", "
    if result == "green":
        return df[df[column] == guess_value]
    if result == "red":
        mask = ~df[column].apply(lambda value: has_overlap(value, guess_value, separator))
        return df[mask]
    if result == "yellow":
        mask = df[column].apply(lambda value: is_partial_match(value, guess_value, separator))
        return df[mask]
    return df

def filter_year(df: pd.DataFrame, guess_year: int, result: str) -> pd.DataFrame:
    if result == "green":
        return df[df["Year"] == guess_year]
    if result == "newer":
        return df[df["Year"] > guess_year]
    if result == "older":
        return df[df["Year"] < guess_year]
    return df


def solve_step(current_df: pd.DataFrame, champion_name: str, results: dict[str, str]) -> pd.DataFrame:
    guess_rows = BASE_DF.loc[BASE_DF["Name"] == champion_name]
    if guess_rows.empty:
        raise ValueError(f"Champion not found: {champion_name}")

    guess = guess_rows.iloc[0]
    df = current_df.copy()

    df = filter_single_choice(df, "Gender", guess["Gender"], results["Gender"])
    df = filter_multi_choice(df, "Position", guess["Position"], results["Position"])
    df = filter_multi_choice(df, "Species", guess["Species"], results["Species"])
    df = filter_single_choice(df, "Resource", guess["Resource"], results["Resource"])
    df = filter_multi_choice(df, "Range", guess["Range"], results["Range"])
    df = filter_multi_choice(df, "Region", guess["Region"], results["Region"])
    df = filter_year(df, int(guess["Year"]), results["Year"])

    return df.drop(columns=["checker"], errors="ignore").reset_index(drop=True)


def current_candidates() -> pd.DataFrame:
    # Important: an empty list is a valid state meaning 0 candidates.
    # Do not use `if not names`, because that turns 0 candidates back into all candidates.
    names = session.get("candidate_names")
    if names is None:
        return BASE_DF.copy()
    return BASE_DF[BASE_DF["Name"].isin(names)].reset_index(drop=True)


@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    candidates = current_candidates()

    if request.method == "POST":
        champion_name = request.form.get("champion_name", "").strip()
        results = {column: request.form.get(column, "") for column in COLUMNS}

        try:
            before_count = len(candidates)
            candidates = solve_step(candidates, champion_name, results)
            session["candidate_names"] = candidates["Name"].tolist()
            session.modified = True

            history = session.get("history", [])
            history.append({
                "champion_name": champion_name,
                "Gender": results["Gender"],
                "Position": results["Position"],
                "Species": results["Species"],
                "Resource": results["Resource"],
                "Range": results["Range"],
                "Region": results["Region"],
                "Year": results["Year"],
                "before_count": before_count,
                "count": len(candidates),
            })
            session["history"] = history

            # Render immediately instead of redirecting, so the updated table is visible right away.
        except Exception as exc:
            error = str(exc)

    champion_names = BASE_DF["Name"].sort_values().tolist()
    candidate_rows = candidates[COLUMNS[:0] + ["Name"] + COLUMNS].to_dict(orient="records")

    return render_template(
        "index.html",
        champion_names=champion_names,
        columns=COLUMNS,
        candidates=candidate_rows,
        count=len(candidates),
        error=error,
        history=session.get("history", []),
    )


@app.route("/reset", methods=["POST"])
def reset():
    session.pop("candidate_names", None)
    session.pop("history", None)
    session.modified = True
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run()
