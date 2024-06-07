javascript: (function () {
  fetch(
    'https://f53muhq5jfnx7gxdt7ihdb2q2u0cwfmj.lambda-url.us-west-2.on.aws?' + new URLSearchParams({url: window.location.href}), 
    {
      method: 'GET',
      headers: {
        'Authorization': 'Basic base64-encoded-credentials-here',
        'Content-Type': 'text/plain',
      },
    })
})();
