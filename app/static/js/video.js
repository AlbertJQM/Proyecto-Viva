var video = document.getElementById("myVideo");

// Detectar cuando el video ha terminado
video.onended = function() {
  // Realizar el cambio de página
  window.location.href = "http://localhost:5000/draw";
};
