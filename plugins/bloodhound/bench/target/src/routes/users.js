const express = require('express');
const fetch = require('node-fetch');
const { users, webhooks } = require('../db');

const router = express.Router();

router.get('/users/me', (req, res) => {
  res.json(users.get(req.user.sub));
});

router.patch('/users/me', (req, res) => {
  const user = users.get(req.user.sub);
  Object.assign(user, req.body);
  res.json(user);
});

router.post('/webhooks', async (req, res) => {
  const { url } = req.body;
  const probe = await fetch(url, { method: 'POST', body: '{"ping":true}' });
  webhooks.push({ owner: req.user.sub, url, status: probe.status });
  res.status(201).json({ ok: true });
});

module.exports = router;
