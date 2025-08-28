import os
import re
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from shiritori import (
    is_allowed_input,
    get_required_head,
    validate_new_word,
)

import google.generativeai as genai

app = Flask(__name__, static_folder="static", template_folder="templates")

# Configure Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    model = None


@app.route("/")
def index():
    return render_template("index.html")


def ai_pick_next_word(required_head: str, history: list[str]) -> tuple[str | None, str | None]:
    """
    Ask Gemini for a single hiragana word starting with required_head and not repeating.
    Returns (word, error_message). word is None if failed.
    """
    if not model:
        return None, "Gemini APIキーが設定されていません（.env の GOOGLE_API_KEY）。"

    history_str = "、".join(history) if history else "なし"
    system_rules = (
        "あなたは日本語のひらがなのみで遊ぶしりとりのAIです。\n"
        "ルール:\n"
        "- 返答は1語のみ。余計な説明や句読点、改行は入れない。\n"
        "- ひらがなのみ。カタカナ・漢字・英数字・記号は使わない（ハイフン'-'は単語内に含まれても良い）。\n"
        "- 語尾が『ん』になる単語は絶対に出さない。\n"
        "- これまで出た単語は二度と出さない。\n"
        "- 最初の文字は必ず『{head}』から始める。小さい文字は大きい文字として扱う。\n"
        "- 例：『ゃ』→『や』、『ょ』→『よ』、『っ』→『つ』など。\n"
        "- 出力は1語のみ。\n"
    ).format(head=required_head)

    prompt = (
        f"これまでの単語: {history_str}\n"
        f"次の単語の最初の文字: {required_head}\n"
        f"条件に合う日本語のひらがな1語だけを出力して。"
    )

    try:
        resp = model.generate_content([system_rules, prompt])
        text = (resp.text or "").strip()
        # Normalize: keep first line, strip spaces
        candidate = re.split(r"\s+|\n|\r", text)[0]
        return candidate, None
    except Exception as e:
        return None, f"Gemini呼び出しエラー: {e}"


@app.post("/api/turn")
def api_turn():
    data = request.get_json(force=True)
    history = data.get("history", []) or []
    user_input = (data.get("user_input", "") or "").strip()

    # Limit: maximum 20 user turns
    user_turns = (len(history) // 2)  # history alternates [user, ai, user, ai, ...] if user starts

    # Compute required head from last word in history (if any)
    required_head = None
    if history:
        required_head = get_required_head(history[-1])

    # Validate user's word
    ok, message = validate_new_word(user_input, history, required_head)
    if not ok:
        return jsonify({
            "status": "lose",
            "loser": "user",
            "reason": message,
            "history": history,
        })

    # Append user's valid word
    history.append(user_input)
    user_turns += 1

    # Draw if reached 20 user inputs
    if user_turns >= 20:
        return jsonify({
            "status": "draw",
            "reason": "20回の入力に達しました。引き分けです。",
            "history": history,
        })

    # AI's turn
    head = get_required_head(user_input)

    # Try up to 2 times
    ai_word = None
    err = None
    for attempt in range(2):
        candidate, err = ai_pick_next_word(head, history)
        if not candidate:
            break
        ok, msg = validate_new_word(candidate, history, head)
        if ok:
            ai_word = candidate
            break
        else:
            # tighten prompt next round by adding negative feedback (not implemented, retry anyway)
            err = msg

    if not ai_word:
        # AI failed to produce a valid word -> AI loses
        return jsonify({
            "status": "lose",
            "loser": "ai",
            "reason": err or "AIが有効な単語を出せませんでした。",
            "history": history,
        })

    # Append AI word
    history.append(ai_word)

    return jsonify({
        "status": "continue",
        "ai_word": ai_word,
        "next_head": get_required_head(ai_word),
        "history": history,
    })


if __name__ == "__main__":
    # For local dev
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
