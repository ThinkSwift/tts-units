#!/usr/bin/env python3
import sys
import re
from collections import defaultdict

CATEGORIES = {
    "ai_future",
    "crypto_basics",
    "food_street",
    "travel_abroad",
    "job_market",
    "health_fitness",
    "music_kpop",
    "movie_scifi",
    "relationships_modern",
    "money_investing",
    "social_media",
    "home_life",
}

def count_words(line: str) -> int:
    return len([w for w in line.strip().split() if w])

def check_sentence_lengths(level: str, text: str) -> list[str]:
    errors = []
    # split by . ? ! but keep it simple
    sentences = re.split(r'[.!?]+', text)
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        n = count_words(s)
        if level == "beginner":
            if n >= 12:
                errors.append(f"beginner sentence too long ({n} words): {s}")
        elif level == "intermediate":
            if n < 10 or n > 18:
                errors.append(f"intermediate sentence length {n} out of range: {s}")
        elif level == "advanced":
            if n < 15 or n > 25:
                errors.append(f"advanced sentence length {n} out of range: {s}")
    return errors

def main(path: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        lines = [ln.rstrip("\n") for ln in f]

    i = 0
    ids_seen = set()
    report = []

    while i < len(lines):
        block = lines[i:i+5]
        if len(block) < 5:
            report.append(f"ERROR: incomplete block starting at line {i+1}")
            break

        id_line, cat_line, title_line, level_line, script_header = block

        # basic field checks
        if not id_line.startswith("id: "):
            report.append(f"ERROR: bad id field at line {i+1}")
        if not cat_line.startswith("category: "):
            report.append(f"ERROR: bad category field at line {i+2}")
        if not title_line.startswith("title: "):
            report.append(f"ERROR: bad title field at line {i+3}")
        if not level_line.startswith("level: "):
            report.append(f"ERROR: bad level field at line {i+4}")
        if script_header != "script:":
            report.append(f"ERROR: missing 'script:' at line {i+5}")

        # parse values
        episode_id = id_line.replace("id: ", "").strip()
        category = cat_line.replace("category: ", "").strip()
        level = level_line.replace("level: ", "").strip()

        # id uniqueness
        if episode_id in ids_seen:
            report.append(f"ERROR: duplicated id: {episode_id}")
        ids_seen.add(episode_id)

        # id/category consistency
        if not episode_id.startswith(f"{category}_"):
            report.append(f"ERROR: id/category mismatch: {episode_id} vs {category}")

        if category not in CATEGORIES:
            report.append(f"ERROR: unknown category: {category}")

        if level not in {"beginner", "intermediate", "advanced"}:
            report.append(f"ERROR: unknown level: {level}")

        # script lines (4 turns)
        script_lines = lines[i+5:i+9]
        if len(script_lines) < 4:
            report.append(f"ERROR: script block too short for id {episode_id}")
        else:
            roles = ["A:", "B:", "A:", "B:"]
            full_text = []
            for idx, (expected, line) in enumerate(zip(roles, script_lines)):
                if not line.startswith(expected):
                    report.append(
                        f"ERROR: turn {idx+1} for {episode_id} should start with '{expected}'"
                    )
                full_text.append(line.split(":", 1)[1])

            # check sentence lengths per level
            text_joined = " ".join(full_text)
            report.extend(
                f"{episode_id}: {msg}" for msg in check_sentence_lengths(level, text_joined)
            )

        # after 4 script lines, expect blank line (or EOF)
        next_index = i + 9
        if next_index < len(lines):
            if lines[next_index].strip() != "":
                report.append(f"ERROR: missing blank line after id {episode_id}")
            i = next_index + 1
        else:
            i = next_index

    # print report
    if not report:
        print("OK: all episodes passed basic validation.")
    else:
        for msg in report:
            print(msg)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python accent_units_validator.py <corpus_file>")
        raise SystemExit(1)
    main(sys.argv[1])
