const API = window.APP_CONFIG.API_BASE_URL.replace(/\/$/, "");
const $ = (sel) => document.querySelector(sel);
const fmt = (n) => Number(n).toLocaleString("ko-KR");

// ---------- 공통 API 호출 ----------
async function api(path, options = {}) {
  const res = await fetch(API + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let msg = `요청에 실패했습니다 (${res.status})`;
    try {
      const body = await res.json();
      if (typeof body.detail === "string") msg = body.detail;
    } catch (_) { /* JSON이 아니면 기본 메시지 사용 */ }
    throw new Error(msg);
  }
  if (res.status === 204) return null;
  return res.json();
}

function makeButton(label, onClick, extraClass = "") {
  const b = document.createElement("button");
  b.type = "button";
  b.textContent = label;
  b.className = `btn small ${extraClass}`.trim();
  b.addEventListener("click", onClick);
  return b;
}

function formatDate(iso) {
  return iso ? new Date(iso).toLocaleString("ko-KR", { dateStyle: "short", timeStyle: "short" }) : "";
}

// ---------- 탭 전환 ----------
function switchTab(name) {
  document.querySelectorAll(".tab").forEach((b) => b.classList.toggle("active", b.dataset.tab === name));
  document.querySelectorAll(".panel").forEach((p) => p.classList.toggle("active", p.id === `tab-${name}`));
  if (name === "data") loadData();
  if (name === "history") loadConversations();
  if (name === "summary") loadSummary();
}
document.querySelectorAll(".tab").forEach((btn) =>
  btn.addEventListener("click", () => switchTab(btn.dataset.tab))
);

// ---------- 서버 상태 (무료 Render 콜드스타트 대응) ----------
async function wakeServer() {
  const status = $("#server-status");
  const slowTimer = setTimeout(() => {
    status.textContent = "서버를 깨우는 중이에요. 무료 서버는 첫 접속 시 최대 1분 정도 걸릴 수 있어요.";
  }, 2000);
  try {
    await api("/health");
    status.textContent = "● 연결됨";
  } catch (_) {
    status.textContent = "서버에 연결할 수 없어요. 잠시 후 새로고침 해주세요.";
  } finally {
    clearTimeout(slowTimer);
  }
}

// ---------- 채팅 ----------
let currentConvId = null;
const messagesEl = $("#messages");

function addBubble(role, content) {
  const div = document.createElement("div");
  div.className = `msg-bubble ${role}`;
  div.textContent = content;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function renderMessages(list) {
  messagesEl.innerHTML = "";
  list.forEach((m) => addBubble(m.role, m.content));
}

function setLoading(on) {
  $("#loading").classList.toggle("hidden", !on);
  $("#chat-form button").disabled = on;
}

$("#chat-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = $("#chat-input");
  const text = input.value.trim();
  if (!text) return;

  addBubble("user", text);
  input.value = "";
  setLoading(true);
  try {
    const data = await api("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message: text, conversation_id: currentConvId }),
    });
    currentConvId = data.conversation_id;
    addBubble("assistant", data.reply);
    $("#chat-title").textContent = "대화 중 (자동 저장됨)";
  } catch (err) {
    addBubble("assistant", `⚠️ ${err.message}`);
  } finally {
    setLoading(false);
  }
});

$("#new-chat").addEventListener("click", () => {
  currentConvId = null;
  messagesEl.innerHTML = "";
  $("#chat-title").textContent = "새 대화";
});

// ---------- 데이터 관리 (CRUD) ----------
let dataCache = [];

function showMsg(text, isError = false) {
  const el = $("#data-msg");
  el.textContent = text;
  el.className = `msg ${isError ? "error" : "ok"}`;
}

async function loadData() {
  try {
    dataCache = await api("/api/data");
    renderData();
  } catch (err) {
    showMsg(err.message, true);
  }
}

function renderData() {
  const body = $("#data-body");
  body.innerHTML = "";
  if (!dataCache.length) {
    body.innerHTML = '<tr><td colspan="4" class="muted">데이터가 없습니다.</td></tr>';
    return;
  }
  dataCache.forEach((item) => {
    const tr = document.createElement("tr");
    [item.date, fmt(item.value), item.memo].forEach((text) => {
      const td = document.createElement("td");
      td.textContent = text;
      tr.appendChild(td);
    });
    const actions = document.createElement("td");
    actions.className = "actions";
    actions.append(
      makeButton("수정", () => startEdit(item)),
      makeButton("삭제", () => removeData(item.id), "danger")
    );
    tr.appendChild(actions);
    body.appendChild(tr);
  });
}

function startEdit(item) {
  $("#data-id").value = item.id;
  $("#data-date").value = item.date;
  $("#data-value").value = item.value;
  $("#data-memo").value = item.memo;
  $("#data-submit").textContent = "수정 저장";
  $("#data-cancel").classList.remove("hidden");
  $("#data-value").focus();
}

