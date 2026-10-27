const express = require('express');
const cors = require('cors');
const { ApolloServer } = require('apollo-server-express');
const auth = require('./middleware/auth');
const accounts = require('./routes/accounts');
const users = require('./routes/users');
const admin = require('./routes/admin');
const { typeDefs, resolvers } = require('./graphql');

const app = express();
app.use(cors({ origin: true, credentials: true }));
app.use(express.json());

app.get('/v1/health', (req, res) => res.json({ ok: true }));

app.use('/v1', admin);
app.use('/v1', auth, accounts);
app.use('/v1', auth, users);
app.use('/v0', accounts);

const gql = new ApolloServer({ typeDefs, resolvers, introspection: true });
gql.start().then(() => gql.applyMiddleware({ app, path: '/graphql' }));

app.use((err, req, res, next) => {
  res.status(500).json({ error: err.message, stack: err.stack });
});

app.listen(8080);
