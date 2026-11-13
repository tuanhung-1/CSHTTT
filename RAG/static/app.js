const $ = (selector) => document.querySelector(selector);
const docsEl = $('#document-list');
const countEl = $('#doc-count');
const uploadMessage = $('#upload-message');
const fileInput = $('#file-input');
const dropZone = $('#drop-zone');
const conversation = $('#conversation');
const composerWrap = $('.composer-wrap');
const questionInput = $('#question');
const sendButton = $('#send-button');
const history = [];
let sending = false;

function updateComposerSpace() {
  document.documentElement.style.setProperty('--composer-space', `${Math.ceil(composerWrap.getBoundingClientRect().height) + 20}px`);
}

function scrollToLatest() {
  requestAnimationFrame(() => {
    window.scrollTo({ top: document.documentElement.scrollHeight - window.innerHeight, behavior: 'smooth' });
  });
}

async function api(url, options = {}) {
  const response = await fetch(url, options);
  let data;
  try { data = await response.json(); } catch { throw new Error('Máy chủ trả về dữ liệu không hợp lệ.'); }
  if (!response.ok) throw new Error(data.error || 'Yêu cầu không thành công.');
  return data;
}

function node(tag, className = '', text = '') {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text) element.textContent = text;
  return element;
}

function showUploadMessage(text, error = false) {
  uploadMessage.textContent = text;
  uploadMessage.classList.toggle('error', error);
}

function sourceUrl(source) {
  const page = /^\d+$/.test(source.page || '') ? `#page=${source.page}` : '';
  return `/api/documents/${encodeURIComponent(source.document_id)}/file${page}`;
}

function renderDocuments(documents) {
  docsEl.replaceChildren();
  countEl.textContent = String(documents.length);
  if (!documents.length) {
    docsEl.append(node('div', 'empty-documents', 'Chưa có tài liệu. Tải một tệp lên để bắt đầu.'));
    return;
  }
  const statusLabel = { ready: 'Sẵn sàng', pending: 'Đang chờ', processing: 'Đang tạo chỉ mục', failed: 'Không thể xử lý' };
  for (const documentItem of documents) {
    const row = node('div', 'document');
    const icon = node('div', 'file-icon', documentItem.filename.split('.').pop().slice(0, 4).toUpperCase());
    const info = node('div', 'document-info');
    const name = node(documentItem.status === 'ready' ? 'a' : 'span', 'document-name', documentItem.filename);
    if (name.tagName === 'A') {
      name.href = sourceUrl({ document_id: documentItem.id, page: '' });
      name.target = '_blank';
      name.rel = 'noopener noreferrer';
    }
    name.title = documentItem.filename;
    info.append(name, node('span', 'document-meta', `${(documentItem.size_bytes / 1024).toFixed(1)} KB · ${documentItem.chunk_count} đoạn`));
    const visibleStatus = documentItem.needs_reindex ? 'Cần lập lại chỉ mục' : (statusLabel[documentItem.status] || documentItem.status);
    info.append(node('span', `doc-status ${documentItem.needs_reindex ? 'pending' : documentItem.status}`, visibleStatus));
    if (documentItem.status === 'failed' && documentItem.error) info.append(node('span', 'doc-error', documentItem.error));
    if (documentItem.status === 'failed' || documentItem.needs_reindex) {
      const reindex = node('button', 'reindex-doc', 'Lập lại chỉ mục');
      reindex.type = 'button';
      reindex.addEventListener('click', async () => {
        try {
          await api(`/api/documents/${encodeURIComponent(documentItem.id)}/reindex`, { method: 'POST', body: '' });
          showUploadMessage(`Đang lập lại chỉ mục ${documentItem.filename}…`);
          await refreshDocuments();
        } catch (error) { showUploadMessage(error.message, true); }
      });
      info.append(reindex);
    }
    const remove = node('button', 'delete-doc', '×');
    remove.type = 'button';
    remove.title = `Xóa ${documentItem.filename}`;
    remove.setAttribute('aria-label', remove.title);
    remove.addEventListener('click', async () => {
      if (!confirm(`Xóa tài liệu “${documentItem.filename}” khỏi thư viện?`)) return;
      try {
        await api(`/api/documents/${encodeURIComponent(documentItem.id)}`, { method: 'DELETE' });
        await refreshDocuments();
      } catch (error) { showUploadMessage(error.message, true); }
    });
    row.append(icon, info, remove);
    docsEl.append(row);
  }
}

async function refreshDocuments() {
  try {
    const data = await api('/api/documents');
    renderDocuments(data.documents);
  } catch (error) { showUploadMessage(error.message, true); }
}

