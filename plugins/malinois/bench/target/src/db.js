const sqlite3 = require('sqlite3');
const db = new sqlite3.Database(':memory:');

db.serialize(() => {
  db.run('CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT, password TEXT, role TEXT)');
  db.run('CREATE TABLE notes (id INTEGER PRIMARY KEY, owner_id INTEGER, body TEXT)');
});

module.exports = db;
