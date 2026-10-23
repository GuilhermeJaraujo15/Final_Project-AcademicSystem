(() => {
  const toast = document.getElementById("toast");
  let toastTimer;
  function notify(message) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.remove("hidden");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.add("hidden"), 3600);
  }

  const roleSelect = document.getElementById("demo-role");
  roleSelect?.addEventListener("change", () => {
    const url = new URL(window.location.href);
    url.searchParams.set("role", roleSelect.value);
    window.location.assign(url);
  });

  const menuButton = document.getElementById("mobile-menu-button");
  const sidebar = document.getElementById("sidebar");
  menuButton?.addEventListener("click", () => {
    const isOpen = !sidebar.classList.contains("hidden");
    sidebar.classList.toggle("hidden", isOpen);
    menuButton.setAttribute("aria-expanded", String(!isOpen));
    menuButton.setAttribute("aria-label", isOpen ? "Abrir navegação" : "Fechar navegação");
  });

  document.addEventListener("click", (event) => {
    const openButton = event.target.closest("[data-modal]");
    if (openButton) document.getElementById(openButton.dataset.modal)?.showModal();
    if (event.target.closest("[data-close-modal]")) event.target.closest("dialog")?.close();
    const toastButton = event.target.closest("[data-toast]");
    if (toastButton) notify(toastButton.dataset.toast);
  });

  document.querySelectorAll("dialog").forEach((dialog) => {
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) dialog.close();
    });
  });
  document.getElementById("demo-form")?.addEventListener("submit", (event) => {
    event.preventDefault();
    event.currentTarget.reset();
    event.currentTarget.closest("dialog")?.close();
    notify("Campos v?lidos. Modo de demonstração: nada foi salvo.");
  });
  document.getElementById("report-demo-form")?.addEventListener("submit", (event) => event.preventDefault());

  const rows = [...document.querySelectorAll(".demo-row")];
  const search = document.getElementById("table-search");
  const status = document.getElementById("status-filter");
  const indicator = document.getElementById("page-indicator");
  const visibleCount = document.getElementById("visible-count");
  const noResults = document.getElementById("no-results");
  const pageSize = 5;
  let page = 0;
  let filtered = rows;
  function updateTable() {
    const query = (search?.value || "").trim().toLocaleLowerCase("pt-BR");
    const selectedStatus = status?.value || "";
    filtered = rows.filter((row) => row.textContent.toLocaleLowerCase("pt-BR").includes(query) && (!selectedStatus || row.dataset.status === selectedStatus));
    const pageCount = Math.max(1, Math.ceil(filtered.length / pageSize));
    page = Math.min(page, pageCount - 1);
    rows.forEach((row) => { row.hidden = true; });
    filtered.slice(page * pageSize, (page + 1) * pageSize).forEach((row) => { row.hidden = false; });
    if (indicator) indicator.textContent = `${page + 1} / ${pageCount}`;
    if (visibleCount) visibleCount.textContent = String(filtered.length);
    if (noResults) noResults.classList.toggle("hidden", filtered.length > 0);
    const prev = document.getElementById("prev-page");
    const next = document.getElementById("next-page");
    if (prev) prev.disabled = page <= 0;
    if (next) next.disabled = page >= pageCount - 1;
  }
  search?.addEventListener("input", () => { page = 0; updateTable(); });
  status?.addEventListener("change", () => { page = 0; updateTable(); });
  document.getElementById("prev-page")?.addEventListener("click", () => { page = Math.max(0, page - 1); updateTable(); });
  document.getElementById("next-page")?.addEventListener("click", () => { page += 1; updateTable(); });
  if (rows.length) updateTable();
})();
