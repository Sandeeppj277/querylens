/**
 * QueryLens — Frontend Core Logic
 * Handles API calls, dynamic chart rendering, table generation, and schema exploration.
 */

const API_BASE = '/api';
let activeChart = null;
let currentChartData = null;

document.addEventListener('DOMContentLoaded', () => {
  fetchHistory();
  fetchSchema();
});

// ── Tab Switching ──────────────────────────────────────────
function switchSidebarTab(tabName) {
  const historyBtn = document.getElementById('tabHistoryBtn');
  const schemaBtn = document.getElementById('tabSchemaBtn');
  const historyTab = document.getElementById('historyTab');
  const schemaTab = document.getElementById('schemaTab');

  if (tabName === 'history') {
    historyBtn.classList.add('active');
    schemaBtn.classList.remove('active');
    historyTab.classList.remove('hidden');
    schemaTab.classList.add('hidden');
  } else {
    schemaBtn.classList.add('active');
    historyBtn.classList.remove('active');
    schemaTab.classList.remove('hidden');
    historyTab.classList.add('hidden');
  }
}

// ── Suggestions ────────────────────────────────────────────
function useSuggestion(buttonElement) {
  const input = document.getElementById('questionInput');
  input.value = buttonElement.innerText.trim();
  input.focus();
}

