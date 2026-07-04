// ============================================
// 晚秋记账 - 前端逻辑
// 负责页面切换、表单处理、数据渲染、图表绘制
// ============================================

// ---- 全局状态 ----
let currentPage = 'add-record';
let pieChart = null;          // 饼图实例（用于更新/销毁）

// ---- 工具函数 ----
function formatMoney(amount) {
  return '¥ ' + Number(amount).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}

function getToday() {
  return new Date().toISOString().split('T')[0];
}

function getCurrentMonth() {
  const d = new Date();
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0');
}

// ============================================
// 1. 侧边栏导航
// ============================================
document.querySelectorAll('.nav-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    // 切换 active 样式
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    // 切换页面
    const pageName = btn.dataset.page;
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById('page-' + pageName).classList.add('active');
    currentPage = pageName;

    // 进入页面时加载对应数据
    if (pageName === 'records-list') loadRecords();
    else if (pageName === 'statistics') loadStatistics();
    else if (pageName === 'categories') loadCategories();
    else if (pageName === 'add-record') loadCategoriesForForm();
  });
});

// ============================================
// 2. 记一笔 - 表单处理
// ============================================
const recordForm = document.getElementById('record-form');
const recordDate = document.getElementById('record-date');
const recordCategory = document.getElementById('record-category');
const recordType = document.getElementById('record-type');

// 设置默认日期为今天
recordDate.value = getToday();

// 切换类型时更新分类列表
recordType.addEventListener('change', () => loadCategoriesForForm());

// 加载分类到下拉框
async function loadCategoriesForForm() {
  const categories = await window.electronAPI.getCategories();
  const type = recordType.value;
  // 收入类型只显示"收入"分类，支出类型显示除收入外的所有分类
  const filtered = type === 'income'
    ? categories.filter(c => c.name === '收入')
    : categories.filter(c => c.name !== '收入');

  recordCategory.innerHTML = '<option value="">请选择分类</option>';
  filtered.forEach(c => {
    recordCategory.innerHTML += `<option value="${c.name}">${c.icon} ${c.name}</option>`;
  });
}

// 提交表单 - 新增记录
recordForm.addEventListener('submit', async (e) => {
  e.preventDefault();

  const amount = parseFloat(document.getElementById('record-amount').value);
  const type = recordType.value;
  const category = recordCategory.value;
  const note = document.getElementById('record-note').value.trim();
  const date = recordDate.value;

  if (!amount || amount <= 0) {
    alert('请输入有效的金额');
    return;
  }
  if (!category) {
    alert('请选择分类');
    return;
  }
  if (!date) {
    alert('请选择日期');
    return;
  }

  await window.electronAPI.addRecord({
    amount,
    type,
    category,
    subCategory: '',
    note,
    date
  });

  // 清空表单
  document.getElementById('record-amount').value = '';
  document.getElementById('record-note').value = '';
  recordCategory.value = '';
  recordDate.value = getToday();

  // 刷新侧边栏汇总
  updateSidebarSummary();

  alert('✅ 记录保存成功！');
});

// ============================================
// 3. 账单列表
// ============================================
const filterMonth = document.getElementById('filter-month');
filterMonth.value = getCurrentMonth();

// 监听月份筛选变化
filterMonth.addEventListener('change', () => loadRecords());
document.getElementById('btn-clear-filter').addEventListener('click', () => {
  filterMonth.value = '';
  loadRecords();
});

async function loadRecords() {
  const month = filterMonth.value || null;
  const records = await window.electronAPI.getRecords({ month });
  const tbody = document.getElementById('records-tbody');

  if (records.length === 0) {
    tbody.innerHTML = '<tr class="empty-row"><td colspan="6">暂无记录，去"记一笔"添加吧</td></tr>';
    return;
  }

  tbody.innerHTML = records.map(r => `
    <tr>
      <td>${r.date}</td>
      <td><span class="type-badge ${r.type}">${r.type === 'expense' ? '支出' : '收入'}</span></td>
      <td>${r.category}</td>
      <td class="${r.type === 'expense' ? 'amount-expense' : 'amount-income'}">
        ${r.type === 'expense' ? '-' : '+'}${formatMoney(r.amount)}
      </td>
      <td>${r.note || '-'}</td>
      <td>
        <button class="btn btn-small btn-outline" onclick="openEditModal(${r.id})">编辑</button>
        <button class="btn btn-small btn-danger" onclick="deleteRecord(${r.id})">删除</button>
      </td>
    </tr>
  `).join('');
}

async function deleteRecord(id) {
  if (!confirm('确定要删除这条记录吗？此操作不可撤销。')) return;
  await window.electronAPI.deleteRecord(id);
  loadRecords();
  updateSidebarSummary();
}

// ============================================
// 4. 编辑弹窗
// ============================================
const editModal = document.getElementById('edit-modal');
const editForm = document.getElementById('edit-form');

