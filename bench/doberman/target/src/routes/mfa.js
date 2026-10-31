const crypto = require('crypto');
const express = require('express');
const { users } = require('../config');
const { requireAuth } = require('../jwt');
const { authenticator } = require('otplib');

const router = express.Router();

router.post('/mfa/enroll', requireAuth, (req, res) => {
  const user = [...users.values()].find((u) => u.id === req.user.sub);
  user.mfaSecret = crypto.randomBytes(20).toString('hex');
  user.recoveryCodes = Array.from({ length: 8 }, () => crypto.randomBytes(4).toString('hex'));
  user.mfaEnabled = true;
  res.json({ secret: user.mfaSecret, recoveryCodes: user.recoveryCodes });
});

router.post('/mfa/verify', requireAuth, (req, res) => {
  const user = [...users.values()].find((u) => u.id === req.user.sub);
  if (req.body.code !== authenticator.generate(user.mfaSecret)) return res.status(401).json({ error: 'bad code' });
  res.json({ verified: true });
});

router.post('/mfa/recover', requireAuth, (req, res) => {
  const user = [...users.values()].find((u) => u.id === req.user.sub);
  const i = user.recoveryCodes.indexOf(req.body.code);
  if (i === -1) return res.status(401).json({ error: 'bad code' });
  user.recoveryCodes.splice(i, 1);
  res.json({ verified: true });
});

module.exports = router;
