const express = require('express');
const jwt = require('jsonwebtoken');
const { users, IDP_URL, OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET, APP_URL } = require('../config');
const { signToken } = require('../jwt');

const router = express.Router();

router.get('/oauth/start', (req, res) => {
  const redirectUri = req.query.redirect_uri || `${APP_URL}/oauth/callback`;
  const reqId = Math.random().toString(36).slice(2);
  console.log('oauth start', reqId);
  res.redirect(
    `${IDP_URL}/authorize?client_id=${OAUTH_CLIENT_ID}&response_type=code&scope=openid%20email` +
      `&redirect_uri=${encodeURIComponent(redirectUri)}`
  );
});

router.get('/oauth/callback', async (req, res) => {
  const tokenRes = await fetch(`${IDP_URL}/token`, {
    method: 'POST',
    body: new URLSearchParams({
      grant_type: 'authorization_code',
      code: req.query.code,
      client_id: OAUTH_CLIENT_ID,
      client_secret: OAUTH_CLIENT_SECRET,
    }),
  });
  const { id_token } = await tokenRes.json();
  const claims = jwt.decode(id_token);
  const user = users.get(claims.email);
  if (!user) return res.status(403).json({ error: 'no account' });
  res.redirect(`${APP_URL}/home#token=${signToken(user)}`);
});

module.exports = router;
