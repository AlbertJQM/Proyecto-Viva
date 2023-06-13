const btnStartRecord = document.getElementById('activar');
const btnStopRecord = document.getElementById('desactivar');
const texto = document.getElementById('texto');

let recognition = new webkitSpeechRecognition();
recognition.lang = 'es-ES';
recognition.continuous = true;
recognition.interimResults = false;

recognition.onresult = (event) => {
    const results = event.results;
    const frase = results[results.length - 1][0].transcript;
    texto.value += frase;
}
btnStartRecord.addEventListener('click', () => {
    recognition.start();
});

btnStopRecord.addEventListener('click', () => {
    recognition.abort();
});


/*para que te lo lea
document.getElementById('hablar').addEventListener("click",()=>{
    decodeURI(document.getElementById("texto").value);
});
function decir(texto){
    speechSynthesis.speak(new SpeechSynthesisUtterance)
}*/