function resetForm() {
  $("#data-form").reset();
  $("#data-id").value = "";
  $("#data-submit").textContent = "추가";
  $("#data-cancel").classList.add("hidden");
}

$("#data-cancel").addEventListener("click", resetForm);

$("#data-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = $("#data-id").value;
  const payload = {
    date: $("#data-date").value,
    value: Number($("#data-value").value),
    memo: $("#data-memo").value.trim(),
  };
  if (!Number.isInteger(payload.value) || payload.value < 0) {
    showMsg("값은 0 이상의 정수여야 합니다.", true);
    return;
  }
  try {
    if (id) {
      await api(`/api/data/${id}`, { method: "PUT", body: JSON.stringify(payload) });
      showMsg("수정되었습니다.");
    } else {
      await api("/api/data", { method: "POST", body: JSON.stringify(payload) });
      showMsg("추가되었습니다.");
    }
    resetForm();
    await loadData();
  } catch (err) {
    showMsg(err.message, true);
  }
});

async function removeData(id) {
  if (!confirm("이 데이터를 삭제할까요?")) return;
  try {
    await api(`/api/data/${id}`, { method: "DELETE" });
    showMsg("삭제되었습니다.");
    await loadData();
  } catch (err) {
    showMsg(err.message, true);
  }
}

// ---------- 대화 기록 ----------
async function loadConversations() {
  const list = $("#conv-list");
  list.innerHTML = "";
  try {
    const items = await api("/api/conversations");
    if (!items.length) {
      list.innerHTML = '<li class="muted" style="padding:12px">저장된 대화가 없습니다.</li>';
      return;
    }
    items.forEach((c) => {
      const li = document.createElement("li");
      li.className = "conv-item";
      const title = document.createElement("strong");
      title.textContent = c.title;
      const meta = document.createElement("small");
      meta.textContent = `${c.message_count}개 메시지 · ${formatDate(c.updated_at)}`;
      li.append(title, meta);
      li.addEventListener("click", () => openConversation(c.id));
      list.appendChild(li);
    });
  } catch (err) {
    list.innerHTML = `<li class="msg error" style="padding:12px">${""}</li>`;
    list.firstChild.textContent = err.message;
  }
}

async function openConversation(id) {
  const detail = $("#conv-detail");
  try {
    const conv = await api(`/api/conversations/${id}`);
    detail.innerHTML = "";

    const head = document.createElement("div");
    head.className = "conv-head";
    const h = document.createElement("h3");
    h.textContent = conv.title;
    head.append(
      h,
      makeButton("이 대화로 이어가기", () => {
        currentConvId = conv.id;
        renderMessages(conv.messages);
        $("#chat-title").textContent = conv.title;
        switchTab("chat");
      }),
      makeButton("삭제", () => removeConversation(id), "danger")
    );

    const wrap = document.createElement("div");
    wrap.className = "conv-messages";
    conv.messages.forEach((m) => {
      const b = document.createElement("div");
      b.className = `msg-bubble ${m.role}`;
      b.textContent = m.content;
      wrap.appendChild(b);
    });

    detail.append(head, wrap);
  } catch (err) {
    detail.innerHTML = "";
    const p = document.createElement("p");
    p.className = "msg error";
    p.textContent = err.message;
    detail.appendChild(p);
  }
}

async function removeConversation(id) {
  if (!confirm("이 대화를 삭제할까요?")) return;
  try {
    await api(`/api/conversations/${id}`, { method: "DELETE" });
    if (currentConvId === id) currentConvId = null;
    $("#conv-detail").innerHTML = '<p class="muted">대화를 선택하세요.</p>';
    loadConversations();
  } catch (err) {
    alert(err.message);
  }
}

// ---------- 데이터 요약 ----------
async function loadSummary() {
  const card = $("#summary-card");
  card.textContent = "불러오는 중...";
  try {
    const s = await api("/api/data/summary");
    if (!s.count) {
      card.textContent = "데이터가 없습니다. '데이터 관리' 탭에서 추가해주세요.";
      return;
    }
    const rows = [
      ["기간", s.period],
      ["레코드 수", `${s.count}개`],
      ["합계", fmt(s.metrics.total)],
      ["평균", fmt(s.metrics.average)],
      ["최대", `${fmt(s.metrics.max)} (${s.best.date})`],
      ["최소", fmt(s.metrics.min)],
      ["최근 트렌드", s.trend],
      ["최신 기록", `${s.latest.date} · ${fmt(s.latest.value)}`],
    ];
    card.innerHTML = "";
    const grid = document.createElement("dl");
    grid.className = "summary-grid";
    rows.forEach(([k, v]) => {
      const dt = document.createElement("dt");
      dt.textContent = k;
      const dd = document.createElement("dd");
      dd.textContent = v;
      grid.append(dt, dd);
    });
    card.appendChild(grid);
  } catch (err) {
    card.textContent = err.message;
  }
}

$("#refresh-summary").addEventListener("click", loadSummary);

// ---------- 시작 ----------
wakeServer();
