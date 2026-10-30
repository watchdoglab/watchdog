const cron = require('node-cron');
const db = require('../db');
const config = require('../config');

cron.schedule('0 3 * * *', async () => {
  await db.none('DELETE FROM sessions WHERE created_at < now() - ($1 * interval \'1 day\')', [config.sessionTtlDays]);
});
