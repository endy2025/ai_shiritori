import re
from typing import Optional, Tuple

# Small kana to large mapping
SMALL_TO_LARGE = {
    "ぁ": "あ", "ぃ": "い", "ぅ": "う", "ぇ": "え", "ぉ": "お",
    "ゃ": "や", "ゅ": "ゆ", "ょ": "よ",
    "っ": "つ", "ゎ": "わ",
}

ALLOWED_PATTERN = re.compile(r"^[ぁ-ゖー\-]+$")  # hiragana + long dash + hyphen


def is_allowed_input(s: str) -> bool:
    s = (s or "").strip()
    return bool(ALLOWED_PATTERN.fullmatch(s))


def to_large(ch: str) -> str:
    return SMALL_TO_LARGE.get(ch, ch)


def last_effective_char(word: str) -> Optional[str]:
    if not word:
        return None
    w = word.strip()
    # Remove trailing hyphens or long dashes
    while w and w[-1] in ("-", "ー"):
        w = w[:-1]
    if not w:
        return None
    return w[-1]


def get_required_head(prev_word: str) -> Optional[str]:
    ch = last_effective_char(prev_word)
    if ch is None:
        return None
    return to_large(ch)


def starts_with_required(w: str, head: Optional[str]) -> bool:
    if head is None:
        return True
    if not w:
        return False
    first = to_large(w[0])
    return first == head


def validate_new_word(word: str, history: list[str], required_head: Optional[str]) -> Tuple[bool, str]:
    w = (word or "").strip()
    if not w:
        return False, "ことばを入力してね。"
    if not is_allowed_input(w):
        return False, "ひらがなとハイフン（-）だけを使ってね。"
    if w.endswith("ん"):
        return False, "『ん』で終わったので負けです。"
    if history and w in history:
        return False, "同じ言葉は使えません。"
    if required_head is not None and not starts_with_required(w, required_head):
        return False, f"はじめの文字は『{required_head}』からにしてね。"
    return True, ""
