'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const P = require('../src/persistence.js');
const counts = [5, 5, 5, 5];

function memoryStorage(seed = {}) {
  const data = new Map(Object.entries(seed));
  return {
    getItem(key) { return data.has(key) ? data.get(key) : null; },
    setItem(key, value) { data.set(key, String(value)); },
    removeItem(key) { data.delete(key); },
    dump() { return Object.fromEntries(data); }
  };
}

test('saves and reloads position and completed result across storage instances', () => {
  const storage = memoryStorage();
  let state = P.defaultState();
  state = P.updatePosition(state, 2, 3, counts);
  state = P.updateResult(state, 2, { correct: 3, review: 1, incorrect: 0, unanswered: 1, total: 5 }, '2026-10-31T12:00:00.000Z', counts);
  assert.equal(P.save(storage, state, counts).ok, true);
  const loaded = P.load(storage, counts);
  assert.equal(loaded.status, 'loaded');
  assert.deepEqual(loaded.state.position, { unit: 2, card: 3 });
  assert.equal(loaded.state.completedUnits['2'].review, 1);
});

test('rejects out-of-range position and malformed results', () => {
  const raw = { version: 1, position: { unit: 99, card: 0 }, completedUnits: {
    '0': { correct: 5, review: 0, incorrect: 0, unanswered: 0, total: 6, completed: '2026-10-31T12:00:00Z' }
  }};
  const safe = P.sanitizeState(raw, counts);
  assert.deepEqual(safe.position, { unit: 0, card: 0 });
  assert.deepEqual(safe.completedUnits, {});
});

test('reports corrupt JSON and unsupported schema without throwing', () => {
  assert.equal(P.load(memoryStorage({ [P.STORAGE_KEY]: '{' }), counts).status, 'corrupt');
  assert.equal(P.load(memoryStorage({ [P.STORAGE_KEY]: JSON.stringify({ version: 99 }) }), counts).status, 'invalid');
});

test('migrates the previous position and per-unit result keys', () => {
  const oldResult = { correct: 4, review: 1, incorrect: 0, unanswered: 0, total: 5, completed: '2026-10-31T12:00:00.000Z' };
  const storage = memoryStorage({
    'english-professor-position': JSON.stringify({ unit: 1, position: 4 }),
    'english-professor-result-unit-1': JSON.stringify(oldResult)
  });
  const loaded = P.load(storage, counts);
  assert.equal(loaded.status, 'migrated');
  assert.deepEqual(loaded.state.position, { unit: 1, card: 4 });
  assert.equal(loaded.state.completedUnits['1'].correct, 4);
  assert.ok(storage.getItem(P.STORAGE_KEY));
});

test('storage denial and quota errors become explicit results', () => {
  assert.equal(P.load(null, counts).status, 'unavailable');
  const denied = { getItem() { throw Object.assign(new Error('denied'), { name: 'SecurityError' }); } };
  assert.equal(P.load(denied, counts).status, 'unavailable');
  const quota = { setItem() { throw Object.assign(new Error('full'), { name: 'QuotaExceededError' }); } };
  assert.equal(P.save(quota, P.defaultState(), counts).reason, 'quota');
});

test('clear removes current and legacy keys', () => {
  const storage = memoryStorage({ [P.STORAGE_KEY]: '{}', 'english-professor-position': '{}', 'english-professor-result-unit-0': '{}' });
  assert.equal(P.clear(storage).ok, true);
  assert.deepEqual(storage.dump(), {});
});
