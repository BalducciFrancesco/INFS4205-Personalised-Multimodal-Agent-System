const conversationEl = document.getElementById("conversation");
const chatForm = document.getElementById("chat-form");
const messageEl = document.getElementById("message");
const imageInput = document.getElementById("image-input");
const attachButton = document.getElementById("attach-button");
const userIdSelect = document.getElementById("user-id");
const sendButton = document.getElementById("send-button");

let pendingNoticeEl = null;
let attachedImage = "";
let currentThreadId = "";

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function appendBubble(classNames, html, side) {
  const article = document.createElement("article");
  article.className = classNames;
  article.innerHTML = html;

  if (!side) {
    conversationEl.appendChild(article);
    conversationEl.scrollTop = conversationEl.scrollHeight;
    return article;
  }

  const row = document.createElement("div");
  row.className = side === "user" ? "msg-row msg-row-user" : "msg-row msg-row-assistant";

  const avatar = document.createElement("span");
  avatar.className = "msg-avatar";
  avatar.setAttribute("aria-hidden", "true");
  avatar.textContent = side === "user" ? "👤" : "🪨";

  if (side === "user") row.append(article, avatar);
  else row.append(avatar, article);

  conversationEl.appendChild(row);
  conversationEl.scrollTop = conversationEl.scrollHeight;
  return row;
}

function fitMessageHeight() {
  messageEl.style.height = "auto";
  const scrollHeight = messageEl.scrollHeight;
  messageEl.style.height = Math.min(scrollHeight, 192) + "px";
}

function syncAttachUi() {
  const has = Boolean(attachedImage);
  attachButton.classList.toggle("has-image", has);
  attachButton.setAttribute(
    "aria-label",
    has ? "Remove attached image" : "Attach image",
  );
  attachButton.title = has ? "Remove image" : "Attach image";
}

function clearAttachment() {
  attachedImage = "";
  imageInput.value = "";
  syncAttachUi();
}

attachButton.addEventListener("click", () => {
  if (attachedImage) {
    clearAttachment();
    return;
  }
  imageInput.click();
});

imageInput.addEventListener("change", () => {
  const file = imageInput.files?.[0];
  if (file) {
    attachedImage = URL.createObjectURL(file);
    syncAttachUi();
  }
});

appendBubble(
  "bubble bubble-assistant",
  "How can I help you today?",
  "assistant",
);

messageEl.addEventListener("input", fitMessageHeight);
fitMessageHeight();

messageEl.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    chatForm.requestSubmit();
  }
});

fetch("/api/users")
  .then((response) => (response.ok ? response.json() : []))
  .then((ids) => {
    const list = ids.length ? ids : [25];
    userIdSelect.innerHTML = list
      .map(
        (id, index) =>
          `<option value="${id}"${index === 0 ? " selected" : ""}>${id}</option>`,
      )
      .join("");
    userIdSelect.disabled = false;
  })

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = messageEl.value.trim();

  if (!text || sendButton.disabled) return;

  sendButton.disabled = true;
  messageEl.value = "";
  pendingNoticeEl?.remove();

  try {
    const userBubbleHtml = attachedImage
      ? escapeHtml(text) + `<img src="${attachedImage}" style="border-radius: 0.4rem;" alt="Attached image">`
      : escapeHtml(text);
    appendBubble("bubble bubble-user", userBubbleHtml, "user");
    pendingNoticeEl = appendBubble(
      "bubble bubble-assistant bubble-assistant-notice",
      escapeHtml("Rock is thinking (???) …"),
      "assistant",
    );

    const formData = new FormData();
    formData.append("thread_id", currentThreadId);
    formData.append("user_id", userIdSelect.value);
    formData.append("message", text);
    if (imageInput.files[0]) {
      formData.append("image", imageInput.files[0]);
    }

    const response = await fetch("/api/chat", {
      method: "POST",
      body: formData
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Error");

    // Persist thread id returned by BE for subsequent requests.
    if (typeof data.thread_id === "string" && data.thread_id.length > 0) {
      currentThreadId = data.thread_id;
    }

    pendingNoticeEl.remove();
    pendingNoticeEl = null;
    appendBubble(
      "bubble bubble-assistant",
      `<div class="reply">${data.html_response}</div>`,
      "assistant",
    );
    clearAttachment();
    fitMessageHeight();
  } catch (error) {
    pendingNoticeEl?.remove();
    pendingNoticeEl = null;
    appendBubble(
      "bubble bubble-assistant bubble-assistant-notice",
      escapeHtml(error.message || "Failed"),
      "assistant",
    );
  } finally {
    sendButton.disabled = false;
  }
});
