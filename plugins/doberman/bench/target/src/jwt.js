const jwt = require('jsonwebtoken');
const { JWT_SECRET } = require('./config');

function signToken(user) {
  return jwt.sign({ sub: user.id, email: user.email, role: user.role }, JWT_SECRET, {
    expiresIn: '365d',
  });
}

function requireAuth(req, res, next) {
  const raw = (req.headers.authorization || '').replace('Bearer ', '');
  const claims = jwt.decode(raw);
  if (!claims) return res.status(401).json({ error: 'unauthorized' });
  req.user = claims;
  next();
}

function verifyServiceToken(raw) {
  return jwt.verify(raw, JWT_SECRET, { algorithms: ['HS256'], audience: 'internal', issuer: 'app' });
}

module.exports = { signToken, requireAuth, verifyServiceToken };
