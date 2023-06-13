const mainCanvas = document.getElementById("pizarra");
const context = mainCanvas.getContext("2d");
context.fillStyle = "white";
context.fillRect(0, 0, mainCanvas.width, mainCanvas.height);
let initialX;
let initialY;

const dibujar = (cursorX, cursorY) => {
  context.beginPath();
  context.moveTo(initialX, initialY);
  context.lineWidth = 8;
  context.strokeStyle = "#000";
  context.lineCap = "round";
  context.lineJoin = "round";
  context.lineTo(cursorX, cursorY);
  context.stroke();

  initialX = cursorX;
  initialY = cursorY;
};

const mouseDown = (evt) => {
  initialX = evt.offsetX;
  initialY = evt.offsetY;
  dibujar(initialX, initialY);
  mainCanvas.addEventListener("mousemove", mouseMoving);
};

const mouseMoving = (evt) => {
  dibujar(evt.offsetX, evt.offsetY);
};

const mouseUp = () => {
  mainCanvas.removeEventListener("mousemove", mouseMoving);
};

mainCanvas.addEventListener("mousedown", mouseDown);
mainCanvas.addEventListener("mouseup", mouseUp);

var limpiar = document.getElementById("limpiar");
limpiar.addEventListener("click", function(){
    var canvas = document.getElementById("pizarra");
    var ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    context.fillStyle = "white";
    context.fillRect(0, 0, mainCanvas.width, mainCanvas.height);
});

var ocultar = document.getElementById("ocultar");
ocultar.addEventListener("click", function(){
    var canvas = document.getElementById("pizarra");
    var img = document.getElementById('contImg');
    var btnO = document.getElementById('ocultar');
    var btnM = document.getElementById('mostrar');
    var btnL = document.getElementById('limpiar');

    canvas.style.display = "none";
    img.style.display = "block";

    btnL.style.display = "none";
    btnO.style.display = "none";
    btnM.style.display = "inline";
});

var mostrar = document.getElementById("mostrar");
mostrar.addEventListener("click", function(){
    var canvas = document.getElementById("pizarra");
    var img = document.getElementById('contImg');
    var btnO = document.getElementById('ocultar');
    var btnM = document.getElementById('mostrar');
    var btnL = document.getElementById('limpiar');

    canvas.style.display = "block";
    img.style.display = "none";

    btnL.style.display = "inline";
    btnO.style.display = "inline";
    btnM.style.display = "none";
});