javascript: (function () {
  fetch(
    'https://f53muhq5jfnx7gxdt7ihdb2q2u0cwfmj.lambda-url.us-west-2.on.aws?' + new URLSearchParams({url: window.location.href}), 
    {
      method: 'GET',
      headers: {
        'Authorization': 'Basic base64-encoded-credentials-here',
        'Content-Type': 'text/plain',
      },
    }).then(res => res.json()).then(data => {
      const summary = data.result;
      const banner = document.createElement('div');
      banner.style.position = 'fixed';
      banner.style.left = '0';
      banner.style.right = '0';
      banner.style.top = '0';
      banner.style.zIndex = 999999999;
      banner.style.background = '#000';
      banner.style.color = '#fff';
      banner.style.padding = '15px';
      banner.innerHTML = summary;
      document.body.appendChild(banner);
    });
})();
