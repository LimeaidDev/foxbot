from flask import Flask, send_file
import os
import boto3

app = Flask(__name__)

session = boto3.session.Session()


s3 = session.client(
    service_name='s3',
    aws_access_key_id="AKIAX7CRDYXPSUB7J2O3",
    aws_secret_access_key="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",
    region_name="us-east-1"
)

@app.route('/dwnld/<filename>')
def view_file(filename):

    filepath = f"data/imgtemp/{filename}.mp4"
    try:
        s3.download_file(Bucket='bucketeer-e38e36d5-84e1-4f15-ab16-7ce5be54dc9d', Key=f'ytdown/{filename}.mp4',
                       Filename=f"./data/imgtemp/{filename}.mp4")
        return send_file(filepath, as_attachment=True)


    except:
        return 'File not found', 404

if __name__ == "__main__":
    # app.run(debug=True)
    from waitress import serve

    serve(app, host="0.0.0.0", port=8080,)