async function refreshStatus() {
  const pill = $('#model-status');
  const banner = $('#setup-banner');
  try {
    const status = await api('/api/status');
    pill.classList.toggle('offline', !status.configured);
    pill.querySelector('span:last-child').textContent = status.configured ? 'Gemini đã cấu hình' : 'Thiếu Gemini API key';
    if (!status.configured) {
      banner.textContent = 'Chưa có GEMINI_API_KEY. Đặt biến môi trường theo README rồi khởi động lại máy chủ.';
      banner.hidden = false;
    } else {
      banner.hidden = true;
    }
  } catch {
    pill.classList.add('offline');
    pill.querySelector('span:last-child').textContent = 'Máy chủ chưa sẵn sàng';
    banner.textContent = 'Không kiểm tra được trạng thái máy chủ.';
    banner.hidden = false;
  }
}

async function uploadFiles(files) {
  for (const file of files) {
    showUploadMessage(`Đang tải ${file.name}…`);
    try {
      const result = await api(`/api/documents?filename=${encodeURIComponent(file.name)}`, {
        method: 'POST', headers: { 'Content-Type': 'application/octet-stream' }, body: file,
      });
      showUploadMessage(`Đã nhận ${result.document.filename}. Đang tạo chỉ mục…`);
      await refreshDocuments();
    } catch (error) { showUploadMessage(`${file.name}: ${error.message}`, true); }
  }
  fileInput.value = '';
}

function addMessage(role, text, sources = [], isError = false) {
  $('#welcome')?.remove();
  const wrapper = node('div', `message ${role}${isError ? ' error' : ''}`);
  const content = node('div', 'message-content');
  if (role === 'assistant') {
    wrapper.append(node('div', 'message-avatar', '✳'));
    content.append(node('div', 'message-label', 'TRỢ LÝ TÀI LIỆU'));
  }
  content.append(node('div', 'message-body', text));
  if (sources.length) {
    content.append(node('div', 'source-heading', 'Nguồn được trích dẫn'));
    const list = node('div', 'source-list');
    for (const source of sources) {
      const link = node('a', 'source-card');
      link.href = sourceUrl(source);
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      link.append(node('div', 'source-title', `[${source.number}] ${source.filename}${source.page ? ` · Trang ${source.page}` : ''}`));
      link.append(node('div', 'source-excerpt', source.content));
      list.append(link);
    }
    content.append(list);
  }
  wrapper.append(content);
  conversation.append(wrapper);
  scrollToLatest();
  return wrapper;
}

function addTyping() {
  const wrapper = node('div', 'message assistant');
  wrapper.append(node('div', 'message-avatar', '✳'));
  const content = node('div', 'message-content');
  content.append(node('div', 'message-label', 'ĐANG TÌM TRONG TÀI LIỆU'));
  const dots = node('div', 'typing');
  dots.append(node('span'), node('span'), node('span'));
  content.append(dots);
  wrapper.append(content);
  conversation.append(wrapper);
  scrollToLatest();
  return wrapper;
}

async function sendQuestion() {
  const question = questionInput.value.trim();
  if (!question || sending) return;
  sending = true;
  sendButton.disabled = true;
  questionInput.value = '';
  questionInput.style.height = '';
  const userMessage = addMessage('user', question);
  const typing = addTyping();
  try {
    const result = await api('/api/chat', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, history: history.slice(-6) }),
    });
    typing.remove();
    addMessage('assistant', result.answer, result.sources || []);
    history.push({ role: 'user', content: question }, { role: 'assistant', content: result.answer });
  } catch (error) {
    typing.remove();
    userMessage.remove();
    if (!questionInput.value.trim()) {
      questionInput.value = question;
      questionInput.dispatchEvent(new Event('input'));
    }
    addMessage('assistant', error.message, [], true);
  } finally {
    sending = false;
    sendButton.disabled = false;
    questionInput.focus();
  }
}

$('#chat-form').addEventListener('submit', (event) => { event.preventDefault(); sendQuestion(); });
questionInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    sendQuestion();
  }
});
questionInput.addEventListener('input', () => {
  questionInput.style.height = 'auto';
  questionInput.style.height = `${Math.min(questionInput.scrollHeight, 130)}px`;
  updateComposerSpace();
});
fileInput.addEventListener('change', () => uploadFiles(fileInput.files));
for (const eventName of ['dragenter', 'dragover']) {
  dropZone.addEventListener(eventName, (event) => { event.preventDefault(); dropZone.classList.add('dragging'); });
}
for (const eventName of ['dragleave', 'drop']) {
  dropZone.addEventListener(eventName, (event) => { event.preventDefault(); dropZone.classList.remove('dragging'); });
}
dropZone.addEventListener('drop', (event) => uploadFiles(event.dataTransfer.files));
document.querySelectorAll('.suggestion').forEach((button) => {
  button.addEventListener('click', () => { questionInput.value = button.dataset.question; sendQuestion(); });
});

refreshStatus();
refreshDocuments();
updateComposerSpace();
if ('ResizeObserver' in window) new ResizeObserver(updateComposerSpace).observe(composerWrap);
setInterval(refreshDocuments, 3000);
setInterval(refreshStatus, 15000);
