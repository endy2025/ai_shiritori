const historyList = document.getElementById('history');
const form = document.getElementById('form');
const input = document.getElementById('user-input');
const messageEl = document.getElementById('message');
const nextHeadEl = document.getElementById('next-head');
const turnCountEl = document.getElementById('turn-count');

let history = [];
let gameOver = false;

function render() {
  historyList.innerHTML = '';
  history.forEach((w, idx) => {
    const li = document.createElement('li');
    li.textContent = w;
    li.className = idx % 2 === 0 ? 'user' : 'ai';
    historyList.appendChild(li);
  });
  const userTurns = Math.ceil(history.length / 2);
  turnCountEl.textContent = userTurns;
}

function setMessage(msg, color) {
  messageEl.textContent = msg || '';
  messageEl.style.color = color || '#c0392b';
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  if (gameOver) return;
  const val = (input.value || '').trim();
  if (!val) return;

  setMessage('考え中…', '#666');

  try {
    const res = await fetch('/api/turn', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ history, user_input: val })
    });
    const data = await res.json();

    if (data.status === 'lose' && data.loser === 'user') {
      setMessage(`まけ… 理由: ${data.reason}`);
      gameOver = true;
      render();
      return;
    }

    // User word was valid if we reach here; append it
    history.push(val);

    if (data.status === 'draw') {
      setMessage(data.reason, '#333');
      gameOver = true;
      render();
      input.value = '';
      return;
    }

    if (data.status === 'lose' && data.loser === 'ai') {
      setMessage(`あなたの勝ち！ 理由: ${data.reason}`, '#27ae60');
      gameOver = true;
      render();
      input.value = '';
      return;
    }

    if (data.status === 'continue') {
      const aiWord = data.ai_word;
      history.push(aiWord);
      setMessage('つぎのことばを入れてね！', '#333');
      if (data.next_head) {
        nextHeadEl.textContent = data.next_head;
      }
      render();
      input.value = '';
      input.focus();
      return;
    }

    setMessage('エラーが発生しました…');
  } catch (err) {
    console.error(err);
    setMessage('通信エラー… サーバーを確認してね');
  }
});

render();
