const rowsElement = document.querySelector("#comparisonRows");
const searchInput = document.querySelector("#comparisonSearch");
const familySelect = document.querySelector("#comparisonFamily");
const statusSelect = document.querySelector("#comparisonStatus");
const countElement = document.querySelector("#comparisonCount");

const state = {
  rows: [],
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function normalizeStatus(status) {
  return String(status || "planned").toLowerCase();
}

function isOptimal(entry) {
  const text = `${entry.notes} ${entry.name}`.toLowerCase();
  return text.includes("optimal") || text.includes("shortest") || text.includes("dijkstra") || text.includes("a*");
}

function isWeighted(entry) {
  const text = `${entry.family} ${entry.notes} ${entry.name}`.toLowerCase();
  return text.includes("weighted") || text.includes("cost") || text.includes("dijkstra") || text.includes("uniform-cost");
}

function complexityBucket(entry) {
  const time = entry.time || "";
  if (time.includes("Unbounded")) return "Unbounded / stochastic";
  if (time.includes("log")) return "Log-priority";
  if (time.includes("VE") || time.includes("V^3") || time.includes("V(E")) return "Polynomial heavy";
  if (time.includes("b^") || time.includes("K")) return "Depth / enumeration";
  if (time.includes("V + E") || time.includes("O(k)")) return "Linear traversal";
  return "Specialized bound";
}

function countBy(items, getKey) {
  return items.reduce((counts, item) => {
    const key = getKey(item);
    counts.set(key, (counts.get(key) || 0) + 1);
    return counts;
  }, new Map());
}

function renderBreakdown(elementId, counts) {
  const element = document.querySelector(elementId);
  element.innerHTML = [...counts.entries()]
    .sort((left, right) => right[1] - left[1] || left[0].localeCompare(right[0]))
    .slice(0, 12)
    .map(([label, count]) => `<div><span>${escapeHtml(label)}</span><strong>${count}</strong></div>`)
    .join("");
}

function renderStats() {
  const implemented = state.rows.filter((entry) => normalizeStatus(entry.status) === "implemented").length;
  const backlog = state.rows.filter((entry) => normalizeStatus(entry.status) === "backlog").length;
  const families = new Set(state.rows.map((entry) => entry.family)).size;
  const optimal = state.rows.filter(isOptimal).length;
  const weighted = state.rows.filter(isWeighted).length;
  document.querySelector("#statTotal").textContent = state.rows.length;
  document.querySelector("#statImplemented").textContent = implemented;
  document.querySelector("#statBacklog").textContent = backlog;
  document.querySelector("#statFamilies").textContent = families;
  document.querySelector("#statOptimal").textContent = optimal;
  document.querySelector("#statWeighted").textContent = weighted;
  renderBreakdown("#statusBreakdown", countBy(state.rows, (entry) => normalizeStatus(entry.status)));
  renderBreakdown("#familyBreakdown", countBy(state.rows, (entry) => entry.family));
  renderBreakdown("#complexityBreakdown", countBy(state.rows, complexityBucket));
}

function renderFamilyOptions() {
  const families = [...new Set(state.rows.map((entry) => entry.family))].sort((a, b) => a.localeCompare(b));
  familySelect.innerHTML = '<option value="all">All families</option>';
  for (const family of families) {
    const option = document.createElement("option");
    option.value = family;
    option.textContent = family;
    familySelect.append(option);
  }
}

function filteredRows() {
  const query = searchInput.value.trim().toLowerCase();
  const family = familySelect.value;
  const status = statusSelect.value;
  return state.rows.filter((entry) => {
    const haystack = `${entry.name} ${entry.family} ${entry.status} ${entry.time} ${entry.space} ${entry.notes} ${entry.reference}`.toLowerCase();
    return (!query || haystack.includes(query)) && (family === "all" || entry.family === family) && (status === "all" || normalizeStatus(entry.status) === status);
  });
}

function renderRows() {
  const rows = filteredRows();
  countElement.textContent = `${rows.length}/${state.rows.length} shown`;
  rowsElement.innerHTML = rows
    .map(
      (entry) => `
        <tr>
          <td data-label="Algorithm"><strong>${escapeHtml(entry.name)}</strong></td>
          <td data-label="Family">${escapeHtml(entry.family)}</td>
          <td data-label="State"><span class="status-pill ${escapeHtml(normalizeStatus(entry.status))}">${escapeHtml(entry.status)}</span></td>
          <td data-label="Time">${escapeHtml(entry.time)}</td>
          <td data-label="Space">${escapeHtml(entry.space)}</td>
          <td data-label="Guarantee / Notes">${escapeHtml(entry.notes)}</td>
          <td data-label="Reference">${escapeHtml(entry.reference)}</td>
        </tr>
      `,
    )
    .join("");
}

async function loadCatalog() {
  const [catalogResponse, backlogResponse] = await Promise.all([
    fetch("./algorithm_catalog.json", { cache: "no-store" }),
    fetch("./known_2d_backlog.json", { cache: "no-store" }),
  ]);
  const catalog = await catalogResponse.json();
  const backlog = await backlogResponse.json();
  const unique = new Map();
  for (const entry of [...catalog, ...backlog]) {
    unique.set(entry.name, entry);
  }
  state.rows = [...unique.values()].sort((left, right) => {
    const statusOrder = { implemented: 0, planned: 1, backlog: 2 };
    return (
      (statusOrder[normalizeStatus(left.status)] ?? 9) - (statusOrder[normalizeStatus(right.status)] ?? 9) ||
      left.family.localeCompare(right.family) ||
      left.name.localeCompare(right.name)
    );
  });
  renderStats();
  renderFamilyOptions();
  renderRows();
}

for (const control of [searchInput, familySelect, statusSelect]) {
  control.addEventListener("input", renderRows);
  control.addEventListener("change", renderRows);
}

await loadCatalog();
