/* ==================================================
   DASHBOARD CONTROLLER (dashboard.js)
   Sidebar Navigation, Tab Switching, Data Sync, Loaders
   ================================================== */

let currentStudentProfile = null;
let currentRiskAssessment = null;

document.addEventListener('DOMContentLoaded', async () => {
  // Check Authentication & Load Profile
  const authenticated = await checkAuthAndLoadProfile();
  if (!authenticated) return;

  // Initialize Sidebar Navigation
  setupSidebarNavigation();

  // Load Overview Data & Initial Risk Assessment
  loadOverviewData();
  
  // Load Fuzzy System & Model Evaluation Info
  loadFuzzySystemData();
  loadEvaluationData();
});

async function checkAuthAndLoadProfile() {
  try {
    const res = await fetch('/api/profile');
    if (!res.ok) {
      window.location.href = 'login.html';
      return false;
    }

    const data = await res.json();
    currentStudentProfile = data;

    // Update Header & Sidebar User Details
    const nameEls = document.querySelectorAll('.user-name-display');
    nameEls.forEach(el => el.textContent = data.name);

    const emailEls = document.querySelectorAll('.user-email-display');
    emailEls.forEach(el => el.textContent = data.email);

    const avatarEls = document.querySelectorAll('.user-avatar-initials');
    const initials = data.name.split(' ').map(n => n[0]).join('').toUpperCase();
    avatarEls.forEach(el => el.textContent = initials || 'S');

    return true;
  } catch (err) {
    console.error('Auth verification error:', err);
    window.location.href = 'login.html';
    return false;
  }
}

function setupSidebarNavigation() {
  const navItems = document.querySelectorAll('.nav-item');
  const tabPanes = document.querySelectorAll('.tab-pane');
  const topTitle = document.getElementById('topBarTitle');

  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const targetTab = item.getAttribute('data-tab');
      if (!targetTab) return;

      // Update Nav active class
      navItems.forEach(n => n.classList.remove('active'));
      item.classList.add('active');

      // Update Tab Pane visibility
      tabPanes.forEach(pane => {
        if (pane.id === `tab-${targetTab}`) {
          pane.classList.add('active');
        } else {
          pane.classList.remove('active');
        }
      });

      // Update Top Bar Title
      if (topTitle) {
        topTitle.textContent = item.textContent.trim();
      }

      // Trigger view-specific re-renders if necessary
      if (targetTab === 'analytics' && typeof renderOverviewCharts === 'function') {
        renderOverviewCharts();
      } else if (targetTab === 'evaluation' && typeof renderEvaluationCharts === 'function') {
        renderEvaluationCharts();
      } else if (targetTab === 'fuzzy' && typeof renderFuzzyCharts === 'function') {
        renderFuzzyCharts();
      } else if (targetTab === 'ga' && typeof renderGACharts === 'function') {
        renderGACharts();
      }
    });
  });
}

async function loadOverviewData() {
  try {
    const res = await fetch('/api/analytics');
    if (!res.ok) return;
    const data = await res.json();
    
    // Update Overview Metric Counters
    const totalStudentsEl = document.getElementById('metricTotalStudents');
    if (totalStudentsEl) totalStudentsEl.textContent = data.inspection.num_rows.toLocaleString();

    // Trigger Chart.js overview charts rendering
    if (typeof initOverviewCharts === 'function') {
      initOverviewCharts(data);
    }
  } catch (err) {
    console.error('Error loading analytics:', err);
  }
}

async function loadFuzzySystemData() {
  try {
    const res = await fetch('/api/fuzzy/rules');
    if (!res.ok) return;
    const data = await res.json();
    
    const rulesListEl = document.getElementById('fuzzyRulesContainer');
    if (rulesListEl) {
      rulesListEl.innerHTML = data.rules.map(r => `
        <tr class="hover:bg-slate-50">
          <td class="px-4 py-2 font-bold text-slate-700">R${r.id}</td>
          <td class="px-4 py-2 text-slate-800 font-mono text-sm">${r.desc}</td>
          <td class="px-4 py-2"><span class="badge badge-${r.consequent.toLowerCase().replace('_', '-')}">${r.consequent}</span></td>
        </tr>
      `).join('');
    }
  } catch (err) {
    console.error('Error loading fuzzy rules:', err);
  }
}

async function loadEvaluationData() {
  try {
    const res = await fetch('/api/evaluation');
    if (!res.ok) return;
    const data = await res.json();

    // Render Evaluation Summary Table
    const evalTableEl = document.getElementById('evaluationMetricsTable');
    if (evalTableEl) {
      const base = data.baseline_model;
      const opt = data.optimized_model;
      evalTableEl.innerHTML = `
        <tr>
          <td class="font-semibold">Accuracy</td>
          <td>${(base.accuracy * 100).toFixed(1)}%</td>
          <td class="font-bold text-emerald-600">${(opt.accuracy * 100).toFixed(1)}%</td>
          <td class="text-emerald-600 font-bold">+${(data.improvement.accuracy_diff * 100).toFixed(1)}%</td>
        </tr>
        <tr>
          <td class="font-semibold">F1-Score (Macro)</td>
          <td>${base.f1_macro.toFixed(3)}</td>
          <td class="font-bold text-emerald-600">${opt.f1_macro.toFixed(3)}</td>
          <td class="text-emerald-600 font-bold">+${data.improvement.f1_diff.toFixed(3)}</td>
        </tr>
        <tr>
          <td class="font-semibold">RMSE (Error)</td>
          <td>${base.rmse.toFixed(2)}</td>
          <td class="font-bold text-emerald-600">${opt.rmse.toFixed(2)}</td>
          <td class="text-emerald-600 font-bold">-${data.improvement.rmse_diff.toFixed(2)}</td>
        </tr>
        <tr>
          <td class="font-semibold">MAE (Mean Abs Error)</td>
          <td>${base.mae.toFixed(2)}</td>
          <td class="font-bold text-emerald-600">${opt.mae.toFixed(2)}</td>
          <td class="text-emerald-600 font-bold">-${data.improvement.mae_diff.toFixed(2)}</td>
        </tr>
        <tr>
          <td class="font-semibold">ROC / AUC (OVR)</td>
          <td>${base.auc_ovr.toFixed(3)}</td>
          <td class="font-bold text-emerald-600">${opt.auc_ovr.toFixed(3)}</td>
          <td class="text-emerald-600 font-bold">+${(opt.auc_ovr - base.auc_ovr).toFixed(3)}</td>
        </tr>
      `;
    }

    if (typeof initEvaluationCharts === 'function') {
      initEvaluationCharts(data);
    }
  } catch (err) {
    console.error('Error loading evaluation:', err);
  }
}
