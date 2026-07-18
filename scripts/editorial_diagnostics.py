#!/usr/bin/env python3
"""Collect raw Editorial Humanizer observations without scoring authorship or quality."""

import re
import statistics
from collections import Counter


WORD_PATTERN = re.compile(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*")
SENTENCE_PATTERN = re.compile(r"[^.!?]+(?:[.!?]+|$)")
BOLD_LABEL_PATTERN = re.compile(r"(?m)^\s*[-*]\s+\*\*[^*]+\*\*\s*[:.]?")
TRANSITIONS = (
    "additionally",
    "certainly",
    "consequently",
    "furthermore",
    "however",
    "indeed",
    "moreover",
    "nevertheless",
    "nonetheless",
    "notably",
    "thus",
)
VOCABULARY_GROUPS = {
    "business_jargon": (
        "ecosystem",
        "facilitate",
        "foster",
        "leverage",
        "robust",
        "scalable",
        "seamless",
        "streamline",
        "synergy",
        "unlock",
    ),
    "significance_language": (
        "crucial",
        "groundbreaking",
        "important",
        "pivotal",
        "remarkable",
        "significant",
        "transformative",
        "unprecedented",
        "vital",
    ),
}


def words(text):
    return [match.group(0).lower() for match in WORD_PATTERN.finditer(text)]


def word_count_distribution(segments):
    counts = []
    for segment in segments:
        segment_word_count = len(words(segment))
        if segment_word_count:
            counts.append(segment_word_count)
    if not counts:
        return {"counts": [], "minimum": 0, "maximum": 0, "mean": 0.0, "stdev": 0.0}
    return {
        "counts": counts,
        "minimum": min(counts),
        "maximum": max(counts),
        "mean": round(statistics.fmean(counts), 2),
        "stdev": round(statistics.pstdev(counts), 2),
    }


def sentence_segments(text):
    return [
        match.group(0).strip()
        for match in SENTENCE_PATTERN.finditer(text)
        if match.group(0).strip()
    ]


def paragraph_segments(text):
    return [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n", text)
        if paragraph.strip()
    ]


def repeated_phrases(text, size=3, limit=10):
    tokens = words(text)
    phrases = Counter(
        tuple(tokens[index : index + size])
        for index in range(max(0, len(tokens) - size + 1))
    )
    candidates = [
        (" ".join(phrase), count)
        for phrase, count in phrases.items()
        if count > 1 and any(len(token) > 3 for token in phrase)
    ]
    candidates.sort(key=lambda item: (-item[1], item[0]))
    return [{"phrase": phrase, "count": count} for phrase, count in candidates[:limit]]


def transition_counts(text):
    token_counts = Counter(words(text))
    return {
        transition: token_counts[transition]
        for transition in TRANSITIONS
        if token_counts[transition]
    }


def vocabulary_clusters(text):
    token_counts = Counter(words(text))
    clusters = {}
    for group_name, vocabulary in VOCABULARY_GROUPS.items():
        matches = {
            term: token_counts[term]
            for term in vocabulary
            if token_counts[term]
        }
        if matches:
            clusters[group_name] = {
                "distinct_terms": len(matches),
                "total_occurrences": sum(matches.values()),
                "terms": matches,
            }
    return clusters


def repeated_paragraph_endings(text):
    endings = []
    for paragraph in paragraph_segments(text):
        sentences = sentence_segments(paragraph)
        if sentences:
            ending = " ".join(words(sentences[-1]))
            if ending:
                endings.append(ending)
    counts = Counter(endings)
    return [
        {"ending": ending, "count": count}
        for ending, count in sorted(counts.items())
        if count > 1
    ]


def analyze_text(text):
    token_count = len(words(text))
    em_dash_count = text.count("—")
    return {
        "word_count": token_count,
        "sentence_word_counts": word_count_distribution(sentence_segments(text)),
        "paragraph_word_counts": word_count_distribution(paragraph_segments(text)),
        "em_dash_count": em_dash_count,
        "em_dashes_per_1000_words": (
            round(em_dash_count * 1000 / token_count, 2) if token_count else 0.0
        ),
        "bold_label_count": len(BOLD_LABEL_PATTERN.findall(text)),
        "transition_counts": transition_counts(text),
        "vocabulary_clusters": vocabulary_clusters(text),
        "repeated_phrases": repeated_phrases(text),
        "repeated_paragraph_endings": repeated_paragraph_endings(text),
    }
