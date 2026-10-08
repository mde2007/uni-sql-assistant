(function () {
  const script = document.currentScript;
  const API_URL = script.dataset.api || "http://localhost:8000";

  // Стили лежат рядом с widget.js
  const css = document.createElement("link");
  css.rel = "stylesheet";
  css.href = script.src.replace("widget.js", "widget.css");
  document.head.appendChild(css);

  // Номер сессии, чтобы в логах было видно, какие вопросы от одного человека
  let sessionId = sessionStorage.getItem("uc_session");
  if (!sessionId) {
    sessionId = Math.random().toString(36).slice(2);
    sessionStorage.setItem("uc_session", sessionId);
  }

  // ---------- Разметка ----------
  const openButton = document.createElement("button");
  openButton.className = "uc-open";
  openButton.textContent = "Ассистент";
  document.body.appendChild(openButton);

  const panel = document.createElement("div");
  panel.className = "uc-panel uc-hidden";
  panel.innerHTML = `
    <div class="uc-header">
      <img src="RGU_Gubkina.jpg" class="uc-header-logo">
      <span>Ассистент по данным университета</span>
      <button class="uc-close">×</button>
    </div>
    <div class="uc-messages"></div>
    <div class="uc-input-row">
      <input class="uc-input" type="text" maxlength="500" placeholder="Задайте вопрос...">
      <button class="uc-send">Отправить</button>
    </div>`;
  document.body.appendChild(panel);

  const messages = panel.querySelector(".uc-messages");
  const input = panel.querySelector(".uc-input");
  const sendButton = panel.querySelector(".uc-send");

  openButton.onclick = () => panel.classList.toggle("uc-hidden");
  panel.querySelector(".uc-close").onclick = () => panel.classList.add("uc-hidden");

  // ---------- Помощники ----------
  function addElement(parent, tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;  // безопасно, без innerHTML
    parent.appendChild(element);
    return element;
  }

  function scrollDown() {
    messages.scrollTop = messages.scrollHeight;
  }

  // ---------- Таблица с пагинацией ----------
  function renderTable(container, data) {
    container.innerHTML = "";  // очистка контейнера, данных тут нет
    if (!data.rows || data.rows.length === 0) {
      addElement(container, "div", "uc-muted", "Запрос выполнен, строк не найдено.");
      return;
    }

    const wrap = addElement(container, "div", "uc-table-wrap");
    const table = addElement(wrap, "table", "uc-table");
    const headRow = addElement(addElement(table, "thead"), "tr");
    data.columns.forEach(column => addElement(headRow, "th", null, column));

    const body = addElement(table, "tbody");
    data.rows.forEach(row => {
      const tr = addElement(body, "tr");
      row.forEach(value => addElement(tr, "td", null, value === null ? "—" : String(value)));
    });

    const pages = Math.ceil(data.total_rows / data.page_size);
    addElement(container, "div", "uc-muted", `Всего строк: ${data.total_rows}`);
    if (pages > 1) {
      const pager = addElement(container, "div", "uc-pager");
      const prev = addElement(pager, "button", null, "←");
      addElement(pager, "span", null, `${data.page} / ${pages}`);
      const next = addElement(pager, "button", null, "→");
      prev.disabled = data.page <= 1;
      next.disabled = data.page >= pages;
      prev.onclick = () => loadPage(container, data.query_id, data.page - 1);
      next.onclick = () => loadPage(container, data.query_id, data.page + 1);
    }
  }

  async function loadPage(container, queryId, page) {
    try {
      const response = await fetch(`${API_URL}/api/result/${queryId}?page=${page}`);
      const data = await response.json();
      if (data.error) {
        container.textContent = data.error;
        return;
      }
      renderTable(container, data);
    } catch (e) {
      container.textContent = "Не удалось загрузить страницу.";
    }
  }

  // ---------- Блоки SQL и объяснения ----------
  function addSqlBlock(parent, sql) {
    const details = addElement(parent, "details", "uc-details");
    addElement(details, "summary", null, "SQL-запрос");
    addElement(details, "pre", "uc-sql", sql);
  }

  function addExplanation(parent, ex) {
    if (!ex || Object.keys(ex).length === 0) return;
    const details = addElement(parent, "details", "uc-details");
    addElement(details, "summary", null, "Как устроен запрос");
    const list = addElement(details, "ul");
    addElement(list, "li", null, "Таблицы: " + (ex.tables || []).join(", "));
    if (ex.joins && ex.joins.length) addElement(list, "li", null, "Соединения: " + ex.joins.join("; "));
    if (ex.filters) addElement(list, "li", null, "Фильтры: " + ex.filters);
    if (ex.group_by && ex.group_by.length) addElement(list, "li", null, "Группировка: " + ex.group_by.join(", "));
    if (ex.aggregates && ex.aggregates.length) addElement(list, "li", null, "Вычисления: " + ex.aggregates.join(", "));
    if (ex.limit) addElement(list, "li", null, "Ограничение строк: " + ex.limit);
  }

  // ---------- Ответ ассистента ----------
  function renderAnswer(data) {
    const message = addElement(messages, "div", "uc-msg uc-bot");

    if (data.error) {
      addElement(message, "div", "uc-error", data.error);
      if (data.sql) addSqlBlock(message, data.sql);
      return;
    }

    addElement(message, "div", null, data.answer);
    if (data.warning) addElement(message, "div", "uc-warning", data.warning);
    addSqlBlock(message, data.sql);
    addExplanation(message, data.explanation);
    renderTable(addElement(message, "div"), data);
  }

  // ---------- Заглушка для работы без backend ----------
  function mockResponse(question) {
    return {
      query_id: "mock",
      answer: "Это тестовый ответ на вопрос: " + question,
      sql: "SELECT p.name, count(*) AS applications\nFROM v_applications AS a\nJOIN programs AS p ON p.id = a.program_id\nGROUP BY p.name\nLIMIT 1000",
      explanation: { tables: ["v_applications", "programs"], aggregates: ["COUNT(*)"], limit: "1000" },
      columns: ["name", "applications"],
      rows: [["Экономика", 412], ["Программная инженерия", 389]],
      total_rows: 2, page: 1, page_size: 50, warning: null, error: null,
    };
  }

  // ---------- Отправка вопроса ----------
  async function send() {
    const question = input.value.trim();
    if (!question) return;

    input.value = "";
    addElement(messages, "div", "uc-msg uc-user", question);
    const loader = addElement(messages, "div", "uc-msg uc-bot uc-loader", "Составляю запрос...");
    sendButton.disabled = true;
    scrollDown();

    try {
      let data;
      if (API_URL === "mock") {
        await new Promise(resolve => setTimeout(resolve, 800));  // имитация ожидания
        data = mockResponse(question);
      } else {
        const response = await fetch(API_URL + "/api/ask", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question: question, session_id: sessionId }),
        });
        data = await response.json();
        if (!response.ok) data = { error: "Сервер вернул ошибку " + response.status };
      }
      loader.remove();
      renderAnswer(data);
    } catch (e) {
      loader.remove();
      renderAnswer({ error: "Нет связи с сервером." });
    }

    sendButton.disabled = false;
    input.focus();
    scrollDown();
  }

  sendButton.onclick = send;
  input.addEventListener("keydown", event => {
    if (event.key === "Enter") send();
  });
})();