async function openEditModal(id) {
  // 获取所有记录，找到对应的那条
  const allRecords = await window.electronAPI.getRecords({ month: null });
  const record = allRecords.find(r => r.id === id);
  if (!record) return;

  document.getElementById('edit-id').value = record.id;
  document.getElementById('edit-amount').value = record.amount;
  document.getElementById('edit-type').value = record.type;
  document.getElementById('edit-date').value = record.date;
  document.getElementById('edit-note').value = record.note || '';

  // 加载分类下拉框
  const categories = await window.electronAPI.getCategories();
  const editCategory = document.getElementById('edit-category');
  const filtered = record.type === 'income'
    ? categories.filter(c => c.name === '收入')
    : categories.filter(c => c.name !== '收入');
  editCategory.innerHTML = filtered.map(c =>
    `<option value="${c.name}" ${c.name === record.category ? 'selected' : ''}>${c.icon} ${c.name}</option>`
  ).join('');

  editModal.style.display = 'flex';

  // 切换编辑类型时重新加载分类
  document.getElementById('edit-type').onchange = async function() {
    const cats = await window.electronAPI.getCategories();
    const f = this.value === 'income'
      ? cats.filter(c => c.name === '收入')
      : cats.filter(c => c.name !== '收入');
    editCategory.innerHTML = f.map(c => `<option value="${c.name}">${c.icon} ${c.name}</option>`).join('');
  };
}

editForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  await window.electronAPI.updateRecord({
    id: parseInt(document.getElementById('edit-id').value),
    amount: parseFloat(document.getElementById('edit-amount').value),
    type: document.getElementById('edit-type').value,
    category: document.getElementById('edit-category').value,
    subCategory: '',
    note: document.getElementById('edit-note').value.trim(),
    date: document.getElementById('edit-date').value
  });
  editModal.style.display = 'none';
  loadRecords();
  updateSidebarSummary();
});

document.getElementById('btn-close-modal').addEventListener('click', () => {
  editModal.style.display = 'none';
});

// 点击弹窗背景关闭
editModal.addEventListener('click', (e) => {
  if (e.target === editModal) editModal.style.display = 'none';
});

// ============================================
// 5. 月度统计
// ============================================
const statsMonth = document.getElementById('stats-month');
statsMonth.value = getCurrentMonth();
statsMonth.addEventListener('change', () => loadStatistics());

async function loadStatistics() {
  const month = statsMonth.value;
  const stats = await window.electronAPI.getMonthlyStats(month);

  // 更新汇总卡片
  document.getElementById('stats-expense-total').textContent = formatMoney(stats.expenseTotal);
  document.getElementById('stats-income-total').textContent = formatMoney(stats.incomeTotal);
  document.getElementById('stats-balance').textContent = formatMoney(stats.incomeTotal - stats.expenseTotal);

  // 更新饼图
  const canvas = document.getElementById('pie-chart');
  const noDataHint = document.getElementById('no-data-hint');

  if (stats.expenseStats.length === 0) {
    canvas.style.display = 'none';
    noDataHint.style.display = 'block';
    if (pieChart) { pieChart.destroy(); pieChart = null; }
    return;
  }

  canvas.style.display = 'block';
  noDataHint.style.display = 'none';

  // 准备饼图数据
  const labels = stats.expenseStats.map(s => s.category);
  const data = stats.expenseStats.map(s => s.total);
  const colors = [
    '#e74c3c', '#e67e22', '#f1c40f', '#2ecc71', '#1abc9c',
    '#3498db', '#9b59b6', '#e91e63', '#00bcd4', '#ff9800',
    '#795548', '#607d8b'
  ];

  if (pieChart) pieChart.destroy();

  pieChart = new Chart(canvas, {
    type: 'pie',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: colors.slice(0, labels.length),
        borderWidth: 2,
        borderColor: '#fff'
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            padding: 16,
            font: { size: 13 }
          }
        },
        tooltip: {
          callbacks: {
            label: function(ctx) {
              const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
              const pct = ((ctx.raw / total) * 100).toFixed(1);
              return ctx.label + ': ' + formatMoney(ctx.raw) + ' (' + pct + '%)';
            }
          }
        }
      }
    }
  });
}

// ============================================
// 6. 分类管理
// ============================================
async function loadCategories() {
  const categories = await window.electronAPI.getCategories();
  const grid = document.getElementById('categories-grid');

  grid.innerHTML = categories.map(c => `
    <div class="category-card">
      <div class="category-info">
        <span class="category-icon">${c.icon}</span>
        <span class="category-name">${c.name}</span>
        ${c.is_default ? '<span class="default-badge">默认</span>' : ''}
      </div>
      ${c.is_default
        ? ''
        : `<button class="category-delete" onclick="deleteCategory(${c.id}, '${c.name}')" title="删除">✕</button>`
      }
    </div>
  `).join('');
}

async function deleteCategory(id, name) {
  if (!confirm(`确定要删除分类「${name}」吗？`)) return;
  await window.electronAPI.deleteCategory(id);
  loadCategories();
}

document.getElementById('btn-add-category').addEventListener('click', async () => {
  const name = document.getElementById('new-category-name').value.trim();
  const icon = document.getElementById('new-category-icon').value.trim() || '📌';

  if (!name) {
    alert('请输入分类名称');
    return;
  }

  try {
    await window.electronAPI.addCategory({ name, icon });
    document.getElementById('new-category-name').value = '';
    document.getElementById('new-category-icon').value = '';
    loadCategories();
  } catch (err) {
    alert('添加失败，分类名称可能已存在');
  }
});

// ============================================
// 7. 侧边栏本月支出汇总
// ============================================
async function updateSidebarSummary() {
  const month = getCurrentMonth();
  const stats = await window.electronAPI.getMonthlyStats(month);
  document.getElementById('sidebar-expense').textContent = formatMoney(stats.expenseTotal);
}

// ============================================
// 8. 启动时初始化
// ============================================
async function init() {
  await loadCategoriesForForm();
  await updateSidebarSummary();
}

init();
