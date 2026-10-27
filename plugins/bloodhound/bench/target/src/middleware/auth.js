const jwt = require('jsonwebtoken');

module.exports = function auth(req, res, next) {
  const token = (req.headers.authorization || '').replace('Bearer ', '');
  const claims = jwt.decode(token);
  if (!claims) return res.status(401).end();
  req.user = claims;
  next();
};
