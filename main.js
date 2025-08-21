const context = canvas.getContext('2d');

let x = 0;
let y = 0;


function update() {
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.fillStyle = 'blue';
    context.beginPath();
    context.fillRect(x, y, 50, 50);
    context.stroke();
    requestAnimationFrame(update);
}

window.onmousemove = function(e) {
    x = e.x
    y = e.y
}

requestAnimationFrame(update);