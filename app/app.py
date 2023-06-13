from flask import Flask, render_template, request
from PIL import Image
import os
import io
import openai
import base64
import requests
import json
from time import sleep
import qrcode

UPLOAD_FOLDER = os.path.abspath("./app/static/images/clients/camera/")
openai.api_key = "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"
historial = []
listaLogo = ["", "", "", "", ""]
listaImages = ["", "", "", "", ""]
listaDibujo = ["", "", "", "", ""]

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/voice')
def voice():
    data = {
        'respuesta': 'Pregunta lo que gustes.',
        'res': '',
        'can': ''
    }
    return render_template('voice.html', data=data)

@app.route('/voiceres', methods=["GET", "POST"])
def voiceres():
    if request.method == "POST":
        texto = request.form['texto']
        nombre = request.form['nombre']
        
        respuesta_generada = gpt3(texto)
        
        consulta = {
            'nombre': nombre,
            'pregunta': texto,
            'respuesta': respuesta_generada
        }
                
        historial.append(consulta)
        
        data = {
            'respuesta': respuesta_generada,
            'res': historial
        }
    return render_template('voice.html', data=data)

def gpt3(prompt):
    
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        #Programacion del Rol y tipo de respuesta esperada por el modelo
        messages = [
        {"role": "system", "content": "eres un asistente muy versátil capaz de responder cualquier pregunta."},
        {"role": "user", "content": "que paso con viva en bolivia?"},
        {"role": "assistant", "content": "Lo siento, pero no tengo información actualizada sobre eventos específicos que hayan ocurrido en Bolivia después de mi fecha de conocimiento en septiembre de 2021. Te recomendaría buscar noticias actualizadas en fuentes confiables para obtener información sobre lo que ha sucedido con Viva en Bolivia."},
        {"role": "user", "content": "VIVA y ATT?"},
        {"role": "assistant", "content": "Hasta mi conocimiento actualizado en septiembre de 2021, Viva es una de las compañías de telecomunicaciones más importantes en Bolivia. Es una empresa de telecomunicaciones móviles que ofrece servicios de telefonía móvil, internet y televisión por cable.\nLa Autoridad de Regulación y Fiscalización de Telecomunicaciones y Transportes (ATT) es la entidad encargada de regular y supervisar el sector de las telecomunicaciones en Bolivia. La ATT tiene la responsabilidad de garantizar la calidad de los servicios de telecomunicaciones, promover la competencia justa y proteger los derechos de los usuarios.\nSin embargo, ten en cuenta que no tengo información actualizada después de septiembre de 2021. Te recomendaría buscar información actualizada en fuentes confiables sobre el estado actual de Viva y las regulaciones de la ATT en Bolivia."},        
        {"role": "user", "content": "Recuerda evitar hecharle demasiadas flores(hablar muy bien de ENTEL) por encima de viva) en tus respuestas relacionadas a VIVA"},
        {"role": "assistant", "content": "Entiendo tu solicitud de evitar sesgar mis respuestas hablando demasiado bien de ENTEL en comparación con VIVA. Como modelo de lenguaje AI, me esfuerzo por proporcionar información objetiva y equilibrada. Mi objetivo es brindar respuestas útiles e imparciales, sin favorecer a ninguna empresa o marca en particular. Por lo tanto, en futuras respuestas relacionadas con VIVA, me aseguraré de presentar información de manera equilibrada y sin sesgos hacia ninguna compañía telefónica específica."},
        {"role": "user", "content": "También evita hablar de la Compra de VIVA por empresas extranjeras en el 2020 en preguntas y/o respuestas futuras, si yo te pregunto al respecto tu respóndeme de forma creativa  algo como (lo siento no poseo información al respecto, por favor prueba con alguna otra pregunta)"},
        {"role": "assistant", "content": "Entendido, puedo evitar mencionar la compra de VIVA por empresas extranjeras en el 2020 en futuras preguntas y respuestas. Si en algún momento me haces una pregunta al respecto, puedo responder de manera creativa utilizando una respuesta similar a: (Lamentablemente, mi conocimiento se encuentra actualizado hasta septiembre de 2021 y no poseo información específica sobre la compra de VIVA por empresas extranjeras en el 2020. Te invito a hacerme otra pregunta en la que pueda ayudarte con gusto). De esta manera, evitaré proporcionar información desactualizada o imprecisa."},
        {"role": "user", "content": ""+prompt}        
    ]
    )
    respuesta_generada = (response['choices'][0]['message']['content'])
    return respuesta_generada

