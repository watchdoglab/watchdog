const crypto = require('crypto');
const express = require('express');
const { users, sessions } = require('../config');
const { signToken, requireAuth } = require('../jwt');

const router = express.Router();

const hash = (pw) => crypto.createHash('md5').update(pw).digest('hex');

router.post('/signup', (req, res) => {
  const { email, password } = req.body;
  if (!password || password.length < 4) return res.status(400).json({ error: 'password too short' });
  if (users.has(email)) return res.status(409).json({ error: 'email already registered' });
  const user = { id: crypto.randomUUID(), email, pw: hash(password), role: 'user', mfaEnabled: false };
  users.set(email, user);
  res.status(201).json({ id: user.id });
});

router.post('/login', (req, res) => {
  const { email, password } = req.body;
  const user = users.get(email);
  if (!user) return res.status(404).json({ error: 'no such user' });
  if (user.pw !== hash(password)) return res.status(401).json({ error: 'wrong password' });

  const token = signToken(user);
  sessions.set(token, user.id);
  res.cookie('session', token, { maxAge: 365 * 24 * 3600 * 1000 });
  res.json({ ok: true, mfaRequired: user.mfaEnabled });
});

router.post('/logout', requireAuth, (req, res) => {
  res.clearCookie('session');
  res.json({ ok: true });
});

router.get('/logout/continue', (req, res) => {
  const next = req.query.next;
  const ok = next && new URL(next).origin === 'https://app.example.test';
  res.redirect(ok ? next : '/');
});

module.exports = router;
