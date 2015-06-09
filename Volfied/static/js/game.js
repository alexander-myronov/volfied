var socket = new io.Socket();
var controls = [0, 0, 0, 0]


var canvas = null;
var ctx = null;
var state = null;
var worldsize = {width: 100, height: 100}
var radius = 4
var rectangles = null;

function resize() {
    //if(canvas===null)return;
    //canvas.width = canvas.parentNode.clientWidth;
    //canvas.height = canvas.parentNode.clientHeight;


}

window.onload = function () {


    canvas = document.getElementById('gameCanvas');
    ctx = canvas.getContext("2d");

    connect();
    setup_controller();
    window.requestAnimationFrame(update);
    resize();
};

var lastUpdateTime = 0;
var acDelta = 0;
var msPerFrame = 2;

function update() {
    window.requestAnimationFrame(update);
    //game.tick();
    var delta = Date.now() - lastUpdateTime;
    if (acDelta > msPerFrame) {
        acDelta = 0;
        socket.send(JSON.stringify(controls));
        redraw();
    }

    else {
        acDelta += delta;
    }

    lastUpdateTime = Date.now();
}

function connect() {
    socket.on('connect', function () {
        //alert('connected');
        socket.subscribe('echo');
        //socket.send('message');
    });


    socket.on('message', function (msg) {

        if (msg == null) return;
        var obj = JSON.parse(msg);
        if (obj.cmd === 'init') {
            worldsize.width = obj.dimensions[0];
            worldsize.height = obj.dimensions[1];
            radius = obj.radius;
            rectangles = obj.active_rectangles;
            state = null;
        }
        else if (obj.cmd === 'tick') {
            if (obj.hasOwnProperty('active_rectangles')) {
                rectangles = obj.active_rectangles
            }
            state = obj;
        }


    });

    socket.connect();
}


function redraw() {

    ctx.save();
    ctx.translate(0.5, 0.5);
    ctx.scale(canvas.width / worldsize.width, canvas.height / worldsize.height);


    ctx.fillStyle = "aqua";
    ctx.fillRect(0, 0, worldsize.width, worldsize.height)

    if (state !== null) {


        ctx.fillStyle = '#AEB23C';
        var i;
        for (i = 0; i < rectangles.length; i++) {
            var rect = rectangles[i];
            ctx.beginPath();

            ctx.rect(rect[0][0], rect[0][1],
                rect[1][0] - rect[0][0], rect[1][1] - rect[0][1]);
            ctx.fill();
            ctx.stroke();

        }

        ctx.strokeStyle = 'yellow';
        if (state.line.length > 1) {
            ctx.beginPath();
            ctx.moveTo(state.line[0][0], state.line[0][1]);

            for (i = 1; i < state.line.length; i++) {
                ctx.lineTo(state.line[i][0], state.line[i][1]);
            }
            ctx.stroke();

        }

        ctx.strokeStyle = "#6AFF77";
        ctx.fillStyle = '#CC4540';
        for (i = 0; i < state.enemies.length; i++) {
            var e = state.enemies[i];
            ctx.beginPath();
            ctx.arc(e.x, e.y, e.radius, 0, 2 * Math.PI);
            ctx.fill();
            ctx.stroke();
        }

        if (state.on_active == true && state.shield > 0)
            ctx.strokeStyle = '#F9FF6A';
        else
            ctx.strokeStyle = 'transparent';
        ctx.beginPath();
        ctx.arc(state.x, state.y, radius, 0, 2 * Math.PI)
        ctx.fillStyle = '#2874B2';
        ctx.fill();
        ctx.stroke();

        ctx.font = "5px Arial";
        ctx.fillStyle = "black"

        ctx.textBaseline = "top";
        ctx.textAlign = "left";
        ctx.fillText("Shield: " + state.shield, 1, 0);

        ctx.textAlign = "center";
        ctx.fillText("Lives: " + Math.max(state.lives, 0), worldsize.width/2, 0);

        ctx.textAlign = "right";
        ctx.fillText("Score: " + state.score, worldsize.width-1,0);

        if (state.hasOwnProperty('status') && state.status != 0) {
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.font = "30px Arial";
            var text = "";
            if (state.status === 1) {
                text = "WIN";
            }
            else if (state.status === -1) {
                text = "LOSE";
            }
            ctx.fillText(text, worldsize.width / 2, worldsize.height / 2);
        }
    }

    ctx.restore();
}

function worldToScreenX(x) {
    return (x / worldsize.width) * canvas.width;
}

function worldToScreenY(y) {
    return (y / worldsize.height) * canvas.height;
}

function setup_controller() {

    document.onkeydown = function (e) {
        controls[mapKey(e)] = 1;
    };
    document.onkeyup = function (e) {
        controls[mapKey(e)] = 0;
    };
}


function mapKey(e) {

    e = e || window.event;

    if (e.keyCode == '38') {
        return 0;
    }
    else if (e.keyCode == '40') {
        return 1
    }
    else if (e.keyCode == '37') {
        return 2
    }
    else if (e.keyCode == '39') {
        return 3
    }
}