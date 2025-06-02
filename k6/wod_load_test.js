import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 10 },
    { duration: '5m', target: 50 },
    { duration: '5m', target: 100 },
    { duration: '5m', target: 200 },
    { duration: '2m', target: 0 },
  ],
};

export function setup() {
  // First create a test user and get the password
  let bootstrapPayload = JSON.stringify({
    email: 'loadtest@example.com',
    name: 'Load Test User'
  });

  let bootstrapParams = {
    headers: {
      'Content-Type': 'application/json',
      'X-Bootstrap-Key': 'bootstrap-secret-key'
    },
  };

  let bootstrapResponse = http.post('http://localhost:5000/bootstrap/admin', bootstrapPayload, bootstrapParams);
  
  if (bootstrapResponse.status === 201) {
    let userData = JSON.parse(bootstrapResponse.body);
    
    // Now login with the created user
    let loginPayload = JSON.stringify({
      email: userData.email,
      password: userData.password
    });

    let loginParams = {
      headers: {
        'Content-Type': 'application/json',
      },
    };

    let loginResponse = http.post('http://localhost:5000/oauth/token', loginPayload, loginParams);
    
    if (loginResponse.status === 200) {
      let responseBody = JSON.parse(loginResponse.body);
      return { token: responseBody.access_token };
    }
  }
  
  return { token: null };
}

export default function (data) {
  if (!data.token) {
    console.log('No valid token available');
    return;
  }

  let params = {
    headers: {
      'Authorization': `Bearer ${data.token}`,
      'Content-Type': 'application/json',
    },
  };

  let response = http.get('http://localhost:5000/fitness/wod', params);
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 5000ms': (r) => r.timings.duration < 5000,
    'has exercises': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.exercises && body.exercises.length > 0;
      } catch {
        return false;
      }
    }
  });

  sleep(1);
}