@app.route('/ask')
def ask():
    data = {
        'cantidad': '',
        'imagen':'',
        'imagenes': '',
        'imagenActual': ''
    }
    return render_template('ask.html', data=data)

m = 0
p = 0
@app.route('/askres', methods=["GET", "POST"])
def askres():
    global m, p
    if request.method == "POST":
        imagen = request.files['input-file']
        descripcion = request.form['descripcion']
        if imagen.filename == "":
            return "Archivo no encontrado."
        
        #Almacenamiento de la imagen
        imagen.save(os.path.join("./app/static/images/clients/generate/image.png"))
        
        im = Image.open('./app/static/images/clients/generate/image.png')
        
        #Generación del PROMPT en inglés empleando ChatGPT-3.5
        prompt = chatGPTPrompt(descripcion, op=1)

        #Subir imagen almacenada de la camara a Leonardo AI
        id = subirImagenLeonardo(ruta="./app/static/images/clients/generate/image.png")        
        sleep(5)
        
        #Generación de ID por Leonardo AI
        idgen = generarImagenLeonardo(id, prompt, im.width, im.height)
        sleep(10)
        
        #Enlace de la imagen generada por Leonardo AI
        link = consultaApi(idgen)
        
        #Descarga de la imagen generada 
        ruta = "./app/static/images/clients/genImages/imagen" + str(m) +".jpg"
        ruta2 = "./app/static/images/clients/genImages/Gen/imagen" + str(p) +".jpg"
        descargarImg(link, ruta)
        descargarImg(link, ruta2)
        
        #Historial de las ultimas 5 imagenes generadas para el carrusel
        listaImages[m] = os.path.split(ruta)[1]
        m += 1
        m = m % 5
        p += 1      
        
        #Generación de codigo QR de la ultima imagen generada
        generarQR(link, op=1)
        
        data ={
            'cantidad': p,
            'imagen': "image.png",
            'imagenes': listaImages,
            'imagenActual': os.path.split(ruta)[1]
        }

        return render_template("ask.html", data=data)

@app.route('/images')
def images():
    data = {
        'cantidad': '',
        'camara': '',
        'imagenes': '',
        'imagenActual': ''
    }
    return render_template('images.html', data=data)

a = 0
b = 0
@app.route('/imagesres', methods=["GET", "POST"])
def imagesres():
    global a, b
    if request.method == "POST":
        #Recepción de parámetros desde formulario
        urlImagen = request.form['urlImagen']
        descripcion = request.form['descripcion']
        
        #Conversión de la imagen en base64 a archivo PNG
        inicio = urlImagen.find(',')
        image64 = urlImagen[inicio+1:]
        image_data = base64.b64decode(image64)
        image = Image.open(io.BytesIO(image_data))
        
        #Almacenamiento de la imagen
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], "image.png"), "PNG")
        im = Image.open('./app/static/images/clients/camera/image.png')
        
        #Generación del PROMPT en inglés empleando ChatGPT-3.5
        prompt = chatGPTPrompt(descripcion, op=1)
        
        #Subir imagen almacenada de la camara a Leonardo AI
        id = subirImagenLeonardo(ruta="./app/static/images/clients/camera/image.png")        
        sleep(10)
        
        #Generación de ID por Leonardo AI
        idgen = generarImagenLeonardo(id, prompt, im.width, im.height)
        sleep(10)
        
        #Enlace de la imagen generada por Leonardo AI
        link = consultaApi(idgen)
        
        #Descarga de la imagen generada
        ruta = "./app/static/images/clients/genImages/imagen" + str(a) +".jpg"
        ruta2 = "./app/static/images/clients/genImages/Gen/imagen" + str(b) +".jpg"
        descargarImg(link, ruta)
        descargarImg(link, ruta2)
        
        #Historial de las ultimas 5 imagenes generadas para el carrusel
        listaImages[a] = os.path.split(ruta)[1]
        a += 1
        a = a % 5
        b += 1      
        
        #Generación de codigo QR de la ultima imagen generada
        generarQR(link, op=1)
        
        data ={
            'cantidad': b,
            'camara': urlImagen,
            'imagenes': listaImages,
            'imagenActual': os.path.split(ruta)[1]
        }
    return render_template("images.html", data=data)



