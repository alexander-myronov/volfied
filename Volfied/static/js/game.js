var socket = new io.Socket();
var controls = {up:false, down:false, left:false, right:false, space:false};

var canvas = null;
var ctx = null;
var x = 50, y =50;
var worldsize = {width:500, height:500}

function resize()
{
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

function update()
{
    window.requestAnimationFrame(update);
    //game.tick();
    var delta = Date.now() - lastUpdateTime;
    if (acDelta > msPerFrame)
    {
        acDelta = 0;
        socket.send(JSON.stringify(controls));
	    redraw();
    }

    else
    {
        acDelta += delta;
    }

    lastUpdateTime = Date.now();
}

function connect() {
    socket.on('connect', function() {
            //alert('connected');
            socket.subscribe('echo');
            //socket.send('message');
        });
        //socket.on('subscribe', function(){
        //    alert('subscribed');
        //    //socket.send('message')
        //});

        socket.on('message', function(msg)
        {

            var newPos = JSON.parse(msg);
            x = newPos.x;
            y = newPos.y;
        });

        socket.connect();
}


function redraw()
{

    ctx.save();
    ctx.translate(0.5, 0.5);
    ctx.scale(canvas.width/worldsize.width,canvas.height/worldsize.height);


    ctx.fillStyle = "aqua";
    ctx.fillRect(0, 0, worldsize.width, worldsize.height)



    ctx.beginPath();
    ctx.arc(x,y, 20, 0, 2*Math.PI)
    ctx.fillStyle = 'blue';
    ctx.fill();
    ctx.stroke();

    ctx.restore();
}

function worldToScreenX(x)
{
    return (x / worldsize.x) * canvas.width;
}

function worldToScreenX(y)
{
    return (y / worldsize.y) * canvas.height;
}

function setup_controller(){

        document.onkeydown = function(e){controls[mapKey(e)] = true;};
        document.onkeyup = function(e){controls[mapKey(e)] = false;};
}




function mapKey(e) {

    e = e || window.event;

    if (e.keyCode == '38') {
        return 'up';
    }
    else if (e.keyCode == '40') {
        return 'down'
    }
    else if (e.keyCode == '37') {
       return 'left'
    }
    else if (e.keyCode == '39') {
       return 'right'
    }
}