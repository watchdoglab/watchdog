const express = require('express');
const app = express();
app.use(express.json());
app.post('/charge', (req, res) => {
  console.log('charge', JSON.stringify(req.body));
  res.json({ ok: true });
});
app.listen(8080);