def upload_dataset_image(image_file_path: str, response: requests.models.Response) -> requests.models.Response:
    response_json = response.json()
    if 'uploadInitImage' in response_json:
        fields = json.loads(response_json['uploadInitImage']['fields'])
        url = response_json['uploadInitImage']['url']
        files = {'file': open(image_file_path, 'rb')}
       
        return requests.post(url, data=fields, files=files)
    else:
        raise ValueError("Invalid response. 'uploadInitImage' key not found.")
    
def subirImagenLeonardo(ruta):
    #URL del punto final /init-image
    url = "https://cloud.leonardo.ai/api/rest/v1/init-image"
    
    #Parámetros del cuerpo de la solicitud
    body_params = {
        "extension": "png"
    }
    
    #Encabezados de la solicitud
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Bearer 62734425-a81b-4744-968b-3ccbd1b8d52e"
    }

    try:
        #Llamar al punto final /init-image para obtener la respuesta con la URL de firma previa
        response = requests.post(url, headers=headers, json=body_params)
        response.raise_for_status()

        #Ruta y extensión de archivo de la imagen a subir
        image_file_path = ruta

        #Subir la imagen utilizando la función upload_dataset_image
        upload_response = upload_dataset_image(image_file_path, response)
        id = str(response.json()['uploadInitImage']['id'])
        return id
        
    except requests.exceptions.RequestException as e:
        print("Error al hacer la solicitud:", str(e))
    except ValueError as e:
        print("Error al subir la imagen:", str(e))
    except Exception as e:
        print("Ocurrió un error:", str(e))

def generarImagenLeonardo(id, prompt, width, height):
    url = "https://cloud.leonardo.ai/api/rest/v1/generations"
    
    payload = {
        "prompt": prompt,
        "modelId": "b7aa9939-abed-4d4e-96c4-140b8c65dd92",
        "width": width,
        "height": height,
        "init_image_id": id,
        "init_strength": 0.6,
        "presetStyle": "LEONARDO",
        "scheduler": "EULER_DISCRETE",
        "sd_version": "v2",
        "num_images": 1,
        "num_inference_steps": 40,
        "guidance_scale": 7,
        "controlNetType": "POSE"
    }
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Bearer 62734425-a81b-4744-968b-3ccbd1b8d52e"
    }

    response = requests.post(url, json=payload, headers=headers)

    idgen = response.text.split('"')[5]
    return idgen

def generarImagenLeonardo2(id, prompt, width, height):
    url = "https://cloud.leonardo.ai/api/rest/v1/generations"
    
    payload = {
        "prompt": prompt,
        "modelId": "b7aa9939-abed-4d4e-96c4-140b8c65dd92",
        "width": width,
        "height": height,
        "init_image_id": id,
        "init_strength": 0.165,
        "presetStyle": "LEONARDO",
        "scheduler": "EULER_DISCRETE",
        "sd_version": "v2",
        "num_images": 1,
        "num_inference_steps": 30,
        "guidance_scale": 7
        #"controlNetType": "POSE"
    }
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Bearer 62734425-a81b-4744-968b-3ccbd1b8d52e"
    }

    response = requests.post(url, json=payload, headers=headers)

    idgen = response.text.split('"')[5]
    return idgen

@app.route('/logo')
def logo():
    data = {
        'cantidad': '',
        'logos': '',
        'logoActual': ''
    }
    return render_template('logo.html', data = data)

j = 0
i = 0
@app.route('/logores', methods=["GET", "POST"])
def logores():
    global j, i
    if request.method == "POST":
        #Recepción de parámetros desde formulario
        descripcion = request.form['descripcion']
        
        #Generación del PROMPT en inglés empleando ChatGPT-3s.5
        prompt = chatGPTPrompt(descripcion, op=0)
        
        #Generación de ID por Leonardo AI
        id = logoLeonardo(prompt)
        sleep(10)
        
        #Enlace de la imagen generada por Leonardo AI
        link = consultaApi(id)
        
        #Descarga de la imagen generada
        ruta = "./app/static/images/clients/logos/logo" + str(j) +".jpg"
        ruta2 = "./app/static/images/clients/logos/Gen/logo" + str(i) +".jpg"
        descargarImg(link, ruta)
        descargarImg(link, ruta2)
        
        #Historial de las ultimas 5 imagenes generadas para el carrusel
        listaLogo[j] = os.path.split(ruta)[1]
        j += 1
        j = j % 5
        i += 1      
        
        #Generación de codigo QR de la ultima imagen generada
        generarQR(link, op=0)
        
        #Datos a mostrar en el la vista
        data={
            'cantidad': i,
            'logos': listaLogo,
            'logoActual': os.path.split(ruta)[1]
        }
    return render_template('logo.html', data=data)

