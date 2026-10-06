"""Карточки на фоне: «как себе помочь» (способ и техника) и приветствие"""

from __future__ import annotations

from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from app.config import HELP_BACKGROUND, HELP_FONT
from app.logger import logger

# Свободная светлая зона фона 1024×1535: справа ветка с вазой, сверху справа пятно.
_BOX = (80, 260, 690, 1320)
_TITLE_COLOR = (120, 82, 50)
_TEXT_COLOR = (58, 66, 48)
# Lora — вариативный шрифт, толщину задаём осью wght.
_TITLE_WEIGHT = 600
_TEXT_WEIGHT = 400
# Заголовок одного размера на всех карточках.
_TITLE_SIZE = 60
# Кегль текста: короткую технику пишем крупно, длинную уменьшаем, пока не поместится.
_MAX_SIZE = 84
_MIN_SIZE = 30
_TITLE_LEADING = 1.2
_TEXT_LEADING = 1.35
# Пустое место между абзацами — в долях кегля.
_PARAGRAPH_GAP = 0.6
# Отступы вокруг черты под заголовком.
_RULE_GAP = 20
_RULE_AFTER = 50
_RULE_WIDTH = 120


def help_card(title: str, text: str) -> bytes | None:
    """JPEG карточки. None — нет фона или шрифта: тогда техника показывается текстом."""
    return _card(title, [(text, _TEXT_COLOR, _TEXT_WEIGHT)])


def start_card(title: str, paragraphs: list[str], accent: str) -> bytes | None:
    """Приветствие: абзацы обычным текстом, призыв выбрать эмоцию — цветом заголовка.
    None — нет фона или шрифта: тогда приветствие показывается текстом."""
    blocks = [(paragraph, _TEXT_COLOR, _TEXT_WEIGHT) for paragraph in paragraphs]
    blocks.append((accent, _TITLE_COLOR, _TITLE_WEIGHT))
    return _card(title, blocks)


def _card(title: str, blocks: list[tuple[str, tuple[int, int, int], int]]) -> bytes | None:
    """Заголовок, черта под ним и блоки текста (текст, цвет, толщина) одним кеглем."""
    for path in (HELP_BACKGROUND, HELP_FONT):
        if not path.is_file():
            logger.warning(f"Файл карточки не найден: {path}")
            return None

    image = Image.open(HELP_BACKGROUND).convert("RGB")
    draw = ImageDraw.Draw(image)
    x0, y0, x1, y1 = _BOX
    width = x1 - x0

    title_font = _font(_TITLE_SIZE, _TITLE_WEIGHT)
    title_lines = _wrap(draw, title, title_font, width)
    for size in range(_MAX_SIZE, _MIN_SIZE - 1, -2):
        laid_out = []
        for text, color, weight in blocks:
            font = _font(size, weight)
            laid_out.append((_wrap(draw, text, font, width), font, color))
        gap = size * _PARAGRAPH_GAP
        height = (
            len(title_lines) * title_font.size * _TITLE_LEADING
            + _RULE_GAP + _RULE_AFTER
            + sum(len(lines) for lines, _, _ in laid_out) * size * _TEXT_LEADING
            + (len(laid_out) - 1) * gap
        )
        # Длинное слово («Последовательно») само по себе может не влезть в ширину.
        widest = max(
            draw.textlength(line, font=font) for lines, font, _ in laid_out for line in lines
        )
        if height <= y1 - y0 and widest <= width:
            break

    y = y0 + (y1 - y0 - height) / 2
    for line in title_lines:
        draw.text((x0, y), line, font=title_font, fill=_TITLE_COLOR)
        y += title_font.size * _TITLE_LEADING
    y += _RULE_GAP
    draw.line((x0, y, x0 + _RULE_WIDTH, y), fill=_TITLE_COLOR, width=3)
    y += _RULE_AFTER
    for lines, font, color in laid_out:
        for line in lines:
            draw.text((x0, y), line, font=font, fill=color)
            y += size * _TEXT_LEADING
        y += gap

    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=90)
    return buffer.getvalue()


def _font(size: int, weight: int) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(str(HELP_FONT), size)
    font.set_variation_by_axes([weight])
    return font


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    """Перенос по словам. Переводы строк в тексте сохраняются — пункты списка
    у зависти идут каждый с новой строки."""
    lines: list[str] = []
    for paragraph in text.split("\n"):
        line = ""
        for word in paragraph.split():
            candidate = f"{line} {word}".strip()
            if line and draw.textlength(candidate, font=font) > width:
                lines.append(line)
                line = word
            else:
                line = candidate
        lines.append(line)
    return lines
