const express = require('express');
const cookieParser = require('cookie-parser');

const app = express();
app.use(express.json());
app.use(cookieParser());

app.use(require('./routes/login'));
app.use(require('./routes/mfa'));
app.use(require('./routes/reset'));
app.use(require('./routes/oauth'));
app.use(require('./routes/sso'));

app.listen(3000);
