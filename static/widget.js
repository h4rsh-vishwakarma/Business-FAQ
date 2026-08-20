(function () {
  const config = window.BusinessFAQChatbotConfig || {};
  const apiBaseUrl = (config.apiBaseUrl || window.location.origin).replace(/\/$/, "");
  const sessionKey = "business-faq-chat-session";
  const sessionId = localStorage.getItem(sessionKey) || crypto.randomUUID();
  localStorage.setItem(sessionKey, sessionId);

  const style = document.createElement("style");
  style.textContent = `
    .bfq-launcher {
      position: fixed;
      right: 20px;
      bottom: 20px;
      width: 64px;
      height: 64px;
      border: 0;
      border-radius: 50%;
      background: linear-gradient(135deg, #2e5e4e, #b45d3d);
      color: #fff;
      font-size: 26px;
      cursor: pointer;
      box-shadow: 0 20px 40px rgba(31, 29, 27, 0.28);
      z-index: 9998;
    }
    .bfq-panel {
      position: fixed;
      right: 20px;
      bottom: 96px;
      width: min(360px, calc(100vw - 24px));
      height: min(560px, calc(100vh - 140px));
      display: none;
      grid-template-rows: auto 1fr auto;
      background: #fffdf8;
      border: 1px solid rgba(46, 94, 78, 0.15);
      border-radius: 26px;
      overflow: hidden;
      box-shadow: 0 20px 60px rgba(31, 29, 27, 0.2);
      z-index: 9999;
    }
    .bfq-panel.is-open { display: grid; }
    .bfq-header {
      padding: 18px;
      background: linear-gradient(135deg, #1f1d1b, #2e5e4e);
      color: #fffdf8;
    }
    .bfq-header h3, .bfq-header p { margin: 0; }
    .bfq-header p { margin-top: 6px; font-size: 13px; opacity: 0.82; }
    .bfq-messages {
      padding: 16px;
      overflow-y: auto;
      background:
        radial-gradient(circle at top left, rgba(234, 217, 184, 0.45), transparent 24%),
        #fffdf8;
    }
    .bfq-message {
      max-width: 84%;
      margin-bottom: 12px;
      padding: 12px 14px;
      border-radius: 18px;
      line-height: 1.4;
      font: 14px/1.4 "Segoe UI", sans-serif;
    }
    .bfq-message.bot {
      background: #f3ecde;
      color: #1f1d1b;
      border-bottom-left-radius: 6px;
    }
    .bfq-message.user {
      margin-left: auto;
      background: #2e5e4e;
      color: #fffdf8;
      border-bottom-right-radius: 6px;
    }
    .bfq-quick-replies {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 8px 0 4px;
    }
    .bfq-chip {
      border: 0;
      border-radius: 999px;
      padding: 8px 12px;
      font-size: 13px;
      cursor: pointer;
      background: #ead9b8;
      color: #1f1d1b;
    }
    .bfq-footer {
      padding: 12px;
      border-top: 1px solid rgba(46, 94, 78, 0.1);
      background: #fff;
    }
    .bfq-form {
      display: flex;
      gap: 10px;
    }
    .bfq-input {
      flex: 1;
      border: 1px solid rgba(46, 94, 78, 0.18);
      border-radius: 999px;
      padding: 12px 14px;
      outline: none;
    }
    .bfq-send {
      border: 0;
      border-radius: 999px;
      padding: 12px 16px;
      background: #b45d3d;
      color: #fff;
      cursor: pointer;
    }
    .bfq-typing {
      display: inline-block;
      min-height: 18px;
      color: #6f6a63;
      font: 13px/1.4 "Segoe UI", sans-serif;
    }
  `;
  document.head.appendChild(style);

  const launcher = document.createElement("button");
  launcher.className = "bfq-launcher";
  launcher.type = "button";
  launcher.setAttribute("aria-label", "Open chat");
  launcher.textContent = "💬";

  const panel = document.createElement("section");
  panel.className = "bfq-panel";
  panel.innerHTML = `
    <header class="bfq-header">
      <h3>${config.title || "Maple & Thyme Bistro"}</h3>
      <p>${config.subtitle || "Restaurant support and lead capture"}</p>
    </header>
    <div class="bfq-messages" id="bfq-messages"></div>
    <footer class="bfq-footer">
      <div class="bfq-typing" id="bfq-typing"></div>
      <form class="bfq-form" id="bfq-form">
        <input class="bfq-input" id="bfq-input" type="text" placeholder="Ask about hours, menu, or bookings" maxlength="1000">
        <button class="bfq-send" type="submit">Send</button>
      </form>
    </footer>
  `;

  document.body.appendChild(launcher);
  document.body.appendChild(panel);

  const messagesEl = panel.querySelector("#bfq-messages");
  const typingEl = panel.querySelector("#bfq-typing");
  const formEl = panel.querySelector("#bfq-form");
  const inputEl = panel.querySelector("#bfq-input");

  function addMessage(text, sender) {
    const bubble = document.createElement("div");
    bubble.className = `bfq-message ${sender}`;
    bubble.textContent = text;
    messagesEl.appendChild(bubble);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function renderQuickReplies(replies) {
    if (!replies || !replies.length) {
      return;
    }
    const wrap = document.createElement("div");
    wrap.className = "bfq-quick-replies";
    replies.forEach((reply) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "bfq-chip";
      chip.textContent = reply;
      chip.addEventListener("click", function () {
        sendMessage(reply);
      });
      wrap.appendChild(chip);
    });
    messagesEl.appendChild(wrap);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  async function sendMessage(message) {
    const text = message.trim();
    if (!text) {
      return;
    }

    addMessage(text, "user");
    inputEl.value = "";
    typingEl.textContent = "Typing...";

    try {
      const response = await fetch(`${apiBaseUrl}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, message: text })
      });

      if (!response.ok) {
        throw new Error("Request failed");
      }

      const data = await response.json();
      typingEl.textContent = "";
      addMessage(data.message, "bot");
      renderQuickReplies(data.quick_replies);
    } catch (error) {
      typingEl.textContent = "";
      addMessage("The chat service is unavailable right now. Please try again shortly.", "bot");
    }
  }

  formEl.addEventListener("submit", function (event) {
    event.preventDefault();
    sendMessage(inputEl.value);
  });

  launcher.addEventListener("click", function () {
    panel.classList.toggle("is-open");
    if (panel.classList.contains("is-open") && !messagesEl.children.length) {
      addMessage("Hi, I’m BistroBot. Ask me about hours, reservations, menu options, or catering.", "bot");
      renderQuickReplies(["Hours", "Reservations", "Menu", "Catering"]);
    }
  });
})();
