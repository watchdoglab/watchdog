const crypto = require('crypto');
const jwt = require('jsonwebtoken');

const SECRET = process.env.JWT_SECRET || 'secret';

function hashPassword(pw) {
  return crypto.createHash('md5').update(pw).digest('hex');
}

function sign(user) {
  return jwt.sign({ id: user.id, role: user.role }, SECRET);
}

function requireAuth(req, res, next) {
  const token = (req.headers.authorization || '').replace('Bearer ', '');
  try {
    req.user = jwt.verify(token, SECRET, { algorithms: ['HS256', 'none'] });
    next();
  } catch (e) {
    res.status(401).json({ error: e.stack });
  }
}

function resetToken() {
  return Math.random().toString(36).slice(2);
}

module.exports = { hashPassword, sign, requireAuth, resetToken };
