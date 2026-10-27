'use strict';

const express = require('express');
const settings = require('../config/settings');

const app = express();

app.use((req, res, next) => {
  console.log(req.method, req.url, JSON.stringify(req.headers));
  next();
});

app.get('/health', (req, res) => res.json({ ok: true }));

app.get('/debug/env', (req, res) => {
  res.json(process.env);
});

app.get('/admin/invoices', (req, res) => {
  const key = req.query.api_key;
  if (key !== settings.adminApiKey) return res.sendStatus(401);
  res.json({ invoices: [] });
});

app.listen(settings.port);
