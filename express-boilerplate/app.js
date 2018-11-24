
/*jslint node: true, nomen: true*/
"use strict";

var express = require('express');
var path = require('path');
var morgan = require('morgan');
var winston = require('winston');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');
var fs = require('fs');
var routes = require('./routes/index');
var users = require('./routes/users');
var socket_io    = require( "socket.io" );

var app = express();

// Socket.io
var io           = socket_io();
app.io           = io;

// view engine setup (not included)


app.use(bodyParser.json());
app.use(bodyParser.urlencoded({
	extended: false
}));
app.use(cookieParser());

let guiSocketId;
let remoteSocketId;

io.on('connection', function(socket){


  socket.on('guiInit', (data) => {
  	guiSocketId = socket.id
  })

  socket.emit('init', {'msg':'start again'});


  socket.on('screenshot_taken', (data) => {
 	
  	let base64Image = data.image.split("b'").pop();
  	//base64Image.data.image.split().pop()
  	console.log(base64Image)
 //  	fs.writeFile('image.png', base64Image, {encoding: 'base64'}, function(err) {
 //    	console.log('File created');

	// });

  	io.sockets.to(guiSocketId).emit('screenshot_send', base64Image);
  })

  socket.on('screenshot', (data) => {
  	 io.sockets.to(remoteSocketId).emit('screenshot');
  })

  socket.on('message', (data) => {
  	remoteSocketId = socket.id
  })

  socket.on('mouseControl', (data) => {
  	let x = data.x
  	let y = data.y

  	console.log(data)

  
  	io.sockets.to(remoteSocketId).emit('mouse', {x:x, y:y});
  })

  socket.on('mouseLeftClick', (data) => {
  	console.log('clicked left')
  	io.sockets.to(remoteSocketId).emit('mouseLeftClick');
  })

  console.log('a user connected', socket.id);

  socket.on('keyLog', (data) => {
  	console.log(`this key was pressed: ${data.key}`)
  	console.log('sending to gui remote... id: ', guiSocketId)
  	io.sockets.to(guiSocketId).emit('keystrokes', data);
  })


  setInterval(() => {
  	if (remoteSocketId) {
  	    io.sockets.to(guiSocketId).emit('remoteConnected');
  	}
  }, 1000)
});


// get config

// pretend to return favicon
app.get('/favicon.ico', function (req, res) {
	res.send(200);
});

// Set the ENV variable to point to the right environment

switch (process.env.NODE_ENV) {
case 'development':
	app.set('env', 'development');
	break;
case 'production':
	app.set('env', 'production');
	break;
case 'test':
	app.set('env', 'test');
	break;
default:
	console.error("NODE_ENV environment variable should have value 'development', 'test', or 'production' \nExiting");
	process.exit();
}

//load the config variables depending on the environment

var config_file_name = app.get('env') + '_config.json';
var data = fs.readFileSync(path.join(__dirname, 'config', config_file_name));
var myObj;
var configObject, property;
try {
	configObject = JSON.parse(data);
} catch (err) {
	console.log('There has been an error parsing the config file JSON.');
	console.log(err);
	process.exit();
}
app.config = {};
for (property in configObject) {
	if (configObject.hasOwnProperty(property)) {
		app.config[property] = configObject[property];
	}
}


var logLevel = process.env.LOGGING_LEVEL;
if (!(logLevel === 'info' || logLevel === 'warn' || logLevel === 'error' || logLevel === 'debug')) {
	console.warn('LOGGING_LEVEL environment variable not set to a valid logging level. Using default level info');
	logLevel = 'info';
}

try {
    fs.accessSync(app.config.LOGGING_DIRECTORY, fs.F_OK);
} catch (e) {
    console.error('Could not access LOGGING_DIRECTORY that is set in config.\nExiting');
	process.exit();
}

//logging using winston

var winstonTransports = [
    new winston.transports.File({
		name: 'fileLog',
		level: logLevel,
		filename: path.join(app.config.LOGGING_DIRECTORY, app.config.LOG_FILE_NAME_PREFIX + '.log'),
		handleExceptions: true,
		json: false,
		maxsize: 5242880, //5MB
		maxFiles: 5,
		colorize: false,
		timestamp: true
	})
];

if (logLevel === 'debug') {
	winstonTransports.push(new winston.transports.Console({
		level: 'debug',
		json: false,
		handleExceptions: true,
		colorize: true,
		timestamp: true
	}));
}

var logger = new winston.Logger({
	transports: winstonTransports,
	exitOnError: false
});

logger.level = logLevel;

logger.stream = {
	write: function (message, encoding) {
		logger.info(message);
	}
};

app.logger = logger;

app.use(require("morgan")('short', {
	"stream": logger.stream
}));

app.use('/', routes);
app.use('/users', users(express, logger, app.config));

// catch 404 and forward to error handler
app.use(function (req, res, next) {
	var err = new Error('Not Found');
	err.status = 404;
	next(err);
});

// error handlers

// development error handler
// will print stacktrace
if (app.get('env') === 'development') {
	app.use(function (err, req, res, next) {
		res.status(err.status || 500);
		res.json({
			message: err.message,
			error: err
		});
	});
}

// production error handler
// no stacktraces leaked to user
app.use(function (err, req, res, next) {
	res.status(err.status || 500);
	res.json({
		message: err.message,
		error: {}
	});
});

module.exports = app;
