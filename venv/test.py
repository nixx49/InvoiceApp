@app.route('/analyze', methods=['POST'])
def analyze():
    # Placeholder for analyze logic
    # analyze_images()
    message = "Analyzing Completed"
    return render_template_string(HTML_TEMPLATE, message=message, show_download=True)


@app.route('/download', methods=['POST'])
def download():
    # Placeholder for download logic
    # download_images()
    return "Download initiated or completed (implement your logic)"


STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=documentdatabase;AccountKey=VaEiGqfB7HBIQzX95Ty4Y0PTs0Ob60kN/Xz6yg+vsAZwIkwXmJQH2/6iXM97suUfqJiY0hbwI4dR+AStBhQF2g==;EndpointSuffix=core.windows.net"
CONTAINER_NAME = "invoices"




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
    <div class="form-group">
        <label for="images">Choose Images</label>
        <input type="file" id="images" name="images" multiple onchange="showSelectedFiles()">
        <div id="selectedFiles" class="selected-files"></div>
    </div>
    <form action="/upload" method="post" enctype="multipart/form-data">
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