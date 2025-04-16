from flask import Flask, render_template, request
import os
import math
import re

app = Flask(__name__)

UPLOAD_FOLDER = 'upload'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_text_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        return "Файл не найден."

    words = re.findall(r'\b\w+\b', text.lower())
    word_counts = {}
    for word in words:
        word_counts[word] = word_counts.get(word, 0) + 1

    total_words = len(words)
    tf_scores = {word: count / total_words for word, count in word_counts.items()}

    num_documents = 1
    idf_scores = {word: math.log(num_documents / 1) for word in tf_scores}

    word_data = []
    for word in tf_scores:
        word_data.append({'word': word, 'tf': tf_scores[word], 'idf': idf_scores[word]})

    sorted_word_data = sorted(word_data, key=lambda x: x['idf'], reverse=True)
    return sorted_word_data[:50]

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('upload.html', error="Файл не выбран")

        file = request.files['file']


        if file.filename == '':
            return render_template('upload.html', error="Файл не выбран")

        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            results = process_text_file(filepath)
            return render_template('result.html', results=results)
        else:
            return render_template('upload.html', error="Недопустимый тип файла. Разрешены только файлы .txt")

    return render_template('upload.html', error=None)

if __name__ == '__main__':
    app.run(debug=True)
