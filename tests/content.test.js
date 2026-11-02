'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
global.window = global;
require('../src/evaluator.js');
require('../src/unit2.js');
require('../src/unit3.js');
require('../src/unit4.js');
const units = [global.EnglishUnit2, global.EnglishUnit3, global.EnglishUnit4];

test('unidades A1 publicadas têm cinco cartões e cinco perguntas', () => {
  for (const unit of units) {
    assert.equal(unit.cards.length, 5);
    assert.equal(unit.questions.length, 5);
  }
});

test('todas as alternativas escritas cadastradas passam no avaliador determinístico', () => {
  for (const unit of units) {
    for (const question of unit.questions.filter(q => q.type === 'write')) {
      assert.ok(Array.isArray(question.accept) && question.accept.length > 0, question.title);
      for (const answer of question.accept) {
        assert.equal(global.EnglishEvaluator.grade(question, answer).status, 'correct', `${question.title}: ${answer}`);
      }
    }
  }
});

test('variantes equivalentes de escrita adicionadas são reconhecidas', () => {
  const qSheWorks = units[0].questions[0];
  const qHeHome = units[1].questions[2];
  const qDaily = units[2].questions[0];
  const qPastContinuous = units[2].questions[3];
  assert.equal(global.EnglishEvaluator.grade(qSheWorks, 'She works in the store.').status, 'correct');
  assert.equal(global.EnglishEvaluator.grade(qHeHome, "He's not at home.").status, 'correct');
  assert.equal(global.EnglishEvaluator.grade(qDaily, 'I study English daily.').status, 'correct');
  assert.equal(global.EnglishEvaluator.grade(qPastContinuous, 'I was studying at 8 o’clock.').status, 'correct');
});
