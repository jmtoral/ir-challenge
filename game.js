/* ============================================================
   IMAGE RECOGNITION: THE GAME
   Game Logic, Computer Vision Metrics, Hotspots & Audio Engine
   ============================================================ */

(function () {
  'use strict';

  // --- CONFIGURACIÓN & LEADERBOARD CLOUD ---
  const CONFIG = {
    leaderboard: {
      maxEntries: 10,
      apiUrl: '' // Coloca aquí la URL pública de tu Cloudflare Worker una vez desplegado
    }
  };
  const LB_STORAGE_KEY = 'ir_challenge_leaderboard_v1';
  const PLAYER_NAME_KEY = 'ir_challenge_player_name';

  // Seed data inicial offline (Top 5 inicial)
  const DEFAULT_LEADERBOARD = [
    { nombre: 'Master Auditor', puntos: 1950, precision: 100.0, recall: 100.0, accuracy: 100.0, rango: 'Human Vision Engine', fecha: '2026-09-01' },
    { nombre: 'Cyber Spotter', puntos: 1720, precision: 95.0, recall: 90.0, accuracy: 88.5, rango: 'Vision Operator', fecha: '2026-09-02' },
    { nombre: 'Tiendita Pro', puntos: 1480, precision: 88.0, recall: 85.0, accuracy: 80.0, rango: 'Sharp Observer', fecha: '2026-09-03' },
    { nombre: 'Cooler Scout', puntos: 1100, precision: 82.5, recall: 78.0, accuracy: 75.0, rango: 'Sharp Observer', fecha: '2026-09-04' },
    { nombre: 'Shelf Trainee', puntos: 750, precision: 72.0, recall: 65.0, accuracy: 60.0, rango: 'Shelf Scanner', fecha: '2026-09-05' }
  ];

  // --- LEADERBOARD LOGIC & CLOUD SYNC ---
  function getLocalLeaderboard() {
    try {
      const stored = localStorage.getItem(LB_STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed) && parsed.length > 0) return parsed;
      }
    } catch (e) {
      console.warn('Error leyendo leaderboard local:', e);
    }
    return [...DEFAULT_LEADERBOARD];
  }

  function saveLocalLeaderboard(list) {
    try {
      localStorage.setItem(LB_STORAGE_KEY, JSON.stringify(list.slice(0, 50)));
    } catch (e) {
      console.warn('Error guardando leaderboard local:', e);
    }
  }

  async function fetchCloudLeaderboard() {
    if (!CONFIG.leaderboard.apiUrl) return null;
    try {
      const url = CONFIG.leaderboard.apiUrl.replace(/\/$/, '') + '/api/leaderboard';
      const resp = await fetch(url, { method: 'GET', headers: { Accept: 'application/json' } });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      if (Array.isArray(data)) {
        saveLocalLeaderboard(data);
        return data;
      }
    } catch (err) {
      console.warn('Cloudflare Leaderboard offline o inalcanzable:', err);
    }
    return null;
  }

  async function submitScoreToLeaderboard(entry) {
    const list = getLocalLeaderboard();
    list.push(entry);
    list.sort((a, b) => {
      if ((b.puntos || 0) !== (a.puntos || 0)) return (b.puntos || 0) - (a.puntos || 0);
      if ((b.precision || 0) !== (a.precision || 0)) return (b.precision || 0) - (a.precision || 0);
      return (b.recall || 0) - (a.recall || 0);
    });
    const top = list.slice(0, 50);
    saveLocalLeaderboard(top);

    if (CONFIG.leaderboard.apiUrl) {
      try {
        const url = CONFIG.leaderboard.apiUrl.replace(/\/$/, '') + '/api/score';
        const resp = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          body: JSON.stringify({
            nombre: entry.nombre,
            puntos: entry.puntos,
            precision: entry.precision,
            recall: entry.recall,
            accuracy: entry.accuracy,
            rango: entry.rango,
            fecha: entry.fecha
          })
        });
        if (resp.ok) {
          const cloudTop = await resp.json();
          if (Array.isArray(cloudTop)) {
            const mapped = cloudTop.map(item => {
              if (item.nombre === entry.nombre && item.puntos === entry.puntos) {
                return { ...item, _fresh: true };
              }
              return item;
            });
            saveLocalLeaderboard(mapped);
            return mapped;
          }
        }
      } catch (err) {
        console.warn('Error enviando puntaje a Cloudflare Worker:', err);
      }
    }
    return top;
  }

  function renderLeaderboard(containerId, highlightName, statusElementId) {
    const container = $(containerId);
    if (!container) return;

    const list = getLocalLeaderboard().slice(0, CONFIG.leaderboard.maxEntries);
    const isCloudConfigured = Boolean(CONFIG.leaderboard.apiUrl);

    if (statusElementId) {
      const statusEl = $(statusElementId);
      if (statusEl) {
        if (isCloudConfigured) {
          statusEl.textContent = '🟢 CLOUD SYNC';
          statusEl.className = 'lb-status-pill is-online';
        } else {
          statusEl.textContent = '🟡 OFFLINE / LOCAL';
          statusEl.className = 'lb-status-pill is-offline';
        }
      }
    }

    let html = `
      <table class="leaderboard-table">
        <thead>
          <tr>
            <th class="lb-pos">#</th>
            <th>AUDITOR</th>
            <th>SCORE</th>
            <th>PRECISION</th>
            <th>RANGO</th>
            <th>FECHA</th>
          </tr>
        </thead>
        <tbody>
    `;

    list.forEach((item, index) => {
      const pos = index + 1;
      const isFresh = Boolean(item._fresh);
      const isMe = highlightName && String(item.nombre).toLowerCase() === String(highlightName).toLowerCase();
      const rowClass = isFresh ? 'lb-row-fresh' : (isMe ? 'lb-row-me' : '');

      let posBadgeClass = '';
      if (pos === 1) posBadgeClass = 'lb-pos-1';
      else if (pos === 2) posBadgeClass = 'lb-pos-2';
      else if (pos === 3) posBadgeClass = 'lb-pos-3';

      let rankClass = 'lb-rank-scanner';
      if (item.rango === 'Human Vision Engine') rankClass = 'lb-rank-engine';
      else if (item.rango === 'Vision Operator') rankClass = 'lb-rank-operator';
      else if (item.rango === 'Sharp Observer') rankClass = 'lb-rank-observer';

      html += `
        <tr class="${rowClass}">
          <td class="lb-pos">
            <span class="lb-pos-badge ${posBadgeClass}">${pos}</span>
          </td>
          <td><strong>${escapeHtml(item.nombre)}</strong></td>
          <td><span class="lb-score-val">${item.puntos}</span></td>
          <td>${(item.precision !== undefined ? Number(item.precision).toFixed(1) : '—')}%</td>
          <td><span class="lb-rank-tag ${rankClass}">${escapeHtml(item.rango || 'Scanner')}</span></td>
          <td style="color:#666; font-size:0.75rem;">${escapeHtml(item.fecha || '')}</td>
        </tr>
      `;
    });

    html += `
        </tbody>
      </table>
    `;

    container.innerHTML = html;
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
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

    playGo() {
      if (!this.enabled || !this.ctx) return;
      this.init();
      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(1046.5, now);
      gain.gain.setValueAtTime(0.2, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.18);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(now);
      osc.stop(now + 0.2);
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

  // --- BACKGROUND MUSIC ENGINE & PLAYLIST ---
  const PLAYLIST = [
    {
      id: 'boss',
      name: 'TRACK 1: BOSS',
      fullName: 'Final Boss Battle',
      src: 'assets/audio/final_boss_battle.mp3',
      fallback: 'assets/audio/final_boss_battle.mp3'
    },
    {
      id: 'arcade',
      name: 'TRACK 2: ARCADE',
      fullName: 'Playful Retro Arcade',
      src: 'assets/audio/playful_retro_arcade.mp3',
      fallback: 'assets/audio/playful_retro_arcade.mp3'
    }
  ];

  class MusicPlayer {
    constructor(playlist) {
      this.playlist = playlist;
      this.currentIndex = 0;
      this.isPausedByUser = false;
      this.fallbackAttempted = false;

      this.audio = new Audio(this.currentTrack.src);
      this.audio.loop = true;
      this.audio.volume = 0.35;

      this.setupAudioListeners();
    }

    get currentTrack() {
      return this.playlist[this.currentIndex];
    }

    setupAudioListeners() {
      this.audio.addEventListener('error', () => {
        if (!this.fallbackAttempted && this.currentTrack.fallback) {
          this.fallbackAttempted = true;
          this.audio.src = this.currentTrack.fallback;
          this.audio.load();
          if (!this.isPausedByUser) {
            this.audio.play().catch(() => {});
          }
        }
      });
    }

    loadCurrentTrack(autoPlay = true) {
      this.fallbackAttempted = false;
      this.audio.src = this.currentTrack.src;
      this.audio.load();
      if (autoPlay && !this.isPausedByUser) {
        this.play();
      }
    }

    nextTrack() {
      this.currentIndex = (this.currentIndex + 1) % this.playlist.length;
      const wasPlaying = !this.audio.paused;
      this.loadCurrentTrack(wasPlaying || !this.isPausedByUser);
      return this.currentTrack;
    }

    play() {
      if (this.isPausedByUser) return;
      const promise = this.audio.play();
      if (promise !== undefined) {
        promise.catch((err) => {
          console.log('Background music deferred until interaction:', err);
        });
      }
    }

    pause() {
      this.audio.pause();
    }

    toggle() {
      if (this.audio.paused) {
        this.isPausedByUser = false;
        this.play();
      } else {
        this.isPausedByUser = true;
        this.pause();
      }
      return !this.audio.paused;
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
    countdownTimerId: null,
    isCountdownActive: false,
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
  const music = new MusicPlayer(PLAYLIST);

  // --- DOM ELEMENTS ---
  const $ = (id) => document.getElementById(id);

  const el = {
    app: $('app'),
    btnMusic: $('btn-music'),
    musicIcon: $('music-icon'),
    btnMusicNext: $('btn-music-next'),
    musicTrackTitle: $('music-track-title'),
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
    // Countdown Overlay Elements
    countdownOverlay: $('countdown-overlay'),
    countdownRoundBadge: $('countdown-round-badge'),
    countdownMissionTitle: $('countdown-mission-title'),
    countdownMissionDesc: $('countdown-mission-desc'),
    countdownTimerCircle: $('countdown-timer-circle'),
    countdownNumber: $('countdown-number'),
    btnSkipCountdown: $('btn-skip-countdown'),
    // Modals
    modalStart: $('modal-start'),
    inputPlayerName: $('input-player-name'),
    btnViewLbStart: $('btn-view-lb-start'),
    btnStartGame: $('btn-start-game'),
    btnLeaderboardNav: $('btn-leaderboard-nav'),
    modalLeaderboard: $('modal-leaderboard'),
    modalLbStatus: $('modal-lb-status'),
    globalLbContainer: $('global-leaderboard-container'),
    btnCloseLeaderboard: $('btn-close-leaderboard'),
    btnRefreshLeaderboard: $('btn-refresh-leaderboard'),
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
    benchmarkLbContainer: $('benchmark-leaderboard-container'),
    benchmarkLbStatus: $('benchmark-lb-status'),
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

    // Cargar nombre de auditor previo si existe
    try {
      const savedName = localStorage.getItem(PLAYER_NAME_KEY);
      if (savedName && el.inputPlayerName) {
        el.inputPlayerName.value = savedName;
      }
    } catch (e) {}

    // Sincronización en la nube si hay API configurada
    if (CONFIG.leaderboard.apiUrl) {
      fetchCloudLeaderboard().catch(() => {});
    }

    updateMusicTrackDisplay(music.currentTrack);
    updateMusicButton(!music.audio.paused);
    setupEventListeners();
  }

  function updateMusicTrackDisplay(track) {
    if (!el.musicTrackTitle || !track) return;
    el.musicTrackTitle.textContent = track.name;
    el.musicTrackTitle.title = `Pista actual: ${track.fullName} (Click para cambiar a la siguiente)`;
  }

  function updateMusicButton(isPlaying) {
    if (!el.btnMusic || !el.musicIcon) return;
    if (isPlaying) {
      el.musicIcon.textContent = '🎵';
      el.btnMusic.title = 'Pausar música de fondo';
      el.btnMusic.classList.remove('is-paused');
    } else {
      el.musicIcon.textContent = '⏸️';
      el.btnMusic.title = 'Reanudar música de fondo';
      el.btnMusic.classList.add('is-paused');
    }
  }

  function setupEventListeners() {
    // Guardar nombre al escribir
    if (el.inputPlayerName) {
      el.inputPlayerName.addEventListener('input', (e) => {
        const val = e.target.value.trim();
        if (val) {
          try { localStorage.setItem(PLAYER_NAME_KEY, val); } catch (err) {}
        }
      });
    }

    // Modal Leaderboard (apertura y cierre)
    function openLeaderboardModal() {
      audio.init();
      if (!el.modalLeaderboard) return;
      const curName = el.inputPlayerName ? el.inputPlayerName.value.trim() : '';
      renderLeaderboard('global-leaderboard-container', curName, 'modal-lb-status');
      el.modalLeaderboard.classList.remove('hidden');

      if (CONFIG.leaderboard.apiUrl) {
        fetchCloudLeaderboard().then(() => {
          renderLeaderboard('global-leaderboard-container', curName, 'modal-lb-status');
        });
      }
    }

    if (el.btnLeaderboardNav) {
      el.btnLeaderboardNav.addEventListener('click', openLeaderboardModal);
    }
    if (el.btnViewLbStart) {
      el.btnViewLbStart.addEventListener('click', openLeaderboardModal);
    }
    if (el.btnCloseLeaderboard) {
      el.btnCloseLeaderboard.addEventListener('click', () => {
        audio.init();
        if (el.modalLeaderboard) el.modalLeaderboard.classList.add('hidden');
      });
    }
    if (el.btnRefreshLeaderboard) {
      el.btnRefreshLeaderboard.addEventListener('click', async () => {
        audio.init();
        const curName = el.inputPlayerName ? el.inputPlayerName.value.trim() : '';
        if (CONFIG.leaderboard.apiUrl) {
          await fetchCloudLeaderboard();
        }
        renderLeaderboard('global-leaderboard-container', curName, 'modal-lb-status');
      });
    }

    el.btnMusic.addEventListener('click', () => {
      audio.init();
      const isPlaying = music.toggle();
      updateMusicButton(isPlaying);
    });

    if (el.btnMusicNext) {
      el.btnMusicNext.addEventListener('click', () => {
        audio.init();
        const track = music.nextTrack();
        updateMusicTrackDisplay(track);
        updateMusicButton(!music.audio.paused);
      });
    }

    if (el.musicTrackTitle) {
      el.musicTrackTitle.addEventListener('click', () => {
        audio.init();
        const track = music.nextTrack();
        updateMusicTrackDisplay(track);
        updateMusicButton(!music.audio.paused);
      });
    }

    el.btnSound.addEventListener('click', () => {
      audio.init();
      const enabled = audio.toggle();
      el.soundIcon.textContent = enabled ? '🔊' : '🔇';
      el.btnSound.title = enabled ? 'Silenciar efectos de sonido' : 'Activar efectos de sonido';
    });

    el.btnRestartNav.addEventListener('click', () => {
      audio.init();
      music.play();
      updateMusicButton(!music.audio.paused);
      resetGame();
    });

    el.btnStartGame.addEventListener('click', () => {
      audio.init();
      music.play();
      updateMusicButton(!music.audio.paused);
      el.modalStart.classList.add('hidden');
      startRound(0);
    });

    el.btnNextRound.addEventListener('click', () => {
      audio.init();
      music.play();
      updateMusicButton(!music.audio.paused);
      el.modalRoundResults.classList.add('hidden');
      if (state.currentRoundIndex + 1 < state.rounds.length) {
        startRound(state.currentRoundIndex + 1);
      } else {
        showFinalBenchmark();
      }
    });

    el.btnPlayAgain.addEventListener('click', () => {
      audio.init();
      music.play();
      updateMusicButton(!music.audio.paused);
      el.modalFinalBenchmark.classList.add('hidden');
      resetGame();
      startRound(0);
    });

    if (el.btnSkipCountdown) {
      el.btnSkipCountdown.addEventListener('click', () => {
        audio.init();
        if (state.isCountdownActive) {
          finishCountdownAndStart();
        }
      });
    }

    document.addEventListener('keydown', (e) => {
      if (e.code === 'Space' && state.isCountdownActive) {
        e.preventDefault();
        audio.init();
        finishCountdownAndStart();
      }
    });

    // Desbloquear audio e iniciar música en primera interacción de usuario
    document.addEventListener('click', () => {
      audio.init();
      if (!music.isPausedByUser && music.audio.paused) {
        music.play();
        updateMusicButton(true);
      }
    }, { once: true });
  }

  function resetGame() {
    clearInterval(state.timerInterval);
    if (state.countdownTimerId) {
      clearTimeout(state.countdownTimerId);
      state.countdownTimerId = null;
    }
    state.isCountdownActive = false;
    if (el.countdownOverlay) {
      el.countdownOverlay.classList.add('hidden');
    }
    state.currentRoundIndex = 0;
    state.score = 0;
    state.history = [];
    state.isPlaying = false;
    updateSidebarUI();
  }

  // --- START ROUND WITH 3-SECOND PREPARATION COUNTDOWN ---
  function startRound(roundIdx) {
    clearInterval(state.timerInterval);
    if (state.countdownTimerId) {
      clearTimeout(state.countdownTimerId);
      state.countdownTimerId = null;
    }

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
    state.isPlaying = false; // Hotspots bloqueados durante la lectura de instrucciones
    state.isCountdownActive = true;

    // Precargar imagen y construir hotspots (invisibles y bloqueados)
    el.fridgeImg.src = state.roundData.image;
    renderHotspots();
    updateSidebarUI();

    // Actualizar datos en overlay de preparación
    if (el.countdownRoundBadge) {
      el.countdownRoundBadge.textContent = `RONDA ${roundIdx + 1} DE ${state.rounds.length} // PREPARACIÓN`;
    }
    if (el.countdownMissionTitle) {
      el.countdownMissionTitle.textContent = state.roundData.mission;
    }
    if (el.countdownMissionDesc) {
      el.countdownMissionDesc.textContent = state.roundData.subtext || 'Identifica rápidamente los objetivos de catálogo requeridos.';
    }

    // Resetear estilos del círculo de cuenta
    if (el.countdownTimerCircle) {
      el.countdownTimerCircle.classList.remove('is-go');
    }
    if (el.countdownNumber) {
      el.countdownNumber.classList.remove('is-go-text');
      el.countdownNumber.textContent = '3';
    }

    if (el.countdownOverlay) {
      el.countdownOverlay.classList.remove('hidden');
    }

    // Segundo 3
    audio.playTick();
    triggerCountdownPop();

    // Segundo 2 (tras 1000ms)
    state.countdownTimerId = setTimeout(() => {
      if (!state.isCountdownActive) return;
      if (el.countdownNumber) el.countdownNumber.textContent = '2';
      audio.playTick();
      triggerCountdownPop();

      // Segundo 1 (tras 2000ms)
      state.countdownTimerId = setTimeout(() => {
        if (!state.isCountdownActive) return;
        if (el.countdownNumber) el.countdownNumber.textContent = '1';
        audio.playTick();
        triggerCountdownPop();

        // ¡AUDITA! (tras 3000ms)
        state.countdownTimerId = setTimeout(() => {
          if (!state.isCountdownActive) return;
          if (el.countdownNumber) {
            el.countdownNumber.textContent = '¡AUDITA!';
            el.countdownNumber.classList.add('is-go-text');
          }
          if (el.countdownTimerCircle) {
            el.countdownTimerCircle.classList.add('is-go');
          }
          audio.playGo();
          triggerCountdownPop();

          // Transición suave al juego activo (350ms de flash de ¡AUDITA!)
          state.countdownTimerId = setTimeout(() => {
            finishCountdownAndStart();
          }, 350);
        }, 1000);
      }, 1000);
    }, 1000);
  }

  function triggerCountdownPop() {
    if (!el.countdownNumber) return;
    el.countdownNumber.classList.remove('pop-anim');
    void el.countdownNumber.offsetWidth; // Forzar reflujo CSS
    el.countdownNumber.classList.add('pop-anim');
  }

  function finishCountdownAndStart() {
    if (state.countdownTimerId) {
      clearTimeout(state.countdownTimerId);
      state.countdownTimerId = null;
    }
    state.isCountdownActive = false;
    if (el.countdownOverlay) {
      el.countdownOverlay.classList.add('hidden');
    }
    beginActiveTimer();
  }

  function beginActiveTimer() {
    state.isPlaying = true;

    // Iniciar bucle de cronómetro de ronda
    clearInterval(state.timerInterval);
    const stepMs = 50; // 20 actualizaciones por segundo
    let lastTickSecond = Math.ceil(state.timeRemaining);

    state.timerInterval = setInterval(() => {
      if (!state.isPlaying) return;

      state.timeRemaining = Math.max(0, state.timeRemaining - (stepMs / 1000));
      updateTimerUI();

      // Ticks de audio en los últimos 3 segundos
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

    // Registrar en Leaderboard y renderizar
    const rawName = el.inputPlayerName ? el.inputPlayerName.value.trim() : '';
    const playerName = rawName || 'Auditor Pop';
    try {
      localStorage.setItem(PLAYER_NAME_KEY, playerName);
    } catch (e) {}

    const scoreEntry = {
      nombre: playerName,
      puntos: state.score,
      precision: parseFloat(globalPrecision.toFixed(1)),
      recall: parseFloat(globalRecall.toFixed(1)),
      accuracy: parseFloat(globalAccuracy.toFixed(1)),
      rango: rankTitle,
      fecha: new Date().toISOString().slice(0, 10),
      _fresh: true
    };

    // Render inmediato local
    renderLeaderboard('benchmark-leaderboard-container', playerName, 'benchmark-lb-status');

    // Enviar a la nube y actualizar
    submitScoreToLeaderboard(scoreEntry).then(() => {
      renderLeaderboard('benchmark-leaderboard-container', playerName, 'benchmark-lb-status');
    });

    el.modalFinalBenchmark.classList.remove('hidden');
    audio.playWin();
  }

  // Auto-init on page load
  document.addEventListener('DOMContentLoaded', init);

})();
