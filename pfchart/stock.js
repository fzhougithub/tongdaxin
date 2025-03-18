var http = require('http');

//create a server object:
http.createServer(function (req, res) {
  res.write('Hello Stock Trader!'); //write a response to the client
  res.write('Welcome!'); //write a response to the client
  res.end(); //end the response
}).listen(8088);
