from flask import Flask, request, render_template, send_file, jsonify
import os
import requests
from zipfile import ZipFile, ZIP_DEFLATED

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    generated_html_files = []
    if request.method == 'POST':
        main_title = request.form.get('title')
        media_urls = request.form.getlist('media_url')
        media_types = request.form.getlist('media_type')
        poster_urls = request.form.getlist('poster_url')
        copy_texts = request.form.getlist('copywriting_text')

        media_data = []
        for i in range(len(media_urls)):
            media_entry = {"url": media_urls[i], "type": media_types[i]}
            if media_types[i] == "video":
                media_entry["poster_url"] = poster_urls[i]
            media_data.append(media_entry)

        output_dir = 'generated_html'
        media_dir = 'downloaded_media'
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(media_dir, exist_ok=True)

        html_template_video = """<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Embed, Preview, and Download Video</title>
            <style>
                .media-container {{
                    text-align: center;
                    margin: 20px;
                }}
                .download-link {{
                    margin-top: 10px;
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #4CAF50;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                }}
                .media-wrapper {{
                    position: relative;
                    width: 100%;
                    max-width: 560px;
                    margin: 0 auto;
                }}
                video {{
                    width: 100%;
                    height: auto;
                }}
            </style>
        </head>
        <body>
            <div class="media-container">
                <div class="media-wrapper">
                    <video id="mediaElement" controls poster="{poster_url}">
                        <source src="{url}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                </div>
                <br>
                <a href="{url}" class="download-link" id="downloadLink" download="{file_name}">Download Media-{number} (Video)</a>
            </div>
            <script>
                document.getElementById('downloadLink').addEventListener('click', function(e) {{
                    e.preventDefault();
                    var url = this.href;
                    var fileName = '{file_name}'; // Custom file name

                    var xhr = new XMLHttpRequest();
                    xhr.open('GET', url, true);
                    xhr.responseType = 'blob';
                    xhr.onload = function() {{
                        if (xhr.status === 200) {{
                            var blob = xhr.response;
                            var a = document.createElement('a');
                            a.href = window.URL.createObjectURL(blob);
                            a.download = fileName;
                            a.style.display = 'none';
                            document.body.appendChild(a);
                            a.click();
                            document.body.removeChild(a);
                        }}
                    }};
                    xhr.send();
                }});
            </script>
        </body>
        </html>
        """

        html_template_image = """<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Embed, Preview, and Download Image</title>
            <style>
                .media-container {{
                    text-align: center;
                    margin: 20px;
                }}
                .download-link {{
                    margin-top: 10px;
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #4CAF50;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                }}
                .media-wrapper {{
                    position: relative;
                    width: 100%;
                    max-width: 560px;
                    margin: 0 auto;
                }}
                img {{
                    width: 100%;
                    height: auto;
                }}
            </style>
        </head>
        <body>
            <div class="media-container">
                <div class="media-wrapper">
                    <img id="mediaElement" src="{url}" alt="Image Preview">
                </div>
                <br>
                <a href="{url}" class="download-link" id="downloadLink" download="{file_name}">Download Media-{number} (Image)</a>
            </div>
            <script>
                document.getElementById('downloadLink').addEventListener('click', function(e) {{
                    e.preventDefault();
                    var url = this.href;
                    var fileName = '{file_name}'; // Custom file name

                    var xhr = new XMLHttpRequest();
                    xhr.open('GET', url, true);
                    xhr.responseType = 'blob';
                    xhr.onload = function() {{
                        if (xhr.status === 200) {{
                            var blob = xhr.response;
                            var a = document.createElement('a');
                            a.href = window.URL.createObjectURL(blob);
                            a.download = fileName;
                            a.style.display = 'none';
                            document.body.appendChild(a);
                            a.click();
                            document.body.removeChild(a);
                        }}
                    }};
                    xhr.send();
                }});
            </script>
        </body>
        </html>
        """

        html_template_copywriting = """<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Copywriting Text {number}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    background-color: #f4f4f4;
                }}
                #container {{
                    width: 100%;
                    max-width: 600px;
                    height: auto;
                    padding: 20px;
                    background: white;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    border-radius: 10px;
                    text-align: center;
                }}
                #textToCopy {{
                    width: 100%;
                    padding: 10px;
                    overflow: hidden; /* Hide scroll bar */
                    resize: none; /* Prevent resizing */
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    margin-bottom: 10px;
                    box-sizing: border-box;
                    height: auto;
                }}
                #copyButton {{
                    padding: 10px 20px;
                    cursor: pointer;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    margin-top: 10px;
                    font-size: 16px;
                }}
                #notification {{
                    display: none;
                    margin-top: 10px;
                    padding: 10px;
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 5px;
                    position: fixed;
                    top: 10%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    z-index: 1000;
                }}
                @media (max-width: 600px) {{
                    #container {{
                        width: 100%;
                        margin: 10px;
                        padding: 10px;
                    }}
                    #copyButton {{
                        padding: 10px;
                        font-size: 14px;
                    }}
                }}
            </style>
        </head>
        <body>

        <div id="container">
            <textarea id="textToCopy" rows="10" cols="50">{copywriting_text}</textarea>
            <button id="copyButton">Copy to Clipboard</button>
            <div id="notification">Copied!</div>
        </div>

        <script>
            function adjustTextareaHeight() {{
                const textarea = document.getElementById('textToCopy');
                textarea.style.height = 'auto'; // Reset the height to auto
                textarea.style.height = textarea.scrollHeight + 'px'; // Set the height to the scrollHeight
            }}

            document.getElementById('copyButton').addEventListener('click', function() {{
                const textToCopy = document.getElementById('textToCopy');
                textToCopy.select();
                textToCopy.setSelectionRange(0, 99999); // For mobile devices
                document.execCommand('copy');

                const notification = document.getElementById('notification');
                notification.style.display = 'block';
                setTimeout(function() {{
                    notification.style.display = 'none';
                }}, 2000);
            }});

            // Adjust textarea height on page load
            window.addEventListener('load', adjustTextareaHeight);
            // Adjust textarea height when window is resized
            window.addEventListener('resize', adjustTextareaHeight);
            // Adjust textarea height when content is inputted
            document.getElementById('textToCopy').addEventListener('input', adjustTextareaHeight);
        </script>

        </body>
        </html>
        """

        generated_html_files = []
        for index, data in enumerate(media_data):
            url = data["url"]
            media_type = data["type"]
            tag = "video" if media_type == "video" else "photo"
            file_name = f"{main_title}_{index + 1}_{tag}.{'mp4' if media_type == 'video' else 'jpg'}"
            number = index + 1
            
            # Download media file
            media_response = requests.get(url)
            media_path = os.path.join(media_dir, file_name)
            with open(media_path, 'wb') as media_file:
                media_file.write(media_response.content)
            
            if media_type == "video":
                poster_url = data["poster_url"]
                html_content = html_template_video.format(url=url, poster_url=poster_url, file_name=file_name, number=number)
            elif media_type == "image":
                html_content = html_template_image.format(url=url, file_name=file_name, number=number)

            output_file_name = f"{output_dir}/{main_title}_{number}_{tag}.html"
            with open(output_file_name, 'w', encoding='utf-8') as file:
                file.write(html_content)
            generated_html_files.append({"file": output_file_name, "content": html_content})
            print(f"Generated HTML file for {media_type}: {output_file_name}")

        for index, text in enumerate(copy_texts):
            if text.strip():  # Check if the text is not empty
                number = len(media_data) + index + 1
                html_content = html_template_copywriting.format(copywriting_text=text, number=number)
                output_file_name = f"{output_dir}/{main_title}_{number}_copywriting.html"
                with open(output_file_name, 'w', encoding='utf-8') as file:
                    file.write(html_content)
                generated_html_files.append({"file": output_file_name, "content": html_content})
                print(f"Generated HTML file for copywriting text: {output_file_name}")

        # Create a zip file of all downloaded media files
        zip_file_name = os.path.join(output_dir, f"{main_title}_media.zip")
        with ZipFile(zip_file_name, 'w', ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(media_dir):
                for file in files:
                    zipf.write(os.path.join(root, file), file)
        print(f"Created zip file: {zip_file_name}")

        # Generate HTML file with link to download zip file
        html_bulk_download = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Download All Media</title>
            <style>
                .download-container {{
                    text-align: center;
                    margin: 20px;
                }}
                .download-link {{
                    margin-top: 10px;
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #4CAF50;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="download-container">
                <a href="{zip_file_name}" class="download-link" download>Download All Media</a>
            </div>
        </body>
        </html>
        """

        bulk_download_file = os.path.join(output_dir, "download_all.html")
        with open(bulk_download_file, 'w', encoding='utf-8') as file:
            file.write(html_bulk_download)
        print(f"Generated bulk download HTML file: {bulk_download_file}")

        return render_template('index.html', generated_html_files=generated_html_files)

    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join('generated_html', filename), as_attachment=True)

@app.route('/get_html_content', methods=['POST'])
def get_html_content():
    index = int(request.form['index'])
    with open(generated_html_files[index]['file'], 'r', encoding='utf-8') as file:
        html_content = file.read()
    return jsonify(html_content)

if __name__ == '__main__':
    app.run(debug=True)
