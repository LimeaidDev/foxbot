import flask
from flask import Flask, send_file, request, jsonify, render_template
import os
import boto3
import pytube
from pytube import YouTube
from pytube.exceptions import RegexMatchError
import datetime
from datetime import datetime, timedelta
import random
import string
import asyncio


app = Flask(__name__)

session = boto3.session.Session()


s3 = session.client(
    service_name='s3',
    aws_access_key_id="AKIAX7CRDYXPSUB7J2O3",
    aws_secret_access_key="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",
    region_name="us-east-1"
)

@app.route('/')
def home():
    return render_template('front.html')
    

@app.route('/dwnld/<filename>')
def view_file(filename):

    filepath = f"data/imgtemp/{filename}.mp4"
    try:
        s3.download_file(Bucket='bucketeer-e38e36d5-84e1-4f15-ab16-7ce5be54dc9d', Key=f'ytdown/{filename}.mp4',
                       Filename=f"./data/imgtemp/{filename}.mp4")
        return send_file(filepath, as_attachment=True)


    except:
        return 'File not found', 404


#if 'key' in request.args and request.args['key'] == 'apikey':


class YouTubeVideo:
    def __init__(self, givenUrl, v_id):
        self.givenUrl = givenUrl
        self.v_id = v_id

    async def download_video(self):
        try:
            yt = YouTube(self.givenUrl)
            video = yt.streams.filter(progressive=True).desc().first()
            title = yt.streams.filter(progressive=True).desc().first().title
            length = yt.length
            expiration_time = datetime.now() + timedelta(hours=1)
            if length <= 7200:
                td = timedelta(seconds=length)
                await asyncio.to_thread(video.download, "./data/imgtemp", filename_prefix="fox_", filename=f"{self.v_id}.mp4")
                s3.upload_file(Bucket='bucketeer-e38e36d5-84e1-4f15-ab16-7ce5be54dc9d', Key=f'ytdown/fox_{self.v_id}.mp4', Filename=f"./data/imgtemp/fox_{self.v_id}.mp4", ExtraArgs={'Expires': expiration_time})
                return "Success", 200
            else:
                return "Video is too long. Must be under 3 hours", 400
        except RegexMatchError as urlWrong:
            return "Invalid URL", 400
        except pytube.exceptions.AgeRestrictedError:
            return "This content is age restricted and can't be accessed", 400

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@app.route('/watch', methods=['GET', 'POST'])
async def watch():


    uniqueid = id_generator(14, string.hexdigits)

    try:
        video = YouTubeVideo(f'https://www.youtube.com/watch?v={request.args["v"]}', uniqueid)

        arg1, arg2 = await video.download_video()
        if arg2 == 400:
            return flask.render_template_string("Video is too long. Must be under 3 hours")
        elif arg2 == 200:
            return flask.redirect(f"/dwnld/fox_{uniqueid}")
    except:
        return flask.render_template_string("An error occurred"), 404

if __name__ == '__main__':
    # app.run(debug=True)
    from waitress import serve

    serve(app, host="0.0.0.0", port=8080)