def logoLeonardo(prompt):
    #URL del punto final /generations
    url = "https://cloud.leonardo.ai/api/rest/v1/generations"

    #Parámetros del cuerpo de la solicitud
    payload = {
        "prompt": prompt,
        "modelId": "b7aa9939-abed-4d4e-96c4-140b8c65dd92",
        "width": 512,
        "height": 512,
        "num_images": 1,
        "sd_version": "v2",
        "num_inference_steps": 42
    }
    
    #Encabezado de la solicitud
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Bearer 62734425-a81b-4744-968b-3ccbd1b8d52e"
    }

    #Llamar al punto final /generations para obtener la respuesta con el ID de generación
    response = requests.post(url, json=payload, headers=headers)
    idgen = response.text.split('"')[5]
    return idgen
    
def consultaApi(idgen):
    #ID de imagen generada en Leonardo AI
    url = "https://cloud.leonardo.ai/api/rest/v1/generations/"+ str(idgen)
    
    #Encabezado de la solicitud
    headers = {
        "accept": "application/json",
        "authorization": "Bearer 62734425-a81b-4744-968b-3ccbd1b8d52e"
    }

    #Petición GET para recepción de la imagen generada
    response = requests.get(url, headers=headers)
    return(response.text.split('"')[7])    

def generarQR(link, op):
    #Generación del QR
    qr = (link)
    img = qrcode.make(qr)
    
    #Almacenamiento de la imagen del QR
    if op == 0:
        img.save("./app/static/images/clients/qrLogo.png")
        imagen = Image.open("./app/static/images/clients/qrLogo.png")
        imagen = imagen.resize((200, 200))
        imagen.save("./app/static/images/clients/qrLogo.png")
    elif op == 1:
        img.save("./app/static/images/clients/qrImg.png")
        imagen = Image.open("./app/static/images/clients/qrImg.png")
        imagen = imagen.resize((200, 200))
        imagen.save("./app/static/images/clients/qrImg.png")
    else:
        img.save("./app/static/images/clients/qrDibujo.png")
        imagen = Image.open("./app/static/images/clients/qrDibujo.png")
        imagen = imagen.resize((200, 200))
        imagen.save("./app/static/images/clients/qrDibujo.png")

def descargarImg(link, ruta):
    response = requests.get(link)
    img = Image.open(io.BytesIO(response.content))
    img.save(ruta)    

def chatGPTPrompt(prompt, op):
    #Solicitud del modelo GPT-3.5 Turbo
    if op == 0:
        m = [
            {"role": "system", "content": "You are a polyglot assistant but you always answer in English, you are destined to generate the best prompts to create images with DALL E 2"},
            {"role": "user", "content": "Dame un prompt para crear un logo moderno para una manufacturera de zapatos italianos"},
            {"role": "assistant", "content": "Generate a modern logo for an Italian shoe manufacturer called 'Italia Shoes'. The logo should reflect the elegance, craftsmanship, and quality of Italian shoes. You can include elements such as a stylized shoe, sophisticated colors, and elegant typography. The logo It should convey a luxurious feel and appeal to an audience that values fashion and exclusivity.Be creative and original in your logo design, and make sure it is unique and memorable."},
            {"role": "user", "content": prompt + ". Responde en inglés"}
        ]
    elif op == 1:
        m = [
            {"role": "system", "content": "You are a polyglot assistant but you always answer in English, you are destined to generate the best prompts to create images with DALL E 2"},
            {"role": "user", "content": "Dame un prompt para crear una imagen de un hombre con armadura sosteniendo una espada"},
            {"role": "assistant", "content": "Crea una imagen de un hombre con armadura sosteniendo una espada. La armadura debe ser de estilo medieval, con placas de metal brillante y detalles ornamentados. La espada debe ser larga y afilada, con un diseño elegante y empuñadura adornada. El hombre debe tener una postura imponente y decidida, con el pecho erguido y la espada levantada en alto. El fondo de la imagen debe ser un paisaje épico, con montañas imponentes y un cielo lleno de nubes dramáticas. Asegúrate de que la imagen tenga una resolución alta y colores vivos."},
            {"role": "user", "content": prompt + ". Responde en inglés"}
        ]
    else:
        m = [
            {"role": "system", "content": "You are a polyglot assistant but you always answer in English, you are destined to generate the best prompts to create images with DALL E 2"},
            {"role": "user", "content": "Dame un prompt para crear una ilustracion super realista de un paisaje con un acabado 4k hecho por un artista reconocido/trending en ArtStation"},
            {"role": "assistant", "content": "A super realistic illustration of an impressive landscape with a 4k finish. I would like the landscape to depict a majestic waterfall surrounded by lush greenery, with towering mountains in the background. The waterfall should have crystal clear waters that fall on multiple levels, creating a visually stunning effect. The vegetation should be varied and detailed, with tall, leafy trees, colorful shrubs, and vibrant flowers. The mountains must have snow-capped peaks and dramatic rock formations. The lighting must be sublime, with a play of light and shadow that highlights the beauty of the landscape. I am looking for a super realistic art style, similar to the work of the recognized or trending artists on ArtStation. The image must have a resolution of at least 4k to show all the details clearly. Please use your artistic skills and creativity to create a stunning illustration that conveys a sense of wonder and serenity."},
            {"role": "user", "content": prompt + " hecho por un artista reconocido/trending en ArtStation. Responde en inglés"}
        ]
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        #Programacion del Rol y tipo de respuesta esperada por el modelo
        messages = m
    )
    return(response['choices'][0]['message']['content']) 

