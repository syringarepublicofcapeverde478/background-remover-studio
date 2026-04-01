const state = {
  files: [],
  selectedId: null,
  results: new Map(),
};

const fileInput = document.getElementById("fileInput");
const dropzone = document.getElementById("dropzone");
const queue = document.getElementById("queue");
const originalPreview = document.getElementById("originalPreview");
const resultPreview = document.getElementById("resultPreview");
const originalEmpty = document.getElementById("originalEmpty");
const resultEmpty = document.getElementById("resultEmpty");
const loadingOverlay = document.getElementById("loadingOverlay");
const resolutionText = document.getElementById("resolutionText");
const threshold = document.getElementById("threshold");
const thresholdValue = document.getElementById("thresholdValue");
const edgeCleanup = document.getElementById("edgeCleanup");
const edgeValue = document.getElementById("edgeValue");
const hairProtect = document.getElementById("hairProtect");
const exportFormat = document.getElementById("exportFormat");
const removeButton = document.getElementById("removeButton");
const downloadButton = document.getElementById("downloadButton");
const copyButton = document.getElementById("copyButton");

threshold.addEventListener("input", () => (thresholdValue.textContent = threshold.value));
edgeCleanup.addEventListener("input", () => (edgeValue.textContent = edgeCleanup.value));

dropzone.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", (event) => addFiles([...event.target.files]));

["dragenter", "dragover"].forEach((type) => {
  dropzone.addEventListener(type, (event) => {
    event.preventDefault();
    dropzone.classList.add("is-dragover");
  });
});
["dragleave", "drop"].forEach((type) => {
  dropzone.addEventListener(type, (event) => {
    event.preventDefault();
    dropzone.classList.remove("is-dragover");
  });
});
dropzone.addEventListener("drop", (event) => {
  addFiles([...event.dataTransfer.files].filter((file) => file.type.startsWith("image/")));
});

removeButton.addEventListener("click", removeBackground);
downloadButton.addEventListener("click", downloadResult);
copyButton.addEventListener("click", copyResult);

function addFiles(files) {
  files.forEach((file) => {
    if (!file.type.startsWith("image/")) return;
    const id = `${file.name}-${file.lastModified}-${Math.random().toString(36).slice(2)}`;
    state.files.push({
      id,
      file,
      name: file.name,
      url: URL.createObjectURL(file),
    });
  });
  if (!state.selectedId && state.files.length) {
    state.selectedId = state.files[0].id;
  }
  renderQueue();
  syncPreview();
}

function getSelectedItem() {
  return state.files.find((item) => item.id === state.selectedId) || null;
}

function renderQueue() {
  queue.innerHTML = "";
  if (!state.files.length) {
    queue.innerHTML = `<div class="empty-state">No images yet</div>`;
    return;
  }

  state.files.forEach((item) => {
    const row = document.createElement("button");
    row.type = "button";
    row.className = `queue-item ${item.id === state.selectedId ? "is-active" : ""}`;
    row.innerHTML = `
      <img src="${item.url}" alt="" />
      <div>
        <div class="queue-name" title="${item.name}">${item.name}</div>
        <div class="queue-status">${state.results.has(item.id) ? "Processed" : "Ready"}</div>
      </div>
    `;
    row.addEventListener("click", () => {
      state.selectedId = item.id;
      renderQueue();
      syncPreview();
    });
    queue.appendChild(row);
  });
}

function syncPreview() {
  const selected = getSelectedItem();
  if (!selected) {
    originalPreview.classList.remove("is-visible");
    resultPreview.classList.remove("is-visible");
    originalEmpty.classList.remove("hidden");
    resultEmpty.classList.remove("hidden");
    resolutionText.textContent = "No image selected";
    downloadButton.disabled = true;
    copyButton.disabled = true;
    return;
  }

  originalPreview.src = selected.url;
  originalPreview.classList.add("is-visible");
  originalEmpty.classList.add("hidden");

  const result = state.results.get(selected.id);
  if (result) {
    resultPreview.src = result.url;
    resultPreview.classList.add("is-visible");
    resultEmpty.classList.add("hidden");
    downloadButton.disabled = false;
    copyButton.disabled = false;
    resolutionText.textContent = `${result.width} × ${result.height}px`;
  } else {
    resultPreview.classList.remove("is-visible");
    resultPreview.removeAttribute("src");
    resultEmpty.classList.remove("hidden");
    resolutionText.textContent = "Original loaded";
    downloadButton.disabled = true;
    copyButton.disabled = true;
  }
}

async function removeBackground() {
  const selected = getSelectedItem();
  if (!selected) return;

  loadingOverlay.classList.remove("hidden");
  removeButton.disabled = true;

  const body = new FormData();
  body.append("file", selected.file);
  body.append("white_threshold", threshold.value);
  body.append("edge_cleanup", edgeCleanup.value);
  body.append("hair_protect", hairProtect.checked ? "true" : "false");
  body.append("output", exportFormat.value);

  try {
    const response = await fetch("/api/remove-background", { method: "POST", body });
    if (!response.ok) {
      throw new Error("Failed to process image.");
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const width = response.headers.get("X-Image-Width") || "-";
    const height = response.headers.get("X-Image-Height") || "-";
    state.results.set(selected.id, {
      blob,
      url,
      width,
      height,
      ext: exportFormat.value,
      filename: selected.name.replace(/\.[^.]+$/, "") + `_transparent.${exportFormat.value}`,
    });
    renderQueue();
    syncPreview();
  } catch (error) {
    alert(error.message || "Unable to remove the background right now.");
  } finally {
    loadingOverlay.classList.add("hidden");
    removeButton.disabled = false;
  }
}

function downloadResult() {
  const selected = getSelectedItem();
  const result = selected ? state.results.get(selected.id) : null;
  if (!result) return;
  const link = document.createElement("a");
  link.href = result.url;
  link.download = result.filename;
  link.click();
}

async function copyResult() {
  const selected = getSelectedItem();
  const result = selected ? state.results.get(selected.id) : null;
  if (!result || !navigator.clipboard || !window.ClipboardItem) return;
  try {
    await navigator.clipboard.write([
      new ClipboardItem({ [result.blob.type]: result.blob }),
    ]);
  } catch {
    alert("Clipboard copy is not available in this browser.");
  }
}
