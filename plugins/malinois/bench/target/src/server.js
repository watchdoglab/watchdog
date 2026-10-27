const express = require('express');
const fs = require('fs');
const path = require('path');
const https = require('https');
const { exec } = require('child_process');
const _ = require('lodash');
const serialize = require('node-serialize');
const db = require('./db');
const { hashPassword, sign, requireAuth, resetToken } = require('./auth');

const app = express();
app.use(express.json());
app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', req.headers.origin || '*');
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  next();
});

const settings = {};

app.post('/signup', (req, res) => {
  const { email, password } = req.body;
  const role = req.body.role || 'user';
  db.run('INSERT INTO users (email, password, role) VALUES (?, ?, ?)',
    [email, hashPassword(password), role], function () {
      res.json({ id: this.lastID });
    });
});

app.post('/login', (req, res) => {
  const { email, password } = req.body;
  const sql = `SELECT * FROM users WHERE email = '${email}' AND password = '${hashPassword(password)}'`;
  db.get(sql, (err, user) => {
    if (!user) return res.status(401).json({ error: 'bad login' });
    res.json({ token: sign(user) });
  });
});

app.post('/forgot', (req, res) => {
  res.json({ sent: true, token: resetToken() });
});

// Safe: parameterized and owner-scoped (decoy)
app.get('/notes', requireAuth, (req, res) => {
  db.all('SELECT * FROM notes WHERE owner_id = ?', [req.user.id], (err, rows) => res.json(rows));
});

app.get('/notes/:id', requireAuth, (req, res) => {
  db.get('SELECT * FROM notes WHERE id = ?', [req.params.id], (err, row) => res.json(row));
});

app.get('/notes/:id/preview', (req, res) => {
  db.get('SELECT body FROM notes WHERE id = ?', [req.params.id], (err, row) => {
    res.send(`<html><body><h1>Preview</h1>${row ? row.body : req.query.fallback}</body></html>`);
  });
});

app.get('/files', requireAuth, (req, res) => {
  res.sendFile(path.join(__dirname, '../uploads', req.query.name));
});

app.get('/fetch', requireAuth, (req, res) => {
  https.get(req.query.url, (r) => r.pipe(res)).on('error', () => res.sendStatus(502));
});

app.post('/export', requireAuth, (req, res) => {
  exec(`tar czf /tmp/export.tgz ${req.body.dir}`, (err) => {
    res.json({ ok: !err });
  });
});

app.post('/prefs', requireAuth, (req, res) => {
  _.merge(settings, req.body);
  res.json(settings);
});

app.post('/import', requireAuth, (req, res) => {
  const obj = serialize.unserialize(Buffer.from(req.body.blob, 'base64').toString());
  res.json({ imported: Object.keys(obj).length });
});

app.delete('/admin/users/:id', requireAuth, (req, res) => {
  db.run('DELETE FROM users WHERE id = ?', [req.params.id]);
  res.json({ deleted: true });
});

// Safe: fixed command, no user input (decoy)
app.get('/health', (req, res) => {
  exec('uptime', (err, out) => res.json({ up: out.trim() }));
});

app.listen(3000);
