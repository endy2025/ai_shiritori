# AIしりとり（Flask + Gemini）

ひらがなでAIと対戦できる しりとりゲームです。かわいいWeb UIつき。

## 必要なもの
- Python 3.10+
- Google Gemini API Key（`GOOGLE_API_KEY`）

## セットアップ（ローカル）
1. プロジェクトをアクティブに設定（Windows）
   - フォルダ: `C:\Users\a.endo\CascadeProjects\ai_shiritori`
2. 依存関係をインストール
   ```bash
   pip install -r requirements.txt
   ```
3. `.env` を作成してAPIキーを入れる
   - `.env.example` をコピーして `.env` を作成
   - `GOOGLE_API_KEY=xxxxx` を設定
4. 起動
   ```bash
   python app.py
   ```
   ブラウザで http://localhost:5000 を開く

## ルール（実装）
- ひらがなとハイフン（-）のみ入力OK
- 語尾が「ん」は負け
- 同じ言葉は負け（重複禁止）
- 小さい文字（ゃゅょぁぃぅぇぉっゎ）は大きくしてつなぐ（例：ゃ→や、っ→つ）
- ハイフンや長音記号（ー）で終わるときは、その直前のひらがなを次の頭文字に使う
- 入力は最大20回（ユーザーの入力回数）。超えたら引き分け

## デプロイ（Render.com）
1. GitHub にリポジトリを作成し、このフォルダをプッシュ
2. Render で「New +」→ Web Service → GitHub リポジトリを選択
3. 確認事項
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --preload --workers=2 --threads=4 --timeout=120`
   - 環境変数 `GOOGLE_API_KEY` を追加
4. デプロイ後のURLにアクセスして遊ぶ

## 開発メモ
- バックエンド: Flask
- フロント: HTML/CSS/JS（シンプル）
- AI: google-generativeai（Gemini 1.5 Flash）
