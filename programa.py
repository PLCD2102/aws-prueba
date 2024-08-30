from flask import Flask, render_template_string, jsonify
import boto3

app = Flask(__name__)

def get_buckets():
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    buckets = [{'Name': bucket['Name'], 'CreationDate': bucket['CreationDate']} for bucket in response['Buckets']]
    return buckets

def get_bucket_objects(bucket_name):
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket_name)
    objects = response.get('Contents', [])
    return [{'Key': obj['Key'], 'Size': obj['Size'], 'LastModified': obj['LastModified'].strftime("%Y-%m-%d %H:%M:%S")} for obj in objects]

@app.route('/')
def list_buckets_html():
    buckets = get_buckets()
    
    template = '''
    <html>
    <head>
        <style>
            .collapsible {
                background-color: #f1f1f1;
                color: #444;
                cursor: pointer;
                padding: 10px;
                width: 100%;
                border: none;
                text-align: left;
                outline: none;
                font-size: 15px;
            }

            .active, .collapsible:hover {
                background-color: #ccc;
            }

            .content {
                padding: 0 18px;
                display: none;
                overflow: hidden;
                background-color: #f9f9f9;
            }

            .bucket-content {
                padding-left: 20px;
            }
        </style>
    </head>
    <body>

    <h2>Lista de Buckets de S3</h2>
    <ul>
        {% for bucket in buckets %}
        <li>
            <button type="button" class="collapsible">{{ bucket.Name }}</button>
            <div class="content bucket-content" id="bucket-{{ bucket.Name }}">
                <p>Fecha de Creación: {{ bucket.CreationDate }}</p>
                <div class="objects-content"></div>
            </div>
        </li>
        {% endfor %}
    </ul>

    <script>
        var coll = document.getElementsByClassName("collapsible");
        for (var i = 0; i < coll.length; i++) {
            coll[i].addEventListener("click", function() {
                this.classList.toggle("active");
                var content = this.nextElementSibling;
                if (content.style.display === "block") {
                    content.style.display = "none";
                } else {
                    content.style.display = "block";
                    var objectsContent = content.querySelector('.objects-content');
                    if (objectsContent.innerHTML === "") {
                        var bucketName = this.innerText;
                        fetch('/bucket/' + bucketName)
                            .then(response => response.json())
                            .then(data => {
                                if (data.objects.length > 0) {
                                    var objectList = '<ul>';
                                    for (var j = 0; j < data.objects.length; j++) {
                                        var obj = data.objects[j];
                                        objectList += '<li><strong>' + obj.Key + '</strong><br>' +
                                                      'Tamaño: ' + obj.Size + ' bytes<br>' +
                                                      'Última modificación: ' + obj.LastModified + '</li><br>';
                                    }
                                    objectList += '</ul>';
                                    objectsContent.innerHTML = objectList;
                                } else {
                                    objectsContent.innerHTML = '<p>Este bucket está vacío.</p>';
                                }
                            });
                    }
                }
            });
        }
    </script>

    </body>
    </html>
    '''
    
    return render_template_string(template, buckets=buckets)

@app.route('/json')
def list_buckets_json():
    buckets = get_buckets()
    return jsonify(buckets=buckets)

@app.route('/bucket/<bucket_name>')
def get_bucket_info(bucket_name):
    objects = get_bucket_objects(bucket_name)
    return jsonify(objects=objects)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
