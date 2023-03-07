###### old

from flask import Flask, render_template, redirect, request, send_from_directory, url_for
#importato per immagini
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
#per riconoscimento
import os
import cv2
import numpy as np
import base64
#########

import cv2
import mediapipe as mp
import matplotlib.pyplot as plt

###non toccato, per caricare l'immagine


app = Flask(__name__)
#db_path = "//home/capanos/mysite/database.db" db su pythonever
#aggiunto per caricamento
app.config['SECRET_KEY'] = 'jkhljhkjjhkjhhkdzzc'
app.config['UPLOADED_PHOTOS_DEST'] ='uploads'

photos =UploadSet('photos', IMAGES)
configure_uploads(app, photos)
#app = Flask(__name__, static_url_path='/static') ###eliminami anche cartella static

################################################
risultatoappoggio = "/upload/human-pose-estimation-cover.jpg"   ###provo ad associargli un valore all'interno del def



class UploadForm(FlaskForm):
    photo = FileField(
        validators=[
            FileAllowed(photos, "Solo Immagini"),
            FileRequired("Il campo non può essere vuoto")
        ]
    )
    submit = SubmitField('Carica!')


@app.route('/')
def index():
    #connection = sqlite3.connect('database.db')

    # organizza il db in righe
    # connection.row_factory = sqlite3.Row
    # # chiama i comandi SQL e e li mette in lista pithon
    # posts = connection.execute('SELECT * FROM posts').fetchall()
    # connection.close()
    # # va mandato a html col parametro (primo posts e la seconda variabile)
    return render_template('index.html')


# non toccare va! guarda la parte html


@app.route('/<int:idx>/delete', methods=("POST",))
def delete(idx):
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    connection.execute('DELETE FROM posts WHERE id=?', (idx,))
    connection.commit()
    connection.close()
    return redirect('/')


@app.route('/crea.html', methods=("GET", "POST"))
def crea():
    if request.method == 'POST':
        titolo = request.form['titolo']
        info = request.form['info']
        connection = sqlite3.connect('database.db')
        connection.row_factory = sqlite3.Row
        connection.execute(
            'INSERT INTO posts (titolo, info) VALUES (?, ?)', (titolo, info)
        )
        connection.commit()
        connection.close()
        return redirect('/')
    return render_template('crea.html')


# carica file nella stessa pagina
@app.route('/upload/<filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)


@app.route('/movenze.html', methods=['GET', 'POST'])
def upload_image():
    ################################################pose
    ####inizializza
    mp_pose = mp.solutions.pose

    pose_image = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)

    pose_video = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.7,
                              min_tracking_confidence=0.7)

    mp_drawing = mp.solutions.drawing_utils

    # definisce posa
    def detectPose(image_pose, pose, draw=False, display=False):
        original_image = image_pose.copy()
        image_in_RGB = cv2.cvtColor(image_pose, cv2.COLOR_BGR2RGB)

        resultant = pose.process(image_in_RGB)
        if resultant.pose_landmarks and draw:
            mp_drawing.draw_landmarks(image=original_image, landmark_list=resultant.pose_landmarks,
                                      connections=mp_pose.POSE_CONNECTIONS,
                                      landmark_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255),
                                                                                   thickness=3, circle_radius=3),
                                      connection_drawing_spec=mp_drawing.DrawingSpec(color=(49, 125, 237),
                                                                                     thickness=2, circle_radius=2))
        #print("filename")
        #print (filename)
        if display:

            plt.figure(figsize=[22, 22])
            plt.subplot(121);
            plt.imshow(image_pose[:, :, ::-1]);
            plt.title("Input Image");
            plt.axis('off');
            plt.subplot(122);
            plt.imshow(original_image[:, :, ::-1]);
            appoggiosalvataggio = "static/"+filename
            plt.imsave(appoggiosalvataggio, original_image[:, :, ::-1]);# ok togliere la parte risultato appoggio
            plt.title("Pose detected Imagedentro");
            plt.axis('off');
            # plt.draw();  ###
            # plt.pause();  ###
            # plt.close();  ###
            global risultatoappoggio ### chiamo la variabile globale### va giu
            risultatoappoggio = "static/"+filename  # do valore alla variabile globale
            #print (risultatoappoggio)
            #print(risultatoappoggio)
            #print("original image")  ###
            # cv2.imshow("", original_image) ### qui è il show non corretto dell'img
            # cv2.waitKey(0)  ###
        else:
            return original_image, results

    form = UploadForm()
    if form.validate_on_submit():  # abbreviazione per validate is true e submit is true
        filename = photos.save(form.photo.data)
        file_url = url_for('get_file', filename=filename)
        #print(file_url) #è lindirizzo dell'immagine caricata senza apici qui è da vedere se rimetterlo
        stringa = "uploads/"+ filename
        #print (stringa)
        image_path = str(stringa)
        output = cv2.imread(image_path)
        detectPose(output, pose_image, draw=True, display=True)
        #risultatoappoggio = "/sample3.jpg"####
        # print ("risultatoappoggio")
        # print (risultatoappoggio)

    else:
        file_url = None
        output = "uploads/human-pose-estimation-cover.jpg"

    return render_template('movenze.html', form=form, file_url=file_url, risultatoappoggio = risultatoappoggio)


##############################
if __name__ == "__main__":
    # Only for debugging while developing
#    app.run(host='0.0.0.0', debug=True, port=80) #era 80
