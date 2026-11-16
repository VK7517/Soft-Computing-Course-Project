/* ==================================================
   WHAT-IF SIMULATOR MODULE (simulator.js)
   Interactive scenario analysis, API /api/simulate integration
   ================================================== */

document.addEventListener('DOMContentLoaded', () => {
  setupSimulatorControls();
});

function setupSimulatorControls() {
  const form = document.getElementById('simulatorForm');
  if (!form) return;

  const simInputs = [
    { slider: 'simAttendance', label: 'valSimAttendance', suffix: '%' },
    { slider: 'simStudyHours', label: 'valSimStudyHours', suffix: ' hrs/wk' },
    { slider: 'simAssignment', label: 'valSimAssignment', suffix: '%' },
    { slider: 'simExamScore', label: 'valSimExamScore', suffix: ' marks' },
    { slider: 'simStressLevel', label: 'valSimStressLevel', suffix: '' }
  ];

  simInputs.forEach(item => {
    const sliderEl = document.getElementById(item.slider);
    const labelEl = document.getElementById(item.label);
    if (sliderEl && labelEl) {
      sliderEl.addEventListener('input', () => {
        let displayVal = sliderEl.value;
        if (item.slider === 'simStressLevel') {
          const stressMap = { '0': '0 (Low)', '1': '1 (Medium)', '2': '2 (High)' };
          displayVal = stressMap[displayVal] || displayVal;
        }
        labelEl.textContent = `${displayVal}${item.suffix}`;
        triggerSimulation();
      });
    }
  });

  const resetBtn = document.getElementById('resetSimulatorBtn');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      // Sync simulator sliders back to current risk assessment inputs
      if (currentRiskAssessment && currentRiskAssessment.raw_inputs) {
        const raw = currentRiskAssessment.raw_inputs;
        setSliderVal('simAttendance', 'valSimAttendance', raw.Attendance, '%');
        setSliderVal('simStudyHours', 'valSimStudyHours', raw.StudyHours, ' hrs/wk');
        setSliderVal('simAssignment', 'valSimAssignment', raw.AssignmentCompletion, '%');
        setSliderVal('simExamScore', 'valSimExamScore', raw.ExamScore, ' marks');
        setSliderVal('simStressLevel', 'valSimStressLevel', raw.StressLevel, '');
        const netEl = document.getElementById('simInternet');
        if (netEl) netEl.value = raw.Internet;
      }
      triggerSimulation();
    });
  }

  const netEl = document.getElementById('simInternet');
  if (netEl) {
    netEl.addEventListener('change', triggerSimulation);
  }
}

function setSliderVal(sliderId, labelId, val, suffix) {
  const sliderEl = document.getElementById(sliderId);
  const labelEl = document.getElementById(labelId);
  if (sliderEl) sliderEl.value = val;
  if (labelEl) labelEl.textContent = `${val}${suffix}`;
}

async function triggerSimulation() {
  if (!currentRiskAssessment || !currentRiskAssessment.raw_inputs) return;

  const currentInputs = currentRiskAssessment.raw_inputs;
  const simulatedInputs = {
    Attendance: parseFloat(document.getElementById('simAttendance')?.value || currentInputs.Attendance),
    StudyHours: parseFloat(document.getElementById('simStudyHours')?.value || currentInputs.StudyHours),
    AssignmentCompletion: parseFloat(document.getElementById('simAssignment')?.value || currentInputs.AssignmentCompletion),
    ExamScore: parseFloat(document.getElementById('simExamScore')?.value || currentInputs.ExamScore),
    StressLevel: parseFloat(document.getElementById('simStressLevel')?.value || currentInputs.StressLevel),
    Internet: parseInt(document.getElementById('simInternet')?.value || currentInputs.Internet)
  };

  try {
    const res = await fetch('/api/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ current: currentInputs, simulated: simulatedInputs })
    });

    if (!res.ok) return;
    const data = await res.json();

    renderSimulationResults(data);
  } catch (err) {
    console.error('Simulation error:', err);
  }
}

function renderSimulationResults(data) {
  // Update Current vs Simulated Scores
  const curScoreEl = document.getElementById('simCurrentScore');
  if (curScoreEl) curScoreEl.textContent = `${data.current_risk_score.toFixed(1)}%`;

  const simScoreEl = document.getElementById('simProjectedScore');
  if (simScoreEl) simScoreEl.textContent = `${data.simulated_risk_score.toFixed(1)}%`;

  const diffEl = document.getElementById('simDiffDisplay');
  if (diffEl) {
    const diff = data.risk_difference;
    if (diff < 0) {
      diffEl.className = 'text-emerald-600 font-extrabold text-2xl';
      diffEl.textContent = `↓ ${Math.abs(diff).toFixed(1)}% (Risk Reduced)`;
    } else if (diff > 0) {
      diffEl.className = 'text-red-600 font-extrabold text-2xl';
      diffEl.textContent = `↑ ${diff.toFixed(1)}% (Risk Increased)`;
    } else {
      diffEl.className = 'text-slate-600 font-extrabold text-2xl';
      diffEl.textContent = `0.0% (No Change)`;
    }
  }

  // Render Factor Changes
  const changesContainer = document.getElementById('simFactorChangesContainer');
  if (changesContainer) {
    if (data.factor_changes.length === 0) {
      changesContainer.innerHTML = `<p class="text-sm text-slate-500 italic">Adjust the sliders above to see how changing study habits impacts student risk.</p>`;
    } else {
      changesContainer.innerHTML = data.factor_changes.map(c => `
        <div class="flex justify-between items-center p-2 mb-2 rounded bg-slate-50 border border-slate-200">
          <div>
            <span class="font-bold text-slate-800">${c.factor}</span>
            <span class="text-xs text-slate-500"> (${c.current_val} → ${c.simulated_val} ${c.unit})</span>
          </div>
          <span class="badge ${c.is_improved ? 'badge-very-low' : 'badge-high'}">
            ${c.is_improved ? 'Improved' : 'Worsened'} (${c.change > 0 ? '+' : ''}${c.change})
          </span>
        </div>
      `).join('');
    }
  }

  // Render Updated Recommendations for Simulated State
  const simRecContainer = document.getElementById('simUpdatedRecsContainer');
  if (simRecContainer && data.updated_recommendations) {
    simRecContainer.innerHTML = data.updated_recommendations.map(r => `
      <div class="rec-card priority-${r.priority}">
        <h4 class="font-bold text-slate-900 text-sm mb-1">${r.factor}: ${r.current_condition}</h4>
        <p class="text-xs text-slate-700 font-medium">${r.action}</p>
      </div>
    `).join('');
  }
}
