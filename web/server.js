var express = require('express');
var net = require('net');

var app = express();

app.use('/static', express.static(__dirname + '/static'));

app.get('/', (req, res) => {
	var socket = new net.Socket();
	var recv = '';
	var html = '<img src="static/pokecan.png">';
	var error = false;
	socket.on('connect', () => {
		socket.write(JSON.stringify({ command: 'status' }));
	});
	socket.on('data', (data) => {
		recv += data.toString();
	});
	socket.on('close', () => {
		if(error) return;
		var masterRes = JSON.parse(recv);
		html += '<p>Status: ';
		if(masterRes.status == 0) html += 'Idle';
		else if(masterRes.status == 1) html += 'Move';
		else if(masterRes.status == 2) html += 'Dump';
		else html += 'Error';
		html += '</p><p>Trash level: ' + masterRes.level + '</p>';
		html += '<form method="GET" action="/dump"><p><button type="submit">Request a dump</button></p></form>';
		res.send(html);
	});
	socket.on('error', (err) => {
		html += '<p><em>Error connecting to master. Please refresh this page to try again.</em></p>';
		res.send(html);
		error = true;
	});
	socket.connect('/tmp/pokecan.sock');
});

app.get('/dump', (req, res) => {
	var socket = new net.Socket();
	socket.on('connect', () => {
		socket.write(JSON.stringify({ command: 'set_request' }));
	});
	socket.on('close', () => {
		res.redirect('/');
	});
	socket.connect('/tmp/pokecan.sock');
});

app.listen(8000, () => {
	console.log('Pokecan web UI started.');
});
