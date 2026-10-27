const express = require('express');
const crypto = require('crypto');
const { users } = require('../config');
const { signToken } = require('../jwt');
const { parseAssertion } = require('saml-parser');

const router = express.Router();

router.post('/sso/acs', (req, res) => {
  const { email, emailVerified, name } = parseAssertion(req.body.SAMLResponse);
  let user = users.get(email);
  if (!user) {
    user = { id: crypto.randomUUID(), email, name, role: 'user', mfaEnabled: false };
    users.set(email, user);
  }
  res.json({ token: signToken(user) });
});

module.exports = router;
