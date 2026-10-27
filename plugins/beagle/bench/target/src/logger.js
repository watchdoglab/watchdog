const fs = require('fs');
const config = require('./config');

function mask(v) {
  return String(v).replace(/(^.).*(@.*$)/, '$1***$2');
}

function requestLogger(req, res, next) {
  const entry = {
    t: new Date().toISOString(),
    ip: req.ip,
    ua: req.headers['user-agent'],
    method: req.method,
    url: req.originalUrl
  };
  if (config.logFullBodies) entry.body = req.body;
  fs.appendFileSync('logs/access.log', JSON.stringify(entry) + '\n');
  next();
}

function auditFailedLogin(email) {
  fs.appendFileSync('logs/audit.log', 'login failed for ' + mask(email) + '\n');
}

module.exports = { requestLogger, auditFailedLogin };
