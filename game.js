/* ============================================================
   IMAGE RECOGNITION: THE GAME
   Game Logic, Computer Vision Metrics, Hotspots & Audio Engine
   ============================================================ */

(function () {
  'use strict';

  // --- AUDIO SYNTHESIS (Web Audio API) ---
  class SoundEngine {
    constructor() {
      this.ctx = null;
      this.enabled = true;
    }

    init() {
      if (!this.ctx) {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) {
          this.ctx = new AudioContext();
        }
      }
      if (this.ctx && this.ctx.state === 'suspended') {
        this.ctx.resume();
      }
    }

    toggle() {
      this.enabled = !this.enabled;
      return this.enabled;
    }

    playCorrect() {
      if (!this.enabled || !this.ctx) return;
      this.init();
      const now = this.ctx.currentTime;
      // Arpeggio C5 -> E5 -> G5
      const notes = [523.25, 659.25, 783.99];
      notes.forEach((freq, idx) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, now + idx * 0.08);

        gain.gain.setValueAtTime(0.001, now + idx * 0.08);
        gain.gain.exponentialRampToValueAtTime(0.25, now + idx * 0.08 + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + idx * 0.08 + 0.25);

        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now + idx * 0.08);
        osc.stop(now + idx * 0.08 + 0.28);
      });
    }

    playError() {
      if (!this.enabled || !this.ctx) return;
      this.init();
      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(160, now);
      osc.frequency.exponentialRampToValueAtTime(90, now + 0.22);

      gain.gain.setValueAtTime(0.3, now);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.24);

      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(now);
      osc.stop(now + 0.25);
    }

    playTick() {
      if (!this.enabled || !this.ctx) return;
      this.init();
      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'triangle';
      osc.frequency.setValueAtTime(800, now);

      gain.gain.setValueAtTime(0.12, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.05);

      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(now);
      osc.stop(now + 0.06);
    }

    playWin() {
      if (!this.enabled || !this.ctx) return;
      this.init();
      const now = this.ctx.currentTime;
      const freqs = [523.25, 659.25, 783.99, 1046.5];
      freqs.forEach((freq, idx) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(freq, now + idx * 0.09);

        gain.gain.setValueAtTime(0.2, now + idx * 0.09);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + idx * 0.09 + 0.4);

        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now + idx * 0.09);
        osc.stop(now + idx * 0.09 + 0.45);
      });
    }
  }

  // --- GAME STATE ---
  const state = {
    rounds: [],
    currentRoundIndex: 0,
    roundData: null,
    timeRemaining: 10.0,
    timerMax: 10.0,
    timerInterval: null,
    isPlaying: false,
    score: 0,
    roundScore: 0,
    tp: 0,
    fp: 0,
    fn: 0,
    totalFound: 0,
    totalTargets: 0,
    foundIndices: new Set(),
    history: []
  };

  const audio = new SoundEngine();

  // --- DOM ELEMENTS ---
  const $ = (id) => document.getElementById(id);

  const el = {
    app: $('app'),
    btnSound: $('btn-sound'),
    soundIcon: $('sound-icon'),
    btnRestartNav: $('btn-restart-nav'),
    roundIndicator: $('round-indicator'),
    missionText: $('mission-text'),
    missionSubtext: $('mission-subtext'),
    timerDisplay: $('timer-display'),
    timerBar: $('timer-bar'),
    scoreDisplay: $('score-display'),
    foundDisplay: $('found-display'),
    coolerContainer: $('cooler-container'),
    fridgeImg: $('fridge-img'),
    hotspotsOverlay: $('hotspots-overlay'),
    feedbackOverlay: $('feedback-overlay'),
    // Modals
    modalStart: $('modal-start'),
    btnStartGame: $('btn-start-game'),
    modalRoundResults: $('modal-round-results'),
    roundResultBadge: $('round-result-badge'),
    roundResultTitle: $('round-result-title'),
    roundResultSub: $('round-result-sub'),
    metricPrecision: $('metric-precision'),
    metricRecall: $('metric-recall'),
    metricAccuracy: $('metric-accuracy'),
    statTp: $('stat-tp'),
    statFp: $('stat-fp'),
    statFn: $('stat-fn'),
    statTimeBonus: $('stat-time-bonus'),
    statRoundScore: $('stat-round-score'),
    btnNextRound: $('btn-next-round'),
    modalFinalBenchmark: $('modal-final-benchmark'),
    finalRankTitle: $('final-rank-title'),
    finalRankDesc: $('final-rank-desc'),
    finalPrecision: $('final-precision'),
    finalRecall: $('final-recall'),
    finalAccuracy: $('final-accuracy'),
    finalTotalScore: $('final-total-score'),
    btnPlayAgain: $('btn-play-again')
  };

  // --- INITIALIZATION & DATA LOADING ---
  async function init() {
    try {
      const resp = await fetch('hotspots.json');
      if (!resp.ok) throw new Error('No se pudo cargar hotspots.json');
      const data = await resp.json();
      state.rounds = [data.round1, data.round2, data.round3, data.round4];
    } catch (err) {
      console.error('Error cargando datos:', err);
    }

    setupEventListeners();
  }

  function setupEventListeners() {
    el.btnSound.addEventListener('click', () => {
      audio.init();
      const enabled = audio.toggle();
      el.soundIcon.textContent = enabled ? '🔊' : '🔇';
    });

    el.btnRestartNav.addEventListener('click', () => {
      audio.init();
      resetGame();
    });

    el.btnStartGame.addEventListener('click', () => {
      audio.init();
      el.modalStart.classList.add('hidden');
      startRound(0);
    });

    el.btnNextRound.addEventListener('click', () => {
      audio.init();
      el.modalRoundResults.classList.add('hidden');
      if (state.currentRoundIndex + 1 < state.rounds.length) {
        startRound(state.currentRoundIndex + 1);
      } else {
        showFinalBenchmark();
      }
    });

    el.btnPlayAgain.addEventListener('click', () => {
      audio.init();
      el.modalFinalBenchmark.classList.add('hidden');
      resetGame();
      startRound(0);
    });
  }

  function resetGame() {
    clearInterval(state.timerInterval);
    state.currentRoundIndex = 0;
    state.score = 0;
    state.history = [];
    state.isPlaying = false;
    updateSidebarUI();
  }

  // --- START ROUND ---
  function startRound(roundIdx) {
    state.currentRoundIndex = roundIdx;
    state.roundData = state.rounds[roundIdx];
    state.timeRemaining = state.roundData.time;
    state.timerMax = state.roundData.time;
    state.roundScore = 0;
    state.tp = 0;
    state.fp = 0;
    state.fn = 0;
    state.totalFound = 0;
    state.foundIndices.clear();
    state.totalTargets = state.roundData.target_count;
    state.isPlaying = true;

    // Preload image & build hotspots
    el.fridgeImg.src = state.roundData.image;
    renderHotspots();
    updateSidebarUI();

    // Start timer loop
    clearInterval(state.timerInterval);
    const stepMs = 50; // 20 updates per second for smooth bar
    let lastTickSecond = Math.ceil(state.timeRemaining);

    state.timerInterval = setInterval(() => {
      if (!state.isPlaying) return;

      state.timeRemaining = Math.max(0, state.timeRemaining - (stepMs / 1000));
      updateTimerUI();

      // Audio tick during last 3 seconds
      const currentSec = Math.ceil(state.timeRemaining);
      if (currentSec <= 3 && currentSec > 0 && currentSec !== lastTickSecond) {
        audio.playTick();
        lastTickSecond = currentSec;
      }

      if (state.timeRemaining <= 0) {
        finishRound(false);
      }
    }, stepMs);
  }

  // --- RENDER HOTSPOTS ---
  function renderHotspots() {
    el.hotspotsOverlay.innerHTML = '';
    el.feedbackOverlay.innerHTML = '';

    state.roundData.hotspots.forEach((h, idx) => {
      const box = document.createElement('div');
      box.className = 'hotspot-box';
      box.style.left = `${h.x}%`;
      box.style.top = `${h.y}%`;
      box.style.width = `${h.width}%`;
      box.style.height = `${h.height}%`;
      box.dataset.index = idx;
      box.dataset.target = h.target;
      box.title = ''; // Never reveal name beforehand

      box.addEventListener('click', (e) => handleHotspotClick(e, h, idx, box));
      el.hotspotsOverlay.appendChild(box);
    });
  }

  // --- HANDLE HOTSPOT CLICK ---
  function handleHotspotClick(e, hotspot, idx, boxEl) {
    if (!state.isPlaying) return;

    // Click position relative to cooler container for floating pill
    const rect = el.coolerContainer.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const clickY = e.clientY - rect.top;

    if (hotspot.target) {
      // Already found check
      if (state.foundIndices.has(idx)) return;

      state.foundIndices.add(idx);
      state.tp++;
      state.totalFound++;
      state.score += 100;
      state.roundScore += 100;

      boxEl.classList.add('target-hit');
      audio.playCorrect();
      showFloatingPill(clickX, clickY, '+100', 'Correcto', 'correct');
      updateSidebarUI();

      // Check win condition (all targets found)
      if (state.totalFound >= state.totalTargets) {
        finishRound(true);
      }
    } else {
      // False Positive (Distractor)
      state.fp++;
      state.score = Math.max(0, state.score - 50);
      state.roundScore -= 50;

      boxEl.classList.remove('distractor-hit');
      // Trigger reflow to restart shake animation
      void boxEl.offsetWidth;
      boxEl.classList.add('distractor-hit');

      audio.playError();
      const distractorLabel = hotspot.distractor_label || 'Falso positivo';
      showFloatingPill(clickX, clickY, '−50', distractorLabel, 'incorrect');
      updateSidebarUI();

      setTimeout(() => {
        boxEl.classList.remove('distractor-hit');
      }, 500);
    }
  }

  // --- FLOATING FEEDBACK PILL ---
  function showFloatingPill(x, y, pts, label, typeClass) {
    const pill = document.createElement('div');
    pill.className = `floating-pill ${typeClass}`;
    pill.style.left = `${x}px`;
    pill.style.top = `${y}px`;
    pill.innerHTML = `<span class="pts">${pts}</span><span class="lbl">${label}</span>`;
    el.feedbackOverlay.appendChild(pill);

    setTimeout(() => {
      pill.remove();
    }, 750);
  }

  // --- UPDATE UI ELEMENTS ---
  function updateSidebarUI() {
    if (!state.roundData) return;

    el.roundIndicator.textContent = `RONDA ${state.roundData.id} / ${state.rounds.length}`;
    el.missionText.textContent = state.roundData.mission;
    el.missionSubtext.textContent = state.roundData.subtext;
    el.scoreDisplay.textContent = state.score;
    el.foundDisplay.textContent = `${state.totalFound} / ${state.totalTargets}`;
  }

  function updateTimerUI() {
    el.timerDisplay.textContent = `${state.timeRemaining.toFixed(1)} s`;
    const pct = Math.max(0, Math.min(100, (state.timeRemaining / state.timerMax) * 100));
    el.timerBar.style.width = `${pct}%`;

    if (state.timeRemaining <= 3.0) {
      el.timerBar.classList.add('urgent');
      el.timerDisplay.style.color = '#ff0033';
    } else {
      el.timerBar.classList.remove('urgent');
      el.timerDisplay.style.color = 'var(--color-red)';
    }
  }

  // --- FINISH ROUND ---
  function finishRound(completedAll) {
    if (!state.isPlaying) return;
    state.isPlaying = false;
    clearInterval(state.timerInterval);

    // Calculate False Negatives (targets missed)
    state.fn = Math.max(0, state.totalTargets - state.tp);
    const missedPenalty = state.fn * 25;
    state.score = Math.max(0, state.score - missedPenalty);
    state.roundScore -= missedPenalty;

    // Time Bonus if finished early
    let timeBonus = 0;
    if (completedAll && state.timeRemaining > 0) {
      timeBonus = Math.round(state.timeRemaining * 20);
      state.score += timeBonus;
      state.roundScore += timeBonus;
      audio.playWin();
    }

    updateSidebarUI();

    // Calculate Computer Vision Metrics
    // Precision = TP / (TP + FP)
    const precisionVal = (state.tp + state.fp > 0) ? (state.tp / (state.tp + state.fp)) * 100 : (state.tp > 0 ? 100 : 0);
    // Recall = TP / (TP + FN)
    const recallVal = (state.tp + state.fn > 0) ? (state.tp / (state.tp + state.fn)) * 100 : 0;
    // Accuracy = TP / (TP + FP + FN)
    const accuracyVal = (state.tp + state.fp + state.fn > 0) ? (state.tp / (state.tp + state.fp + state.fn)) * 100 : 0;

    // Save history
    state.history.push({
      round: state.roundData.id,
      tp: state.tp,
      fp: state.fp,
      fn: state.fn,
      timeBonus: timeBonus,
      roundScore: state.roundScore,
      precision: precisionVal,
      recall: recallVal,
      accuracy: accuracyVal
    });

    // Reveal unclicked targets with subtle yellow outline
    state.roundData.hotspots.forEach((h, idx) => {
      if (h.target && !state.foundIndices.has(idx)) {
        const box = el.hotspotsOverlay.children[idx];
        if (box) {
          box.style.border = '2px dashed var(--color-yellow)';
          box.style.background = 'rgba(245, 158, 11, 0.15)';
        }
      }
    });

    // Show round modal after brief pause
    setTimeout(() => {
      showRoundResults(precisionVal, recallVal, accuracyVal, timeBonus, completedAll);
    }, 700);
  }

  // --- SHOW ROUND RESULTS MODAL ---
  function showRoundResults(precision, recall, accuracy, timeBonus, completedAll) {
    if (completedAll) {
      el.roundResultBadge.textContent = '¡OBJETIVO CUMPLIDO!';
      el.roundResultBadge.className = 'modal-badge-success';
    } else {
      el.roundResultBadge.textContent = 'TIEMPO AGOTADO';
      el.roundResultBadge.className = 'modal-badge';
    }

    el.roundResultTitle.textContent = `RESULTADOS — RONDA ${state.roundData.id}`;
    el.roundResultSub.textContent = state.roundData.mission;

    el.metricPrecision.textContent = `${precision.toFixed(1)}%`;
    el.metricRecall.textContent = `${recall.toFixed(1)}%`;
    el.metricAccuracy.textContent = `${accuracy.toFixed(1)}%`;

    el.statTp.textContent = `${state.tp} (+${state.tp * 100} pts)`;
    el.statFp.textContent = `${state.fp} (−${state.fp * 50} pts)`;
    el.statFn.textContent = `${state.fn} (−${state.fn * 25} pts)`;
    el.statTimeBonus.textContent = timeBonus > 0 ? `+${timeBonus} pts` : '0 pts';
    el.statRoundScore.textContent = `${state.score} pts`;

    if (state.currentRoundIndex + 1 < state.rounds.length) {
      el.btnNextRound.textContent = `CONTINUAR A LA RONDA ${state.currentRoundIndex + 2}`;
    } else {
      el.btnNextRound.textContent = 'VER HUMAN BENCHMARK FINAL';
    }

    el.modalRoundResults.classList.remove('hidden');
  }

  // --- SHOW FINAL BENCHMARK SCREEN ---
  function showFinalBenchmark() {
    let sumTp = 0, sumFp = 0, sumFn = 0;
    state.history.forEach(h => {
      sumTp += h.tp;
      sumFp += h.fp;
      sumFn += h.fn;
    });

    const globalPrecision = (sumTp + sumFp > 0) ? (sumTp / (sumTp + sumFp)) * 100 : 0;
    const globalRecall = (sumTp + sumFn > 0) ? (sumTp / (sumTp + sumFn)) * 100 : 0;
    const globalAccuracy = (sumTp + sumFp + sumFn > 0) ? (sumTp / (sumTp + sumFp + sumFn)) * 100 : 0;

    el.finalPrecision.textContent = `${globalPrecision.toFixed(1)}%`;
    el.finalRecall.textContent = `${globalRecall.toFixed(1)}%`;
    el.finalAccuracy.textContent = `${globalAccuracy.toFixed(1)}%`;
    el.finalTotalScore.textContent = `${state.score} PTS`;

    // Ranking Logic
    let rankTitle = 'Shelf Scanner';
    let rankDesc = 'Fácilmente distraído por empaques secundarios y variantes. Requiere mayor calibración visual.';

    if (state.score >= 1400 && globalPrecision >= 85) {
      rankTitle = 'Human Vision Engine';
      rankDesc = 'Rendimiento sobrehumano. Identificación visual precisa de catálogo bajo estrés extremo y condensación.';
    } else if (state.score >= 950 && globalPrecision >= 75) {
      rankTitle = 'Vision Operator';
      rankDesc = 'Rendimiento profesional de auditor de anaquel. Excelente balance entre velocidad de escaneo y precisión.';
    } else if (state.score >= 500) {
      rankTitle = 'Sharp Observer';
      rankDesc = 'Buena agudeza visual. Se detecta dificultad para discriminar empaques bajo presión de tiempo.';
    }

    el.finalRankTitle.textContent = rankTitle;
    el.finalRankDesc.textContent = rankDesc;

    el.modalFinalBenchmark.classList.remove('hidden');
    audio.playWin();
  }

  // Auto-init on page load
  document.addEventListener('DOMContentLoaded', init);

})();
