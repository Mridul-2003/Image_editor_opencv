from flask import Flask, request, render_template, flash
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

# upload file settings
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"webp", "png", "jpg", "jpeg", "gif"}

# base dir
basedir = os.path.abspath(os.path.dirname(__file__))

# init flask app
app = Flask(__name__)
app.secret_key = "super secret key"

# apps upload folder
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# limiting allowed files
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# processing image
def processImage(filename, operation, x_value, y_value,brightness_value,contrast_value,x1_value,x2_value,y1_value,y2_value,text,fontScale,fontThickness):
    print(filename, operation)
    img = cv2.imread(f"{basedir}/uploads/{filename}")

    if operation == "cgray":
        name = filename
        imgProcessed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        newFile = f"{basedir}/static/{filename}"
        cv2.imwrite(newFile, imgProcessed)
        return name
    elif operation == "threshold_binary":
        name = filename
        img_read = cv2.imread(f"{basedir}/uploads/{filename}", cv2.IMREAD_GRAYSCALE)
        retval, img_thresh = cv2.threshold(img_read, x_value, y_value, cv2.THRESH_BINARY)
        newFile = f"{basedir}/static/{filename}"
        cv2.imwrite(newFile, img_thresh)
        return name
    elif operation == "Brightness":
        name = filename
        img_read = cv2.imread(f"{basedir}/uploads/{filename}", cv2.IMREAD_GRAYSCALE)
        img_rgb_brighter = np.clip(img + brightness_value, 0, 255).astype(np.uint8)
        newFile = f"{basedir}/static/{filename}"
        cv2.imwrite(newFile, img_rgb_brighter)
        return name
    elif operation == "Contrast":
        name = filename
        try:
            contrast_value = float(contrast_value)
        except ValueError:
            # Handle the case when contrast_value is not a valid number
            print("Contrast value is not a valid number.")
            return None
        contrast_value = np.clip(contrast_value, 0.1, 2.0)

        # Adjust contrast
        img_rgb_contrast = np.clip(img.astype(float) * contrast_value, 0, 255).astype(np.uint8)
        processed_img = cv2.cvtColor(img_rgb_contrast, cv2.COLOR_RGB2BGR)

        newFile = f"{basedir}/static/{filename}"
        cv2.imwrite(newFile, processed_img)
        return name
    elif operation == "DrawLine":

        name = filename
        try:
            x1_value = int(x1_value)
            y1_value = int(y1_value)
            x2_value = int(x2_value)
            y2_value = int(y2_value)
        except ValueError:
            flash("Invalid coordinate values. Please enter numeric values for drawing a line.")
            return render_template("index.html")

        lined_image = cv2.line(img, (x1_value, y1_value), (x2_value, y2_value), (0, 0, 255), thickness=10, lineType=cv2.LINE_AA)
        newFile = f"{basedir}/static/{filename}"
        cv2.imwrite(newFile, lined_image)
        return name
    elif operation == "DrawRectangle":
        name=filename
        imageRectangle = cv2.rectangle(img,(x1_value,y1_value),(x2_value,y2_value),(255,0,2),thickness=10,lineType=cv2.LINE_8)
        newFile = f"{basedir}/static/{filename}"
        cv2.imwrite(newFile, imageRectangle)
        return name
    elif operation == "WriteText":
        name = filename
        try:
            fontScale = float(fontScale)
        except ValueError:
            flash("Invalid font scale. Please enter a valid number.")
            return render_template("index.html")

        fontFace = cv2.FONT_HERSHEY_PLAIN
        fontColor = (0, 0, 255)
        fontthickness = fontThickness
        textimage = cv2.putText(img, text, (x_value, y_value), fontFace, fontScale, fontColor, fontthickness, cv2.LINE_AA)
        newFile = f"{basedir}/static/{filename}"
        cv2.imwrite(newFile, textimage)
        return name
    

# first web page
@app.route("/")
def home():
    return render_template("index.html")


# image editing
# image editing
@app.route("/edit", methods=["GET", "POST"])
def edit():
    operation = request.form.get("operation")
    x_value = request.form.get("xValue")
    y_value = request.form.get("yValue")
    brightness_value = request.form.get("brightnessValue")
    contrast_value = request.form.get("contrastValue")
    x1_value = request.form.get("x1Value")
    y1_value = request.form.get("y1Value")
    x2_value = request.form.get("x2Value")
    y2_value = request.form.get("y2Value")
    text = request.form.get("textvalue")
    fontScale = request.form.get("fontScale")
    fontThickness = request.form.get("fontThickness")
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file Submission")
            return render_template("index.html")
        file = request.files["file"]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == "":
            flash("No selected file")
            return render_template("index.html")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(basedir, app.config["UPLOAD_FOLDER"], filename))
            
            # Image processing
            try:
                brightness_value = int(brightness_value) if brightness_value else 0
                if x_value and y_value :
                    processedImg = processImage(filename, operation, int(x_value), int(y_value),brightness_value,contrast_value,0,0,0,0,text,fontScale,fontThickness)
                elif x1_value and y1_value and x2_value and y2_value:
                    processedImg = processImage(filename, operation,0,0,brightness_value,contrast_value,int(x1_value), int(x2_value),int(y1_value), int(y2_value),text,fontScale,fontThickness)
                else:
                    processedImg = processImage(filename, operation, 0,0,brightness_value,contrast_value,0,0,0,0,text,fontScale,fontThickness)  # Default values or handle as needed

                # flashing success message
                return render_template("index.html",img=processedImg)
            except ValueError:
                flash("Invalid brightness value. Please enter a number.")

    return render_template("index.html")



# runserver
app.run(debug=True)
