const http = require('http');

const data = JSON.stringify({
  message: 'Someone claiming to be from CBI says my Aadhar is linked to money laundering',
  history: []
});

const options = {
  hostname: 'localhost',
  port: 5000,
  path: '/api/fraud-shield/chat',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': data.length
  }
};

const req = http.request(options, (res) => {
  let body = '';
  res.on('data', (chunk) => { body += chunk; });
  res.on('end', () => {
    console.log('Status Code:', res.statusCode);
    console.log('Response Body:', body);
  });
});

req.on('error', (e) => {
  console.error(`Problem with request: ${e.message}`);
});

req.write(data);
req.end();