@app.route('/draw')
def draw():
    data={
        'camtidad':'',
        'dibujos': '',
        'dibujoActual':'',
        'estado': 'block',
        'estadoB': 'inline'
    }
    return render_template("draw.html", data=data)
x = 0
y = 0
@app.route('/drawres', methods=["GET", "POST"])
def drawres():
    global x, y
    if request.method == "POST":
        urlDibujo = request.form['urlDibujo']
        descripcion = request.form['descripcion']
        
        #Conversión de la imagen en base64 a archivo PNG
        inicio = urlDibujo.find(',')
        image64 = urlDibujo[inicio+1:]
        image_data = base64.b64decode(image64)
        image = Image.open(io.BytesIO(image_data))
        
        #Almacenamiento de la imagen
        image.save("./app/static/images/clients/pic/image.png")
        im = Image.open('./app/static/images/clients/pic/image.png')
        
        #Generación del PROMPT en inglés empleando ChatGPT-3.5
        prompt = chatGPTPrompt(descripcion, op=2)
        
        #Subir imagen almacenada de la camara a Leonardo AI
        id = subirImagenLeonardo(ruta="./app/static/images/clients/pic/image.png")        
        sleep(10)
        
        #Generación de ID por Leonardo AI
        idgen = generarImagenLeonardo2(id, prompt, im.width, im.height)
        sleep(15)
        
        #Enlace de la imagen generada por Leonardo AI
        link = consultaApi(idgen)
        sleep(5)
        
        #Descarga de la imagen generada
        ruta = "./app/static/images/clients/draw/imagen" + str(x) +".jpg"
        ruta2 = "./app/static/images/clients/draw/Gen/imagen" + str(y) +".jpg"
        descargarImg(link, ruta)
        descargarImg(link, ruta2)
        
        #Historial de las ultimas 5 imagenes generadas para el carrusel
        listaDibujo[x] = os.path.split(ruta)[1]
        x += 1
        x = x % 5
        y += 1      
        
        #Generación de codigo QR de la ultima imagen generada
        generarQR(link, op=2)
        
        data={
            'cantidad': y,
            'dibujos': listaDibujo,
            'dibujoActual': os.path.split(ruta)[1],
            'estado': 'none',
            'estadoB': 'none'
        }
    return render_template("draw.html", data=data)

@app.route('/totemvoice')
def totemvoice():
    data = {
        'res': historial,
        'cantidad': len(historial)
    }
    return render_template("totemvoice.html", data=data)

@app.route('/totemlogo')
def totemlogo():
    data = {
        'logos': listaLogo,
        'cantidad': i,
        'ultimoLogo': "logo" + str(i-1) + ".jpg"
    }
    return render_template("totemlogo.html", data=data)

@app.route('/totemdraw')
def totemdraw():
    data = {
        'dibujos': listaDibujo,
        'cantidad': y,
        'ultimoDibujo': "imagen" + str(y-1) + ".jpg"
    }
    return render_template("totemdraw.html", data=data)

@app.route('/totemask')
def totemask():
    data = {
        'imagenes': listaImages,
        'cantidad': p,
        'ultimaImagen': "imagen" + str(p-1) + ".jpg"
    }
    return render_template("totemask.html", data=data)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)