from flask import Flask, render_template, request

app = Flask(__name__)


# Boyer-Moore search algorithm
def boyer_moore(text, pattern):
    n = len(text)
    m = len(pattern)

    # pre-processing
    skip = {}
    for i in range(m):
        skip[pattern[i]] = m - i - 1

    # search
    i = m - 1
    while i < n:
        j = m - 1
        while text[i] == pattern[j]:
            if j == 0:
                return i
            i -= 1
            j -= 1
        i += max(skip.get(text[i], m), m - j)

    return -1


# function to highlight keyword in a line of text
def highlight_keyword(line, keyword):
    return line.replace(keyword, '<span style="background-color: yellow; font-weight: bold;">{}</span>'.format(keyword))




@app.route('/')
def index():
    return render_template('file_upload.html')


@app.route('/result', methods=['POST'])
def result():
    keyword = request.form['keyword']
    file = request.files['file']

    if file.filename == '':
        return render_template('file_upload.html', error='Please select a file.')

    if not file.filename.endswith('.txt'):
        return render_template('file_upload.html', error='File must be a text file (.txt).')

    try:
        # read the text file and decode using utf-8
        text = file.read().decode('utf-8')
    except UnicodeDecodeError:
        # if an error occurs during the file reading process, return an error message
        return render_template('file_upload.html', error='Invalid file format. File must be UTF-8 encoded.')

    # perform search using Boyer-Moore algorithm
    index = boyer_moore(text, keyword)

    if index != -1:
        # highlight the keyword in the text
        lines = text.split('\n')
        highlighted_lines = []
        for line in lines:
            highlighted_line = highlight_keyword(line, keyword)
            highlighted_lines.append(highlighted_line)
        return render_template('result.html', keyword=keyword, text='\n'.join(highlighted_lines))
    else:
        return render_template('result.html', keyword=keyword, text=None)


if __name__ == '__main__':
    app.run(debug=True)
