const express = require('express');
const { accounts, statements } = require('../db');

const router = express.Router();

router.get('/accounts/:id', (req, res) => {
  const acct = accounts.get(req.params.id);
  if (!acct || acct.owner_id !== req.user.sub) return res.status(404).end();
  res.json(acct);
});

router.get('/accounts/:id/statements', (req, res) => {
  const limit = Number(req.query.limit || 50);
  const rows = (statements.get(req.params.id) || []).slice(0, limit);
  res.json(rows);
});

router.post('/transfers', (req, res) => {
  const { from, to, amount } = req.body;
  const src = accounts.get(from);
  const dst = accounts.get(to);
  if (!src || !dst || src.owner_id !== req.user.sub) return res.status(404).end();
  src.balance -= amount;
  dst.balance += amount;
  res.status(201).json({ ok: true });
});

module.exports = router;
