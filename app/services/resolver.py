"""Определение эмоции по набору телесных ощущений."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from app.content.body import SENSATIONS, pair_id
from app.content.emotions import EMOTION_ORDER

# Больше трёх эмоций разом человеку в плохом состоянии не помогают, а мешают.
MAX_RESULT_EMOTIONS = 3


@dataclass
class Resolution:
    """Результат разбора отмеченных ощущений."""

    emotions: list[str] = field(default_factory=list)
    # Пары, по которым нужно задать уточняющий вопрос (по одной паре — один вопрос).
    pending: list[str] = field(default_factory=list)
    # Сколько эмоций отсеклось лимитом.
    truncated: int = 0

    @property
    def needs_question(self) -> bool:
        return bool(self.pending)


def resolve(selected: list[str], answers: dict[str, str] | None = None) -> Resolution:
    """Считает голоса эмоций по отмеченным ощущениям"""
    answers = answers or {}
    votes: Counter[str] = Counter()
    ambiguous = []

    for key in selected:
        sensation = SENSATIONS.get(key)
        if sensation is None:
            continue
        if sensation.is_ambiguous:
            ambiguous.append(sensation)
        else:
            votes[sensation.emotions[0]] += 1

    pending: list[str] = []
    for sensation in ambiguous:
        pair = pair_id(sensation.emotions)

        answered = answers.get(pair)
        if answered in sensation.emotions:
            votes[answered] += 1
            continue

        # Counter[...] на отсутствующем ключе возвращает 0 и не создаёт запись.
        confirmed = [emotion for emotion in sensation.emotions if votes[emotion]]
        if confirmed:
            for emotion in confirmed:
                votes[emotion] += 1
        elif pair not in pending:
            pending.append(pair)

    if pending:
        return Resolution(pending=pending)

    ranked = sorted(votes, key=lambda key: (-votes[key], EMOTION_ORDER.index(key)))
    return Resolution(
        emotions=ranked[:MAX_RESULT_EMOTIONS],
        truncated=max(0, len(ranked) - MAX_RESULT_EMOTIONS),
    )
