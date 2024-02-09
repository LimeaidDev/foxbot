from flask import Flask, send_file
import os

app = Flask(__name__)

@app.route('/dwnld/<filename>')
def view_file(filename):

    filepath = f'./data/imgtemp/fox_{filename}.mp4'

    if os.path.exists(filepath):
        return send_file(filepath)

    else:
        return 'File not found', 404

if __name__ == "__main__":
    # app.run(debug=True)
    from waitress import serve

    serve(app, host="0.0.0.0", port=8080,)
