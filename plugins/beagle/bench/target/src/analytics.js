const crypto = require('crypto');
const config = require('./config');

async function send(event, props) {
  await fetch(config.analyticsHost + '/track', {
    method: 'POST',
    body: JSON.stringify({ token: config.mixpanelToken, event, properties: props })
  });
}

function identify(user) {
  return send('identify', user);
}

function trackWorkout(user, workout) {
  const id = crypto.createHash('sha256').update(user.id + process.env.ANALYTICS_SALT).digest('hex');
  return send('workout_logged', { distinct_id: id, type: workout.type, minutes: workout.minutes });
}

function trackHealth(user, profile) {
  return send('health_profile', {
    email: user.email,
    conditions: profile.conditions,
    lat: profile.lat,
    lng: profile.lng
  });
}

module.exports = { identify, trackWorkout, trackHealth };
