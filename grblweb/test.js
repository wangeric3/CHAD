var config = require('./config');
var app = require('http').createServer()
  , io = require('socket.io').listen(app)
  , fs = require('fs');
var static = require('node-static');
var EventEmitter = require('events').EventEmitter;
var url = require('url');
var qs = require('querystring');
var http = require('http');

app.listen(9000);


io.sockets.on('connection', function (socket) {
  //Send welcome after connection is established
  socket.emit('welcome', { hello: 'world' });

  //Response question from client include client name
  socket.on('howareyou', function (data) {
  	console.log("Client "+ data.name+" requested 'howareyou'");
    socket.emit('howareyou', { data: 'I\'m fine, thank' + data.name });
  });

  socket.on('disconnect', function () {
    console.log("Client is disconnected");
  });
});