/* Versioned, privacy-minimal local progress storage. No free-text answers or audio are stored. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.EnglishPersistence = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const STORAGE_KEY = 'english-professor-state-v1';
  const LEGACY_KEYS = [
    'english-professor-position',
    'english-professor-result',
    'english-professor-result-unit-0',
    'english-professor-result-unit-1',
    'english-professor-result-unit-2',
    'english-professor-result-unit-3'
  ];

  function defaultState() {
    return { version: 1, position: { unit: 0, card: 0 }, completedUnits: {} };
  }

  function validIndex(value, max) {
    return Number.isInteger(value) && value >= 0 && value < max;
  }

  function sanitizeSummary(value) {
    if (!value || typeof value !== 'object') return null;
    const fields = ['correct', 'review', 'incorrect', 'unanswered', 'total'];
    if (!fields.every(k => Number.isInteger(value[k]) && value[k] >= 0 && value[k] <= 1000)) return null;
    if (value.total < 1 || fields.slice(0, 4).reduce((sum, key) => sum + value[key], 0) !== value.total) return null;
    const completed = typeof value.completed === 'string' && Number.isFinite(Date.parse(value.completed))
      ? new Date(value.completed).toISOString() : null;
    if (!completed) return null;
    return { correct: value.correct, review: value.review, incorrect: value.incorrect,
      unanswered: value.unanswered, total: value.total, completed };
  }

  function sanitizeState(input, cardCounts) {
    if (!input || typeof input !== 'object' || input.version !== 1 || !Array.isArray(cardCounts) || !cardCounts.length) return null;
    const state = defaultState();
    const position = input.position;
    if (position && validIndex(position.unit, cardCounts.length) &&
        validIndex(position.card, cardCounts[position.unit])) {
      state.position = { unit: position.unit, card: position.card };
    }
    if (input.completedUnits && typeof input.completedUnits === 'object' && !Array.isArray(input.completedUnits)) {
      Object.entries(input.completedUnits).forEach(([key, value]) => {
        if (!/^(0|[1-9]\d*)$/.test(key)) return;
        const unit = Number(key);
        if (validIndex(unit, cardCounts.length)) {
          const summary = sanitizeSummary(value);
          if (summary) state.completedUnits[key] = summary;
        }
      });
    }
    return state;
  }

  function updatePosition(state, unit, card, cardCounts) {
    const safe = sanitizeState(state, cardCounts) || defaultState();
    if (!validIndex(unit, cardCounts.length) || !validIndex(card, cardCounts[unit])) return safe;
    return { ...safe, position: { unit, card } };
  }

  function updateResult(state, unit, result, completed, cardCounts) {
    const safe = sanitizeState(state, cardCounts) || defaultState();
    if (!validIndex(unit, cardCounts.length)) return safe;
    const summary = sanitizeSummary({ ...result, completed });
    if (!summary) return safe;
    return { ...safe, completedUnits: { ...safe.completedUnits, [String(unit)]: summary } };
  }

  function save(storage, state, cardCounts) {
    try {
      if (!storage) return { ok: false, reason: 'unavailable' };
      const safe = sanitizeState(state, cardCounts);
      if (!safe) return { ok: false, reason: 'invalid-state' };
      storage.setItem(STORAGE_KEY, JSON.stringify(safe));
      return { ok: true, reason: 'saved' };
    } catch (error) {
      return { ok: false, reason: error && error.name === 'QuotaExceededError' ? 'quota' : 'unavailable' };
    }
  }

  function readLegacy(storage, cardCounts) {
    const state = defaultState();
    let found = false;
    const rawPosition = storage.getItem(LEGACY_KEYS[0]);
    if (rawPosition) {
      found = true;
      try {
        const old = JSON.parse(rawPosition);
        if (old && validIndex(old.unit, cardCounts.length) && validIndex(old.position, cardCounts[old.unit])) {
          state.position = { unit: old.unit, card: old.position };
        }
      } catch { /* Corrupt legacy position is ignored; completed results can still migrate. */ }
    }
    cardCounts.forEach((_, unit) => {
      const raw = storage.getItem(`english-professor-result-unit-${unit}`);
      if (!raw) return;
      found = true;
      try {
        const old = JSON.parse(raw);
        const summary = sanitizeSummary({ ...old, completed: old && old.completed });
        if (summary) state.completedUnits[String(unit)] = summary;
      } catch { /* Corrupt legacy result is ignored. */ }
    });
    return found ? state : null;
  }

  function load(storage, cardCounts) {
    if (!storage) return { state: defaultState(), status: 'unavailable' };
    try {
      const raw = storage.getItem(STORAGE_KEY);
      if (raw !== null) {
        let parsed;
        try { parsed = JSON.parse(raw); } catch { return { state: defaultState(), status: 'corrupt' }; }
        const state = sanitizeState(parsed, cardCounts);
        return state ? { state, status: 'loaded' } : { state: defaultState(), status: 'invalid' };
      }
      const migrated = readLegacy(storage, cardCounts);
      if (migrated) {
        const saved = save(storage, migrated, cardCounts);
        return { state: migrated, status: saved.ok ? 'migrated' : 'migration-unsaved' };
      }
      return { state: defaultState(), status: 'empty' };
    } catch {
      return { state: defaultState(), status: 'unavailable' };
    }
  }

  function clear(storage) {
    try {
      if (!storage) return { ok: false, reason: 'unavailable' };
      storage.removeItem(STORAGE_KEY);
      LEGACY_KEYS.forEach(key => storage.removeItem(key));
      return { ok: true, reason: 'cleared' };
    } catch {
      return { ok: false, reason: 'unavailable' };
    }
  }

  return Object.freeze({ STORAGE_KEY, defaultState, sanitizeState, updatePosition, updateResult, save, load, clear });
});
