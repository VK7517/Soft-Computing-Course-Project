/* ==================================================
   CHART.JS VISUALIZATION ENGINE (charts.js)
   Overview Charts, Factor Impact, GA Convergence, Model Evaluation
   ================================================== */

let chartInstances = {};

function initOverviewCharts(analyticsData) {
  if (!window.Chart) return;

  // 1. Grade Distribution Chart
  const gradeCtx = document.getElementById('chartGradeDistribution')?.getContext('2d');
  if (gradeCtx) {
    if (chartInstances.gradeDist) chartInstances.gradeDist.destroy();
    
    const labels = Object.keys(analyticsData.grade_distribution);
    const values = Object.values(analyticsData.grade_distribution);

    chartInstances.gradeDist = new Chart(gradeCtx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: values,
          backgroundColor: ['#10B981', '#3B82F6', '#F59E0B', '#EF4444'],
          borderWidth: 2,
          borderColor: '#FFFFFF'
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'bottom' },
          title: { display: true, text: 'Dataset Final Grade Distribution' }
        }
      }
    });
  }

  // 2. Attendance vs Grade Chart
  const attCtx = document.getElementById('chartAttendanceVsGrade')?.getContext('2d');
  if (attCtx && analyticsData.averages_by_grade) {
    if (chartInstances.attVsGrade) chartInstances.attVsGrade.destroy();

    const grades = ['0', '1', '2', '3'];
    const gradeNames = ['Grade F (0)', 'Grade C (1)', 'Grade B (2)', 'Grade A (3)'];
    const attVals = grades.map(g => (analyticsData.averages_by_grade.Attendance[g] || 0).toFixed(1));

    chartInstances.attVsGrade = new Chart(attCtx, {
      type: 'bar',
      data: {
        labels: gradeNames,
        datasets: [{
          label: 'Average Attendance (%)',
          data: attVals,
          backgroundColor: '#3B82F6',
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        scales: { y: { min: 50, max: 100 } },
        plugins: { legend: { display: false } }
      }
    });
  }
}

function updateFactorImpactChart(contributions) {
  if (!window.Chart) return;
  const ctx = document.getElementById('chartFactorImpact')?.getContext('2d');
  if (!ctx) return;

  if (chartInstances.factorImpact) chartInstances.factorImpact.destroy();

  const labels = contributions.map(c => c.factor);
  const data = contributions.map(c => c.contribution_percentage);
  const colors = contributions.map(c => c.color);

  chartInstances.factorImpact = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Risk Contribution (%)',
        data: data,
        backgroundColor: colors,
        borderRadius: 6
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      scales: { x: { max: 50 } },
      plugins: { legend: { display: false } }
    }
  });
}

function initEvaluationCharts(evalData) {
  if (!window.Chart) return;

  // Baseline vs GA-Optimized Model Performance Comparison
  const compCtx = document.getElementById('chartModelComparison')?.getContext('2d');
  if (compCtx) {
    if (chartInstances.modelComp) chartInstances.modelComp.destroy();

    const base = evalData.baseline_model;
    const opt = evalData.optimized_model;

    chartInstances.modelComp = new Chart(compCtx, {
      type: 'bar',
      data: {
        labels: ['Accuracy (%)', 'F1-Score', 'Precision', 'Recall', 'MAE (Error)'],
        datasets: [
          {
            label: 'Baseline Fuzzy Model',
            data: [(base.accuracy * 100).toFixed(1), base.f1_macro.toFixed(3), base.precision_macro.toFixed(3), base.recall_macro.toFixed(3), base.mae.toFixed(2)],
            backgroundColor: '#94A3B8',
            borderRadius: 6
          },
          {
            label: 'GA-Optimized Fuzzy Model',
            data: [(opt.accuracy * 100).toFixed(1), opt.f1_macro.toFixed(3), opt.precision_macro.toFixed(3), opt.recall_macro.toFixed(3), opt.mae.toFixed(2)],
            backgroundColor: '#2563EB',
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: 'top' } }
      }
    });
  }

  // GA Convergence History Chart
  const gaCtx = document.getElementById('chartGAConvergence')?.getContext('2d');
  if (gaCtx && evalData.ga_history) {
    if (chartInstances.gaConvergence) chartInstances.gaConvergence.destroy();

    const h = evalData.ga_history;
    chartInstances.gaConvergence = new Chart(gaCtx, {
      type: 'line',
      data: {
        labels: h.generations.map(g => `Gen ${g}`),
        datasets: [
          {
            label: 'Best Fitness',
            data: h.best_fitness,
            borderColor: '#10B981',
            backgroundColor: '#10B98122',
            fill: true,
            tension: 0.3
          },
          {
            label: 'Average Fitness',
            data: h.avg_fitness,
            borderColor: '#3B82F6',
            borderDash: [5, 5],
            fill: false,
            tension: 0.3
          }
        ]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: 'top' } }
      }
    });
  }
}
