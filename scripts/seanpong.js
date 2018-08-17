// seanpong .js
// 7 - 19 - 2018

var canvas;
var ctx;
var mouse = {x: 0, y: 0};
var player1;
var player2;
var interval;
var fr = 30;

var ball = {
	x: 300,
	y: 200,
	radius: 25, 
	color: 'blue',
	
    draw: function() {
		ctx.save();
		ctx.translate(this.x, this.y);
		ctx.beginPath();
		ctx.arc(0, 0, this.radius, 0, Math.PI * 2, true);
		ctx.closePath();
		ctx.fillStyle = this.color;
		ctx.fill();
		ctx.restore();
	}
}

function paddle(h, w, y, scorex, scorey) {
	this.width = w;
	this.height = h;
	this.x = scorex;
    this.y = y;
    this.score = { x: scorex, y: scorey, value: 0};
}

paddle.prototype.draw = 
function() {
    //draw score
    ctx.save();
    ctx.font = '50px Consolas';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.translate(this.score.x, this.score.y);
    ctx.fillStyle = 'rgba(0, 0, 0, 1.0)';
    ctx.fillText(this.score.value, 0, 0);
    ctx.restore();
	
    //draw paddle
    ctx.save();
	ctx.fillStyle = 'rgba(0, 0, 0, 1.0)';
    ctx.translate(this.x-this.width/2., this.y);
	ctx.fillRect(0, 0, this.width, this.height);
	ctx.restore();
}	

function adjustVerticalCentering(canvasContainer, bodyHeight, canvasHeight) {
	let pad = (bodyHeight - canvasHeight) / 2;
	let toolbar = 30;
	canvasContainer.style.paddingBottom = pad+toolbar;
	canvasContainer.style.paddingTop = pad-toolbar;
	console.log(pad);
}

function clear() {
  ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
  ctx.fillRect(0,0,canvas.width,canvas.height);
}

function main(uri) {
	canvas = document.getElementById('canvas');
	ctx = canvas.getContext('2d');
	
	adjustVerticalCentering(document.getElementsByClassName('canvas-container')[0], document.body.clientHeight, canvas.height);
	
	player1 = new paddle(10, 100, canvas.height-10, canvas.width/2., canvas.height-60);
    player2 = new paddle(10, 100, 0, canvas.width/2., 60);
	websocket = new WebSocket(uri);
	console.log(player1);
    //async handlers
	websocket.onopen = function (evt) {
		console.log("connection established");
	};
	
	websocket.onmessage = function (evt) {
		let msg = JSON.parse(evt.data);
        player1.x = msg['pos'][0][0];
        player1.score.value = msg['score'][0];
        player2.x = msg['pos'][1][0];
        player2.score.value = msg['score'][1];
        ball.x = msg['ball'][0];
        ball.y = msg['ball'][1];
        console.log(msg);
	};
	
	websocket.onerror = function (evt) {
		console.log(evt.data);
	};

	document.addEventListener('mousemove', function(e) {
		mouse.x = e.clientX - canvas.offsetLeft;
		mouse.y = e.clientY - canvas.offsetTop;
		
		if (mouse.y < 0) { mouse.y = 0; }
		if (mouse.x < 0) { mouse.x = 0; }
		if (mouse.y > canvas.height) { mouse.y = canvas.height; }
		if (mouse.x > canvas.width) { mouse.x = canvas.width; }

        let msg = {'pos': [mouse.x, mouse.y]};    
		websocket.send(JSON.stringify(msg));
	});

    //event loop
    interval = setInterval(draw, 1000. / fr);
}
function draw() {
	clear();
	player1.draw();
	player2.draw();
	ball.draw();
}
