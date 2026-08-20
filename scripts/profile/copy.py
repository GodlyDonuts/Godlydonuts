from __future__ import annotations

from typing import Any

def authored_copy(theme: str) -> dict[str, Any]:
    day = theme == "light"
    return {
        "copy_label": "DAY COPY" if day else "NIGHT COPY",
        "top_note": (
            "usually a bad sign. usually worth it."
            if day
            else "most of the good ones start after midnight."
        ),
        "bio": (
            [
                "I am a CS student at UCF.",
                "That is the boring line.",
                "I get fixated on questions and build",
                "until they stop being vague.",
            ]
            if day
            else [
                "This was supposed to be a normal profile.",
                "It lasted about ten minutes.",
                "I get fixated on questions and build",
                "until they stop being vague.",
            ]
        ),
        "bio_sub": (
            [
                "Sometimes that means a model. Sometimes a kernel.",
                "Sometimes a product. I do not care what box it fits in.",
            ]
            if day
            else [
                "The layer changes: research, systems, product, kernels.",
                "The question is the only part that stays put.",
            ]
        ),
        "habit_note": (
            "yes, this is slower. no, I have not stopped."
            if day
            else "yes, I know this is inefficient."
        ),
        "list_note": (
            "This list changes faster than my bio."
            if day
            else "the list after midnight."
        ),
        "candid_left": (
            ["I move fast.", "I overthink names.", "I distrust a clean benchmark."]
            if day
            else [
                "I start too much.",
                "I hate leaving a question half-answered.",
                "I know when a result is too clean.",
            ]
        ),
        "candid_right": (
            [
                "I care whether software has aura.",
                "I will argue about rockets for an hour.",
                "I am probably still editing this page.",
            ]
            if day
            else [
                "I rewrite things that were already good.",
                "I will argue about rockets for an hour.",
                "I am still here.",
            ]
        ),
        "still_editing": "still editing." if day else "02:13 and not done.",
        "offscreen": (
            ["lifting / spaceflight / the AI race / too many tabs"]
            if day
            else ["spaceflight / the AI race / too many tabs / probably a benchmark"]
        ),
        "closing": (
            [
                "I want to work on intelligence, autonomy,",
                "and the machinery underneath both.",
            ]
            if day
            else [
                "I want to work on intelligence, autonomy,",
                "and the machinery underneath both. I will rewrite this tomorrow.",
            ]
        ),
    }


