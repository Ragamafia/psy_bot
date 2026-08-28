from __future__ import annotations

from app.config import PsychologistSettings

DISCLAIMER = (
    "<i>Бот помогает назвать чувство и немного себя поддержать. "
    "Он не заменяет консультацию психолога и не является медицинской помощью. "
    "Если состояние тяжёлое и не проходит — лучше обратиться к специалисту.</i>"
)

START = (
    "Здравствуйте.\n\n"
    "Давайте разберёмся, что вы сейчас чувствуете и о чём это говорит.\n\n"
    "<b>Выберите эмоцию, которую вы испытываете.</b>\n\n" + DISCLAIMER
)

CHOOSE_EMOTION = "<b>Выберите эмоцию, которую вы испытываете.</b>"

CHOOSE_SHADE = "<b>{emotion}</b>\n\nВыберите оттенок — тот, который точнее описывает ваше состояние."

CHOOSE_ZONE = (
    "Назвать эмоцию бывает трудно — тело знает раньше, чем голова.\n\n"
    "<b>Выберите, где вы что-то замечаете.</b>"
)

CHOOSE_SENSATIONS = (
    "<b>{zone}</b>\n\n"
    "Отметьте всё, что откликается. Можно выбрать несколько, "
    "в том числе в разных зонах."
)

NOTHING_SELECTED = "Отметьте хотя бы одно ощущение"

MEANING = "<b>{emotion}</b>\n\n{meaning}\n\nВыберите, как себе помочь."

MEANING_WITH_SHADE = (
    "<b>{emotion}</b> · {shade}\n\n{meaning}\n\nВыберите, как себе помочь."
)

HELP_BLOCK = "<b>{emotion} · {block}</b>\n\n{text}"

RESULT_SINGLE = (
    "Похоже, вы испытываете <b>{emotion}</b>.\n\n{meaning}\n\nВыберите, как себе помочь."
)

RESULT_MANY_HEADER = "Похоже, вы испытываете {emotions}."

RESULT_MANY_FOOTER = "С чем поработаем сейчас?"

RESULT_TRUNCATED = (
    "<i>Вы отметили много разного — показываю то, что откликнулось сильнее всего.</i>"
)


def final(psy: PsychologistSettings) -> str:
    return (
        "Если хочется разобраться глубже и не в одиночку — можно прийти на сеанс.\n\n"
        f"Психолог: <b>{psy.name}</b>\n"
        f"Написать: {psy.tg_username}\n"
        f"Телефон: {psy.phone}\n"
        f"{psy.city}\n\n" + DISCLAIMER
    )
