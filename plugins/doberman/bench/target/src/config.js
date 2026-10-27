const users = new Map();
const resets = new Map();
const sessions = new Map();

module.exports = {
  users,
  resets,
  sessions,
  JWT_SECRET: 'FAKE-jwt-secret-not-real-0000',
  OAUTH_CLIENT_ID: 'FAKE-client-id-0000',
  OAUTH_CLIENT_SECRET: 'FAKE-client-secret-0000',
  IDP_URL: 'https://idp.example.test',
  APP_URL: 'https://app.example.test',
  REDIRECT_ALLOWLIST: ['https://app.example.test'],
};
