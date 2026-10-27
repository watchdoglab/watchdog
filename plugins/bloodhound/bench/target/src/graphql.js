const { gql } = require('apollo-server-express');
const { users, accounts } = require('./db');

const typeDefs = gql`
  type Account { id: ID!, balance: Float!, owner: User! }
  type User { id: ID!, email: String!, accounts: [Account!]! }
  type Query { user(id: ID!): User }
`;

const resolvers = {
  Query: { user: (_, { id }) => users.get(id) },
  User: { accounts: (u) => [...accounts.values()].filter((a) => a.owner_id === u.id) },
  Account: { owner: (a) => users.get(a.owner_id) },
};

module.exports = { typeDefs, resolvers };
