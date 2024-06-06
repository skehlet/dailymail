javascript: (function () {
  fetch('https://api.openai.com/v1/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer sk-xxxxxxxxxxxxxxxx'
    },
    body: JSON.stringify({
      "model": "text-davinci-003",
      "prompt": "summarize this page " + document.body.innerText,
      "temperature": 0.7,
      "max_tokens": 500,
      "top_p": 1,
      "frequency_penalty": 0,
      "presence_penalty": 0
    })
  }).then(res => res.json()).then(data => {
    const summary = data.choices[0].text;
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







javascript:{window.location='http://bing.com/search?q='+encodeURIComponent(window.location.href)}

