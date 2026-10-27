const express = require('express');
const { users } = require('../db');

const router = express.Router();

router.get('/reports/export', (req, res) => {
  const rows = [...users.values()].map((u) => [u.id, u.email, u.ssn].join(','));
  res.type('text/csv').send(rows.join('\n'));
});

router.get('/debug/users', (req, res) => {
  res.json([...users.values()]);
});

router.delete('/users/:id', (req, res) => {
  users.delete(req.params.id);
  res.status(204).end();
});

module.exports = router;
