/* Deterministic, conservative grading; no AI or semantic inference. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.EnglishEvaluator = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  function normalize(input) {
    if (typeof input !== 'string') return '';
    return input.toLocaleLowerCase('en-US').normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '').replace(/[.,!?;:]/g, '')
      .replace(/[’‘]/g, "'").replace(/\s+/g, ' ').trim();
  }
  function grade(question, value) {
    if (!question || !['write', 'choose'].includes(question.type)) throw new TypeError('Invalid question');
    if (question.type === 'choose') {
      if (value === null || value === undefined || value === '') return {status:'unanswered', score:0};
      return Number(value) === question.answer ? {status:'correct', score:1} : {status:'incorrect', score:0};
    }
    const answer = normalize(value);
    if (!answer) return {status:'unanswered', score:0};
    if ((question.accept || []).some(a => normalize(a) === answer)) return {status:'correct', score:1};
    // In an open-ended task, not matching approved answers is NOT proof of being wrong.
    return {status:'review', score:null};
  }
  function summarize(questions, values) {
    if (!Array.isArray(questions) || !Array.isArray(values) || questions.length !== values.length) throw new TypeError('Invalid inputs');
    const outcomes = questions.map((q,i)=>grade(q,values[i]));
    return {outcomes, correct:outcomes.filter(o=>o.status==='correct').length,
      review:outcomes.filter(o=>o.status==='review').length,
      incorrect:outcomes.filter(o=>o.status==='incorrect').length,
      unanswered:outcomes.filter(o=>o.status==='unanswered').length,
      total:questions.length};
  }
  return Object.freeze({normalize,grade,summarize});
});
