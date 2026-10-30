const router = require('express').Router();
const bcrypt = require('bcrypt');
const db = require('../db');
const analytics = require('../analytics');
const { auditFailedLogin } = require('../logger');

router.post('/signup', async (req, res) => {
  const { name, email, phone, aadhaar, dob, password, marketing = true } = req.body;
  const user = await db.one(
    'INSERT INTO users (name, email, phone, aadhaar, dob, pw_hash, marketing_opt_in) VALUES ($1,$2,$3,$4,$5,$6,$7) RETURNING *',
    [name, email, phone, aadhaar, dob, await bcrypt.hash(password, 12), marketing]
  );
  await analytics.identify(user);
  res.status(201).json({ id: user.id });
});

router.post('/login', async (req, res) => {
  const user = await db.oneOrNone('SELECT id, pw_hash FROM users WHERE email=$1', [req.body.email]);
  if (!user || !(await bcrypt.compare(req.body.password, user.pw_hash))) {
    auditFailedLogin(req.body.email);
    return res.status(401).end();
  }
  res.json({ id: user.id });
});

router.post('/otp', async (req, res) => {
  const otp = String(Math.floor(100000 + Math.random() * 900000));
  console.log('OTP for', req.body.phone, otp);
  res.json({ sent: true });
});

router.get('/lookup/:email', async (req, res) => {
  res.json(await db.oneOrNone('SELECT * FROM users WHERE email=$1', [req.params.email]));
});

router.get('/', async (req, res) => {
  res.json(await db.any('SELECT * FROM users'));
});

router.post('/:id/health', async (req, res) => {
  const { conditions, lat, lng } = req.body;
  await db.none('UPDATE users SET conditions=$1, lat=$2, lng=$3 WHERE id=$4', [conditions, lat, lng, req.params.id]);
  await analytics.trackHealth(req.user, req.body);
  res.status(204).end();
});

router.post('/:id/workouts', async (req, res) => {
  await db.none('INSERT INTO workouts (user_id, type, minutes) VALUES ($1,$2,$3)', [req.params.id, req.body.type, req.body.minutes]);
  await analytics.trackWorkout(req.user, req.body);
  res.status(201).end();
});

router.delete('/:id', async (req, res) => {
  await db.none('UPDATE users SET deleted=true WHERE id=$1', [req.params.id]);
  res.status(204).end();
});

module.exports = router;
