"""Телесный вход: ощущения, разложенные по зонам тела."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Sensation:
    key: str
    label: str
    # Одна эмоция — однозначное ощущение. Две — спорное, нужен уточняющий вопрос.
    emotions: tuple[str, ...]

    @property
    def is_ambiguous(self) -> bool:
        return len(self.emotions) > 1


@dataclass(frozen=True)
class Zone:
    key: str
    title: str
    sensations: tuple[Sensation, ...]


ZONES: tuple[Zone, ...] = (
    Zone(
        key="head",
        title="Голова и лицо",
        sensations=(
            Sensation("brows", "Хмурятся брови", ("anger",)),
            Sensation("jaws", "Сжимаются челюсти, губы, зубы", ("anger",)),
            Sensation("blood_face", "Кровь приливает к лицу", ("anger",)),
            Sensation("wrinkle", "Сморщивание", ("disgust",)),
            Sensation("gaze_down", "Опущенный взгляд", ("sadness",)),
            Sensation("tears", "Слёзы", ("sadness",)),
            Sensation("smile", "Улыбка", ("joy",)),
            Sensation("gaze_away", "Желание отвести взгляд", ("shame", "guilt")),
            Sensation("red_cheeks", "Покраснение щёк", ("shame", "guilt")),
            Sensation("tearful", "Слезливость", ("resentment",)),
            Sensation("pout", "Надутые губы", ("resentment",)),
        ),
    ),
    Zone(
        key="chest",
        title="Горло, грудь, дыхание",
        sensations=(
            Sensation("fast_breath", "Учащённое дыхание", ("anger",)),
            Sensation("voice_up", "Повышается голос, крик", ("anger",)),
            Sensation("pulse_up", "Повышается пульс, давление", ("anger",)),
            Sensation("shallow_breath", "Поверхностное дыхание", ("fear",)),
            Sensation("heartbeat", "Сердцебиение", ("anxiety",)),
            Sensation("squeal", "Визг радости", ("joy",)),
            Sensation("laughter", "Смех", ("joy",)),
            Sensation("throat_lump", "Ком в горле", ("resentment",)),
        ),
    ),
    Zone(
        key="belly",
        title="Живот",
        sensations=(
            Sensation("nausea", "Тошнота", ("disgust",)),
            Sensation("no_appetite", "Отсутствие аппетита", ("sadness",)),
            Sensation("butterflies", "«Бабочки» в животе", ("joy",)),
            Sensation("belly_cramp", "Сводит живот", ("fear",)),
            Sensation("ibs", "Синдром раздражённого кишечника", ("anxiety",)),
            Sensation("belly_twist", "Скручивает живот", ("anxiety",)),
        ),
    ),
    Zone(
        key="limbs",
        title="Руки, ноги, осанка",
        sensations=(
            Sensation("fists", "Энергия в руках, сжимаются кулаки", ("anger",)),
            Sensation("shoulders_down", "Опущенные плечи", ("sadness",)),
            Sensation("slouch", "Ссутуленность", ("sadness",)),
            Sensation("stability", "Устойчивость", ("joy",)),
            Sensation("open_posture", "Расправленная осанка, плечи, грудь", ("joy",)),
            Sensation("instability", "Неустойчивость", ("fear",)),
            Sensation("numbness", "Онемение конечностей", ("fear",)),
            Sensation("tremble", "Дрожь", ("fear",)),
            Sensation("neck_tension", "Напряжение в области шеи, плеч", ("anxiety",)),
            Sensation("hunched", "Понурость", ("shame", "guilt")),
        ),
    ),
    Zone(
        key="energy",
        title="Энергия и силы",
        sensations=(
            Sensation("heat", "Жар", ("anger",)),
            Sensation("emptiness", "Опустошённость", ("sadness",)),
            Sensation("fatigue", "Усталость, апатия", ("sadness",)),
            Sensation("powerless", "Бессилие", ("sadness",)),
            Sensation("lightness", "Лёгкость", ("joy",)),
            Sensation("warmth", "Теплота", ("joy",)),
            Sensation("energy", "Энергия", ("joy",)),
            Sensation("energetic", "Энергичность", ("joy",)),
            Sensation("no_energy", "Отсутствие сил, энергии", ("sadness", "resentment")),
        ),
    ),
    Zone(
        key="nerves",
        title="Общее состояние и нервы",
        sensations=(
            Sensation("tension", "Напряжение", ("fear", "anxiety")),
            Sensation("freeze", "Замирание", ("fear",)),
            Sensation("slowdown", "Замедление", ("sadness",)),
            Sensation("depressed", "Подавленность", ("sadness",)),
            Sensation("calm", "Спокойствие", ("joy",)),
            Sensation("goosebumps", "Мурашки, возбуждение", ("joy",)),
            Sensation("insomnia", "Бессонница", ("anxiety",)),
            Sensation("fussiness", "Суетливость", ("anxiety",)),
            Sensation("worry", "Волнение", ("anxiety",)),
            Sensation("unease", "Беспокойство", ("anxiety",)),
        ),
    ),
    Zone(
        key="urges",
        title="Порывы и желания",
        sensations=(
            Sensation("detach", "Отстранение", ("disgust",)),
            Sensation("turn_away", "Желание отвернуться", ("disgust",)),
            Sensation("lie_down", "Желание прилечь", ("sadness",)),
            Sensation("sink_ground", "«Охота провалиться сквозь землю»", ("shame", "guilt")),
            Sensation("shrink", "Желание сжаться, исчезнуть, стать невидимым", ("shame", "guilt")),
        ),
    ),
)

ZONES_BY_KEY: dict[str, Zone] = {zone.key: zone for zone in ZONES}
SENSATIONS: dict[str, Sensation] = {
    sensation.key: sensation for zone in ZONES for sensation in zone.sensations
}


def pair_id(emotions: tuple[str, ...]) -> str:
    """Стабильный идентификатор спорной пары, независимый от порядка."""
    return "-".join(sorted(emotions))


# Уточняющие вопросы для спорных ощущений — по паре эмоций, а не по ощущению:
# несколько спорных ощущений с одной парой спрашиваем один раз.
AMBIGUITY_QUESTIONS: dict[str, str] = {
    pair_id(("fear", "anxiety")): (
        "Напряжение бывает и при страхе, и при тревоге. Что вам ближе?\n\n"
        "<b>Страх</b> — опасность конкретная и прямо сейчас.\n"
        "<b>Тревога</b> — тягостное ожидание, что что-то случится."
    ),
    pair_id(("sadness", "resentment")): (
        "Отсутствие сил бывает и при грусти, и при обиде. Что откликается больше?\n\n"
        "<b>Грусть</b> — вы чего-то лишились.\n"
        "<b>Обида</b> — с вами обошлись несправедливо."
    ),
    pair_id(("shame", "guilt")): (
        "Стыд и вина ощущаются в теле похоже. Что ближе?\n\n"
        "<b>Стыд</b> — вам важно, как вас оценят другие.\n"
        "<b>Вина</b> — вы сами считаете, что поступили плохо."
    ),
}
