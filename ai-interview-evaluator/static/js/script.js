/**
 * AI Interview Evaluator - Client Script
 * Handles question stepper navigation, real-time counters, Chart.js visualizations, and filters.
 */

document.addEventListener('DOMContentLoaded', function () {
  initInterviewRoom();
  initHistorySearch();
});

/* ================= INTERVIEW ROOM LOGIC ================= */
function initInterviewRoom() {
  const cards = document.querySelectorAll('.question-card');
  if (!cards.length) return;

  let currentIdx = 0;
  const total = cards.length;

  const prevBtn = document.getElementById('prevBtn');
  const nextBtn = document.getElementById('nextBtn');
  const submitBtn = document.getElementById('submitBtn');
  const progressFill = document.getElementById('progressBarFill');
  const progressText = document.getElementById('progressText');
  const interviewForm = document.getElementById('interviewForm');

  function updateView() {
    cards.forEach((card, index) => {
      if (index === currentIdx) {
        card.classList.add('active');
        const textarea = card.querySelector('textarea');
        if (textarea) {
          updateCounts(textarea);
        }
      } else {
        card.classList.remove('active');
      }
    });

    // Update buttons
    if (prevBtn) {
      prevBtn.style.display = currentIdx === 0 ? 'none' : 'inline-flex';
    }

    if (nextBtn) {
      nextBtn.style.display = currentIdx === total - 1 ? 'none' : 'inline-flex';
    }

    if (submitBtn) {
      submitBtn.style.display = currentIdx === total - 1 ? 'inline-flex' : 'none';
    }

    // Update progress bar
    const percent = Math.round(((currentIdx + 1) / total) * 100);
    if (progressFill) {
      progressFill.style.width = percent + '%';
    }
    if (progressText) {
      progressText.textContent = `Question ${currentIdx + 1} of ${total} (${percent}%)`;
    }
  }

  function updateCounts(textarea) {
    const card = textarea.closest('.question-card');
    if (!card) return;
    const wordCountEl = card.querySelector('.word-count');
    const charCountEl = card.querySelector('.char-count');

    const text = textarea.value.trim();
    const words = text ? text.split(/\s+/).length : 0;
    const chars = textarea.value.length;

    if (wordCountEl) wordCountEl.textContent = `${words} words`;
    if (charCountEl) charCountEl.textContent = `${chars} characters`;
  }

  // Bind textarea input events
  document.querySelectorAll('.answer-textarea').forEach(textarea => {
    textarea.addEventListener('input', function () {
      updateCounts(this);
    });
  });

  if (prevBtn) {
    prevBtn.addEventListener('click', function () {
      if (currentIdx > 0) {
        currentIdx--;
        updateView();
      }
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', function () {
      const activeCard = cards[currentIdx];
      const textarea = activeCard.querySelector('textarea');
      if (textarea && !textarea.value.trim()) {
        alert('Please write an answer for this question before proceeding to the next.');
        textarea.focus();
        return;
      }
      if (currentIdx < total - 1) {
        currentIdx++;
        updateView();
      }
    });
  }

  if (interviewForm) {
    interviewForm.addEventListener('submit', function (e) {
      // Validate all answers are non-empty
      for (let i = 0; i < cards.length; i++) {
        const textarea = cards[i].querySelector('textarea');
        if (!textarea || !textarea.value.trim()) {
          e.preventDefault();
          currentIdx = i;
          updateView();
          alert(`Question ${i + 1} does not have an answer. Please answer all questions before submitting.`);
          if (textarea) textarea.focus();
          return false;
        }
      }

      // Display loading state on submit button
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner">⏳</span> Evaluating Answers with NLP Engine...';
      }
    });
  }

  // Initialize first view
  updateView();
}

/* ================= RESULT CHARTS (Chart.js) ================= */
function renderResultCharts(radarData, barData) {
  if (typeof Chart === 'undefined') {
    console.warn('Chart.js is not loaded.');
    return;
  }

  // 1. Radar Chart (5 NLP Evaluation Dimensions)
  const radarCtx = document.getElementById('radarChart');
  if (radarCtx && radarData) {
    new Chart(radarCtx, {
      type: 'radar',
      data: {
        labels: ['Relevance', 'Keywords', 'Similarity', 'Completeness', 'Grammar'],
        datasets: [{
          label: 'Candidate NLP Scores (%)',
          data: [
            radarData.relevance || 0,
            radarData.keywords || 0,
            radarData.similarity || 0,
            radarData.completeness || 0,
            radarData.grammar || 0
          ],
          backgroundColor: 'rgba(99, 102, 241, 0.25)',
          borderColor: '#6366f1',
          pointBackgroundColor: '#06b6d4',
          pointBorderColor: '#ffffff',
          pointHoverBackgroundColor: '#ffffff',
          pointHoverBorderColor: '#6366f1',
          borderWidth: 2,
          pointRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
            grid: { color: 'rgba(255, 255, 255, 0.08)' },
            pointLabels: {
              color: '#cbd5e1',
              font: { size: 12, family: "'Plus Jakarta Sans', sans-serif", weight: '600' }
            },
            ticks: {
              backdropColor: 'transparent',
              color: '#94a3b8',
              stepSize: 20,
              min: 0,
              max: 100
            },
            suggestedMin: 0,
            suggestedMax: 100
          }
        },
        plugins: {
          legend: {
            display: false
          }
        }
      }
    });
  }

  // 2. Bar Chart (Question-wise Scores)
  const barCtx = document.getElementById('questionBarChart');
  if (barCtx && barData) {
    const labels = barData.map((_, i) => `Question ${i + 1}`);
    const scores = barData.map(item => item.score);

    new Chart(barCtx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Final Score',
          data: scores,
          backgroundColor: scores.map(s => {
            if (s >= 80) return 'rgba(16, 185, 129, 0.7)';
            if (s >= 70) return 'rgba(99, 102, 241, 0.7)';
            if (s >= 60) return 'rgba(245, 158, 11, 0.7)';
            return 'rgba(239, 68, 68, 0.7)';
          }),
          borderColor: scores.map(s => {
            if (s >= 80) return '#10b981';
            if (s >= 70) return '#6366f1';
            if (s >= 60) return '#f59e0b';
            return '#ef4444';
          }),
          borderWidth: 1.5,
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            min: 0,
            max: 100,
            grid: { color: 'rgba(255, 255, 255, 0.08)' },
            ticks: { color: '#94a3b8', stepSize: 20 }
          },
          x: {
            grid: { display: false },
            ticks: { color: '#cbd5e1', font: { weight: '600' } }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }
}

/* ================= HISTORY SEARCH & FILTER ================= */
function initHistorySearch() {
  const searchInput = document.getElementById('historySearch');
  const roleFilter = document.getElementById('historyRoleFilter');
  const rows = document.querySelectorAll('.history-row');

  if (!rows.length) return;

  function filterTable() {
    const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
    const selectedRole = roleFilter ? roleFilter.value.toLowerCase().trim() : '';

    rows.forEach(row => {
      const name = row.getAttribute('data-candidate')?.toLowerCase() || '';
      const email = row.getAttribute('data-email')?.toLowerCase() || '';
      const role = row.getAttribute('data-role')?.toLowerCase() || '';

      const matchesSearch = !query || name.includes(query) || email.includes(query);
      const matchesRole = !selectedRole || role === selectedRole;

      if (matchesSearch && matchesRole) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    });
  }

  if (searchInput) searchInput.addEventListener('input', filterTable);
  if (roleFilter) roleFilter.addEventListener('change', filterTable);
}