// ── Main Query Pipeline ────────────────────────────────────
async function handleQuerySubmit(event) {
  event.preventDefault();
  const input = document.getElementById('questionInput');
  const question = input.value.trim();
  if (!question) return;

  setLoading(true);

  try {
    const res = await fetch(`${API_BASE}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to process query');
    }

    const data = await res.json();
    renderResults(data);
    fetchHistory(); // refresh recent history list
  } catch (error) {
    alert(`Error: ${error.message}`);
  } finally {
    setLoading(false);
  }
}

// ── Render Query Results ───────────────────────────────────
function renderResults(data) {
  const resultsArea = document.getElementById('resultsArea');
  resultsArea.classList.remove('hidden');

  // 1. Summary
  document.getElementById('summaryText').innerText = data.summary;
  document.getElementById('executionTimestamp').innerText = new Date(data.timestamp).toLocaleTimeString();

  // 2. SQL & Explanation
  const formattedSql = formatSQL(data.sql);
  const sqlEl = document.getElementById('sqlDisplay');
  sqlEl.textContent = formattedSql;
  if (window.hljs) {
    hljs.highlightElement(sqlEl);
  }
  document.getElementById('sqlExplanation').innerText = data.explanation;

  // 3. Table
  renderTable(data.columns, data.rows);
  document.getElementById('rowCountBadge').innerText = `${data.row_count} rows`;

  // 4. Chart Visualization
  currentChartData = data;
  const initialType = (['bar', 'line', 'pie'].includes(data.chart_type)) ? data.chart_type : 'bar';
  renderChart(initialType);

  // Scroll smoothly to results
  resultsArea.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ── Table Rendering ────────────────────────────────────────
function renderTable(columns, rows) {
  const thead = document.getElementById('tableHead');
  const tbody = document.getElementById('tableBody');

  thead.innerHTML = '';
  tbody.innerHTML = '';

  if (!columns || columns.length === 0) {
    tbody.innerHTML = '<tr><td colspan="100%">No data returned.</td></tr>';
    return;
  }

  // Headers
  const headerRow = document.createElement('tr');
  columns.forEach(col => {
    const th = document.createElement('th');
    th.innerText = col;
    headerRow.appendChild(th);
  });
  thead.appendChild(headerRow);

  // Rows
  rows.forEach(row => {
    const tr = document.createElement('tr');
    row.forEach(cell => {
      const td = document.createElement('td');
      td.innerText = (cell !== null && cell !== undefined) ? cell : 'NULL';
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
}

// ── Chart Rendering ────────────────────────────────────────
function renderChart(chartType = 'bar') {
  if (!currentChartData || !currentChartData.columns || currentChartData.rows.length === 0) {
    document.getElementById('chartContainer').classList.add('hidden');
    return;
  }

  document.getElementById('chartContainer').classList.remove('hidden');
  const canvas = document.getElementById('resultChart');
  const ctx = canvas.getContext('2d');

  if (activeChart) {
    activeChart.destroy();
  }

  // Update active pill button
  document.querySelectorAll('.chart-type-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-type') === chartType);
  });

  const columns = currentChartData.columns;
  const rows = currentChartData.rows;

  // Determine label column & numeric values column
  let labelIdx = 0;
  let valueIdx = 1;

  // If there's more than 1 column, find the first numeric column for values
  if (columns.length > 1) {
    for (let i = 1; i < columns.length; i++) {
      if (typeof rows[0][i] === 'number') {
        valueIdx = i;
        break;
      }
    }
  }

  const labels = rows.map(r => String(r[labelIdx] || ''));
  const values = rows.map(r => Number(r[valueIdx]) || 0);

  const colors = [
    '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b',
    '#ec4899', '#3b82f6', '#14b8a6', '#f43f5e'
  ];

  activeChart = new Chart(ctx, {
    type: chartType,
    data: {
      labels: labels,
      datasets: [{
        label: columns[valueIdx] || 'Value',
        data: values,
        backgroundColor: chartType === 'pie' ? colors : 'rgba(139, 92, 246, 0.65)',
        borderColor: chartType === 'pie' ? 'rgba(255, 255, 255, 0.15)' : '#a855f7',
        borderWidth: 2,
        borderRadius: chartType === 'bar' ? 8 : 0,
        fill: chartType === 'line' ? true : false,
        tension: 0.35,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: chartType === 'pie',
          labels: { color: '#cbd5e1', font: { family: 'Plus Jakarta Sans', size: 11 } }
        },
        tooltip: {
          backgroundColor: 'rgba(15, 23, 42, 0.9)',
          titleFont: { family: 'Plus Jakarta Sans', size: 12 },
          bodyFont: { family: 'Plus Jakarta Sans', size: 12 },
          borderColor: 'rgba(255, 255, 255, 0.1)',
          borderWidth: 1,
          padding: 10,
        }
      },
      scales: chartType === 'pie' ? {} : {
        x: {
          ticks: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', size: 11 } },
          grid: { color: 'rgba(255, 255, 255, 0.04)' }
        },
        y: {
          ticks: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', size: 11 } },
          grid: { color: 'rgba(255, 255, 255, 0.05)' }
        }
      }
    }
  });
}

function switchChartType(type) {
  renderChart(type);
}

// ── SQL Formatter ──────────────────────────────────────────
function formatSQL(sql) {
  if (!sql) return '';

  // If the query already has multiple distinct lines, normalize whitespace
  let clean = sql.trim().replace(/\r\n/g, '\n');

  // Major SQL keywords that should always start on their own fresh line
  const majorKeywords = [
    'SELECT', 'FROM', 'WHERE', 'GROUP BY', 'HAVING',
    'ORDER BY', 'LIMIT', 'OFFSET', 'UNION ALL', 'UNION',
    'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'CROSS JOIN', 'JOIN'
  ];

  // If it's flattened into a single line or poorly formatted, break it cleanly
  if (!clean.includes('\n') || clean.split('\n').length <= 2) {
    // Break before each major keyword
    majorKeywords.forEach(kw => {
      const regex = new RegExp(`\\s+(${kw})\\b`, 'gi');
      clean = clean.replace(regex, '\n$1');
    });

    // Indent columns under SELECT
    clean = clean.replace(/(SELECT\s+)([\s\S]*?)(\nFROM\b)/i, (match, sel, cols, from) => {
      // Split individual columns by commas that are not inside parentheses
      const colList = cols.split(/,(?![^(]*\))/).map(c => '    ' + c.trim()).join(',\n');
      return `${sel.trim()}\n${colList}\n${from.trim()}`;
    });

    // Indent JOIN clauses
    clean = clean.replace(/\n(INNER JOIN|LEFT JOIN|RIGHT JOIN|CROSS JOIN|JOIN)\b/gi, '\n  $1');

    // Indent AND / OR under WHERE / HAVING
    clean = clean.replace(/\s+(AND|OR)\s+/gi, '\n    $1 ');
  }

  return clean;
}

// ── Copy SQL ───────────────────────────────────────────────
function copySql() {
  const sqlText = document.getElementById('sqlDisplay').innerText;
  navigator.clipboard.writeText(sqlText).then(() => {
    const btn = document.getElementById('copySqlBtn');
    btn.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
    setTimeout(() => {
      btn.innerHTML = '<i class="fa-regular fa-copy"></i> Copy SQL';
    }, 2000);
  });
}

// ── CSV Export ─────────────────────────────────────────────
function exportTableToCSV() {
  if (!currentChartData) return;
  const cols = currentChartData.columns;
  const rows = currentChartData.rows;

  let csv = cols.map(c => `"${c}"`).join(',') + '\n';
  rows.forEach(row => {
    csv += row.map(val => `"${val}"`).join(',') + '\n';
  });

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `querylens_export_${Date.now()}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

// ── History & Schema Fetch ─────────────────────────────────
async function fetchHistory() {
  try {
    const res = await fetch(`${API_BASE}/history`);
    if (!res.ok) return;
    const history = await res.json();
    const list = document.getElementById('historyList');

    if (history.length === 0) {
      list.innerHTML = '<div class="empty-state">No queries executed yet</div>';
      return;
    }

    list.innerHTML = '';
    history.forEach(item => {
      const div = document.createElement('div');
      div.className = 'history-item';
      div.onclick = () => {
        document.getElementById('questionInput').value = item.question;
        handleQuerySubmit({ preventDefault: () => {} });
      };
      div.innerHTML = `
        <div class="history-item-question">${escapeHtml(item.question)}</div>
        <div class="history-item-meta">
          <span>${item.row_count} rows</span>
          <span>${new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
        </div>
      `;
      list.appendChild(div);
    });
  } catch (err) {
    console.error('History fetch failed:', err);
  }
}

async function fetchSchema() {
  try {
    const res = await fetch(`${API_BASE}/schema`);
    if (!res.ok) return;
    const data = await res.json();
    const schemaSql = data.schema_sql;

    document.getElementById('modalSchemaContent').innerText = schemaSql;

    // Parse table names and columns robustly
    const explorer = document.getElementById('schemaExplorer');
    explorer.innerHTML = '';

    // Match CREATE TABLE <name> ( ... );
    const tableRegex = /CREATE TABLE\s+([a-zA-Z0-9_]+)\s*\(([\s\S]*?)\);/gi;
    let match;
    let count = 0;

    while ((match = tableRegex.exec(schemaSql)) !== null) {
      count++;
      const tableName = match[1];
      const rawBody = match[2];
      const colLines = rawBody
        .split('\n')
        .map(l => l.trim().replace(/,$/, ''))
        .filter(l => l.length > 0 && !l.toUpperCase().startsWith('FOREIGN KEY'));

      const card = document.createElement('div');
      card.className = 'schema-table-item';
      card.innerHTML = `
        <div class="schema-table-header">
          <i class="fa-solid fa-table"></i> ${escapeHtml(tableName)}
        </div>
        <div class="schema-column-list">
          ${colLines.slice(0, 5).map(c => `<div>${escapeHtml(c)}</div>`).join('')}
          ${colLines.length > 5 ? `<div style="color:var(--text-muted); font-size: 10px;">+ ${colLines.length - 5} more columns...</div>` : ''}
        </div>
      `;
      explorer.appendChild(card);
    }

    if (count === 0) {
      explorer.innerHTML = '<div style="color:var(--text-muted); font-size:12px; padding:8px;">No tables found in database.</div>';
    }
  } catch (err) {
    console.error('Schema fetch failed:', err);
  }
}

// ── Modals & Loading ───────────────────────────────────────
function openSchemaModal() {
  document.getElementById('schemaModal').classList.remove('hidden');
}

function closeSchemaModal(e) {
  if (e && e.target !== e.currentTarget && !e.target.closest('.close-btn')) return;
  document.getElementById('schemaModal').classList.add('hidden');
}

function setLoading(isLoading) {
  const overlay = document.getElementById('loadingOverlay');
  const submitBtn = document.getElementById('submitBtn');
  if (isLoading) {
    overlay.classList.remove('hidden');
    submitBtn.disabled = true;
  } else {
    overlay.classList.add('hidden');
    submitBtn.disabled = false;
  }
}

function escapeHtml(text) {
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
  return String(text).replace(/[&<>"']/g, m => map[m]);
}
