/* ==================================================
   RISK ASSESSMENT MODULE (risk.js)
   Form inputs, predict REST API calls, animated gauge, rules & recommendations
   ================================================== */

document.addEventListener('DOMContentLoaded', () => {
  setupRiskAssessmentForm();
  
  // Auto run initial risk calculation with default values
  triggerRiskPrediction();
});

function setupRiskAssessmentForm() {
  const form = document.getElementById('riskAssessmentForm');
  if (!form) return;

  // Sync range inputs with live value labels
  const inputs = [
    { slider: 'inputAttendance', label: 'valAttendance', suffix: '%' },
    { slider: 'inputStudyHours', label: 'valStudyHours', suffix: ' hrs/wk' },
    { slider: 'inputAssignment', label: 'valAssignment', suffix: '%' },
    { slider: 'inputExamScore', label: 'valExamScore', suffix: ' marks' },
    { slider: 'inputStressLevel', label: 'valStressLevel', suffix: '' }
  ];

  inputs.forEach(item => {
    const sliderEl = document.getElementById(item.slider);
    const labelEl = document.getElementById(item.label);
    if (sliderEl && labelEl) {
      sliderEl.addEventListener('input', () => {
        let displayVal = sliderEl.value;
        if (item.slider === 'inputStressLevel') {
          const stressMap = { '0': '0 (Low)', '1': '1 (Medium)', '2': '2 (High)' };
          displayVal = stressMap[displayVal] || displayVal;
        }
        labelEl.textContent = `${displayVal}${item.suffix}`;
      });
    }
  });

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    triggerRiskPrediction();
  });
}

async function triggerRiskPrediction() {
  const attendance = parseFloat(document.getElementById('inputAttendance')?.value || 75);
  const studyHours = parseFloat(document.getElementById('inputStudyHours')?.value || 18);
  const assignment = parseFloat(document.getElementById('inputAssignment')?.value || 75);
  const examScore = parseFloat(document.getElementById('inputExamScore')?.value || 65);
  const stressLevel = parseFloat(document.getElementById('inputStressLevel')?.value || 1);
  const internet = parseInt(document.getElementById('inputInternet')?.value || 1);

  const payload = {
    Attendance: attendance,
    StudyHours: studyHours,
    AssignmentCompletion: assignment,
    ExamScore: examScore,
    StressLevel: stressLevel,
    Internet: internet
  };

  try {
    const res = await fetch('/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      showToast('Error generating risk score.', 'error');
      return;
    }

    const data = await res.json();
    currentRiskAssessment = data;

    // Render Risk Results across Dashboard Views
    renderRiskResults(data);

  } catch (err) {
    console.error('Prediction API Error:', err);
    showToast('Failed to connect to fuzzy risk backend.', 'error');
  }
}

function renderRiskResults(data) {
  // 1. Animated Risk Gauge & Score Count-Up
  const scoreNumEls = document.querySelectorAll('.risk-score-display');
  scoreNumEls.forEach(el => animateValue(el, 0, data.risk_score, 800));

  const catBadgeEls = document.querySelectorAll('.risk-category-badge');
  catBadgeEls.forEach(el => {
    el.textContent = data.risk_category;
    el.className = `badge badge-${data.risk_level_code.toLowerCase().replace('_', '-')}`;
    el.style.backgroundColor = data.risk_color + '22';
    el.style.color = data.risk_color;
  });

  const gaugeCircleEls = document.querySelectorAll('.gauge-circle');
  gaugeCircleEls.forEach(circle => {
    circle.style.setProperty('--score', data.risk_score);
    circle.style.setProperty('--risk-color', data.risk_color);
  });

  // 2. Overview Quick Metrics
  const topFactorEl = document.getElementById('overviewTopFactor');
  if (topFactorEl) topFactorEl.textContent = data.top_risk_factor;

  const expEl = document.getElementById('riskExplanationText');
  if (expEl) expEl.textContent = data.explanation;

  // 3. Render Factor Contribution Progress Bars
  const factorContainer = document.getElementById('factorContributionContainer');
  if (factorContainer) {
    factorContainer.innerHTML = data.factor_contributions.map(c => `
      <div class="factor-bar-item">
        <div class="factor-bar-header">
          <span>${c.factor} (${c.raw_value}${c.unit})</span>
          <span style="color: ${c.color}">${c.impact_level} (${c.contribution_percentage}%)</span>
        </div>
        <div class="factor-progress-track">
          <div class="factor-progress-fill" style="width: ${c.contribution_percentage}%; background-color: ${c.color};"></div>
        </div>
      </div>
    `).join('');
  }

  // 4. Render Activated Rules
  const rulesContainer = document.getElementById('activatedRulesContainer');
  if (rulesContainer) {
    if (data.activated_rules.length === 0) {
      rulesContainer.innerHTML = `<tr><td colspan="3" class="text-center py-4 text-slate-500">No fuzzy rules activated</td></tr>`;
    } else {
      rulesContainer.innerHTML = data.activated_rules.map(r => `
        <tr>
          <td class="font-bold text-slate-700">R${r.id}</td>
          <td class="font-mono text-sm text-slate-800">${r.rule_text}</td>
          <td class="text-right font-bold text-blue-600">${(r.firing_strength * 100).toFixed(1)}%</td>
        </tr>
      `).join('');
    }
  }

  // 5. Render Personalized Recommendations
  const recContainer = document.getElementById('recommendationsListContainer');
  if (recContainer && data.recommendations) {
    recContainer.innerHTML = data.recommendations.map(r => `
      <div class="rec-card priority-${r.priority}">
        <div class="flex justify-between items-center mb-2">
          <h4 class="font-bold text-slate-900">${r.factor}: ${r.current_condition}</h4>
          <span class="badge ${r.priority === 'Urgent' ? 'badge-high' : r.priority === 'High' ? 'badge-moderate' : 'badge-low'}">${r.priority} Priority</span>
        </div>
        <p class="text-sm text-slate-600 mb-2"><strong>Why it matters:</strong> ${r.why_it_matters}</p>
        <p class="text-sm text-slate-800 font-semibold bg-white p-2 rounded border border-slate-200"><strong>Recommended Action:</strong> ${r.action}</p>
      </div>
    `).join('');
  }

  // 6. Update Factor Impact Chart if available
  if (typeof updateFactorImpactChart === 'function') {
    updateFactorImpactChart(data.factor_contributions);
  }
}

function animateValue(obj, start, end, duration) {
  if (!obj) return;
  let startTimestamp = null;
  const step = (timestamp) => {
    if (!startTimestamp) startTimestamp = timestamp;
    const progress = Math.min((timestamp - startTimestamp) / duration, 1);
    const currentVal = (progress * (end - start) + start).toFixed(1);
    obj.innerHTML = currentVal;
    if (progress < 1) {
      window.requestAnimationFrame(step);
    }
  };
  window.requestAnimationFrame(step);
}
