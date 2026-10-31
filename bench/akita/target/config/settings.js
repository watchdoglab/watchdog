'use strict';

const env = process.env.NODE_ENV || 'development';

module.exports = {
  env,
  port: Number(process.env.PORT) || 3000,
  db: {
    url: process.env.DATABASE_URL,
  },
  jwt: {
    secret: process.env.JWT_SECRET || 'FAKE-JWT-SECRET-0001',
    expiresIn: '3650d',
  },
  stripe: {
    key: process.env.STRIPE_SECRET_KEY || 'FAKE-STRIPE-KEY-0001',
  },
  adminApiKey: 'FAKE-ADMIN-KEY-0001',
};
