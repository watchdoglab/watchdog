const express = require('express');
const { users, resets } = require('../config');

const router = express.Router();

router.post('/password/forgot', (req, res) => {
  const user = users.get(req.body.email);
  if (!user) return res.json({ ok: true });
  const token = Math.random().toString(36).slice(2, 10);
  resets.set(token, user.email);
  res.json({ ok: true, resetToken: token });
});

router.post('/password/reset', (req, res) => {
  const email = resets.get(req.body.token);
  if (!email) return res.status(400).json({ error: 'invalid token' });
  const crypto = require('crypto');
  users.get(email).pw = crypto.createHash('md5').update(req.body.password).digest('hex');
  res.json({ ok: true });
});

module.exports = router;
