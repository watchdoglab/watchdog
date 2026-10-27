const express = require('express');
const Sentry = require('@sentry/node');
const config = require('./config');
const { requestLogger } = require('./logger');
const users = require('./routes/users');
require('./jobs/retention');

Sentry.init({ dsn: config.sentryDsn, sendDefaultPii: true });

const app = express();
app.use(express.json());
app.use(requestLogger);
app.use('/users', users);
app.use(express.static('web'));

app.use((err, req, res, next) => {
  Sentry.withScope(scope => {
    scope.setUser({ id: req.user && req.user.id, email: req.user && req.user.email });
    scope.setExtra('body', req.body);
    Sentry.captureException(err);
  });
  res.status(500).json({ error: 'internal' });
});

app.listen(config.port);
