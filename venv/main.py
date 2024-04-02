from flask import Flask, request, render_template_string, send_file
from azure.storage.blob import BlobServiceClient
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import datetime
from io import BytesIO
import json
import pandas as pd

app = Flask(__name__)

# Initialize Azure clients
STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=documentdatabase;AccountKey=VaEiGqfB7HBIQzX95Ty4Y0PTs0Ob60kN/Xz6yg+vsAZwIkwXmJQH2/6iXM97suUfqJiY0hbwI4dR+AStBhQF2g==;EndpointSuffix=core.windows.net"
CONTAINER_NAME = "invoices"
document_analysis_client = DocumentAnalysisClient(
    endpoint="https://eastasia.api.cognitive.microsoft.com/",
    credential=AzureKeyCredential("ace955c2cbcd4ba69dddca52ac5e48d4")
)
blob_service_client = BlobServiceClient.from_connection_string(
    STORAGE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

# Custom serializer for complex types


def custom_serializer(obj):
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif hasattr(obj, "__dict__"):
        return {attr: getattr(obj, attr) for attr in dir(obj) if not attr.startswith("_")}
    elif hasattr(obj, "value"):
        return obj.value
    else:
        return str(obj)


# HTML Template for the application
HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Processing with Azure</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #0a0f0d, #334455);
            color: #ffffff;
            text-align: center;
            padding: 20px;
        }
        h2 {
            color: #EFEFEF;
        }
        form {
            margin: 20px auto;
            display: inline-block;
            text-align: left;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group input[type=file] {
            display: none;
        }
        .form-group label {
            display: block;
            background: #5599ff;
            color: #fff;
            padding: 10px 20px;
            border-radius: 50px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .form-group label:hover {
            background: #3377cc;
        }
        .form-group input[type=submit] {
            background: #22cc88;
            border: 0;
            color: #fff;
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 50px;
            transition: background-color 0.3s ease;
        }
        .form-group input[type=submit]:hover {
            background: #33aa77;
        }
        .selected-files {
            margin-top: 10px;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
        }
        .file-capsule {
            background: #ffaa55;
            color: #ffffff;
            border-radius: 25px;
            padding: 5px 15px;
            margin: 5px;
            font-size: 14px;
        }
        footer {
            margin-top: 40px;
            color: #ddd;
        }
    </style>
</head>
<body>
    <h2>Invoice Analyzer</h2>
    {% if message %}
        <p>{{ message }}</p>
    {% endif %}

<form action="/upload" method="post" enctype="multipart/form-data">
    <!-- File Selection Group -->
    <div class="form-group">
        <label for="images">Choose Images</label>
        <input type="file" id="images" name="images" multiple onchange="showSelectedFiles()">
    </div>

    <!-- Selected Files Display Group -->
    <div class="form-group">
        <div id="selectedFiles" class="selected-files"></div>
    </div>

    <!-- Submit Button Group -->
    <div class="form-group">
        <input type="submit" value="Upload">
    </div>
</form>


    {% if show_analyze %}
        <form action="/analyze" method="post">
            <div class="form-group">
                <input type="submit" value="Analyze">
            </div>
        </form>
    {% endif %}

    {% if show_download %}
        <form action="/download" method="post">
            <div class="form-group">
                <input type="submit" value="Download">
            </div>
        </form>
    {% endif %}


    <div style="height: 300px;"></div> 
    <footer>
        <p>&copy; 2024 H One Private Limited. All rights reserved.</p>
    </footer>
    <script>
        function showSelectedFiles() {
            var input = document.getElementById('images');
            var output = document.getElementById('selectedFiles');
            var files = input.files;
            output.innerHTML = '';
            for (var i = 0; i < files.length; i++) {
                output.innerHTML += '<span class="file-capsule">' + files[i].name + '</span>';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def home():
    return render_template_string(HTML_TEMPLATE, message="Upload your files", show_analyze=False, show_download=False)


@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('images')
    if files:
        for file in files:
            if file.filename:
                blob_client = container_client.get_blob_client(file.filename)
                blob_client.upload_blob(file.read(), overwrite=True)
        message = "Upload Completed"
    else:
        message = "No files to upload."
    return render_template_string(HTML_TEMPLATE, message=message, show_analyze=True)


def analyze_document_and_convert_to_json(blob_client):
    download_stream = blob_client.download_blob().readall()
    stream = BytesIO(download_stream)
    poller = document_analysis_client.begin_analyze_document(
        "prebuilt-invoice", document=stream)
    result = poller.result()
    invoices_data = [invoice.fields for invoice in result.documents]
    json_data = json.dumps(
        invoices_data, default=custom_serializer, ensure_ascii=False, indent=4)
    return json_data


@app.route('/analyze', methods=['POST'])
def analyze():
    all_invoices_json_data = []
    try:
        for blob in container_client.list_blobs():
            blob_client = container_client.get_blob_client(blob)
            json_data = analyze_document_and_convert_to_json(blob_client)
            all_invoices_json_data.extend(json.loads(json_data))
        df = pd.json_normalize(all_invoices_json_data)
        df.to_csv('invoices_data.csv', index=False)
        message = "Analysis completed."
    except Exception as e:
        message = f"An error occurred: {str(e)}"
    return render_template_string(HTML_TEMPLATE, message=message, show_download=True)


@app.route('/download', methods=['POST'])
def download():
    csv_file_path = 'invoices_data.csv'
    try:
        return send_file(csv_file_path, as_attachment=True)
    except Exception as e:
        return f"An error occurred during download: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)
