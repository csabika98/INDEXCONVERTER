from flask import Flask, render_template, request, send_file
import re
import json
import csv

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    pattern = r'"_source"\s*:\s*({[^}]+})'

    # Read input text from uploaded file
    input_file = request.files['input_file']
    content = input_file.read().decode('utf-8')

    matches = []
    for match in re.finditer(pattern, content):
        matches.append(match.group(1))

    if matches:
        with open('output.txt', 'w') as file:
            file.write('[\n')
            for idx, match in enumerate(matches, start=1):
                file.write(match)
                if idx != len(matches):
                    file.write(',\n')
                else:
                    file.write('\n')
            file.write(']')

        try:
            with open('output.txt', 'r') as file:
                extracted_content = file.read()

            json_data = json.loads(extracted_content)

            if isinstance(json_data, list):
                csv_filename = 'output.csv'
                with open(csv_filename, 'w', newline='') as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=json_data[0].keys())
                    writer.writeheader()
                    writer.writerows(json_data)

                return render_template('download.html')

            else:
                return "Invalid JSON structure: Expected an array of objects"

        except json.JSONDecodeError as e:
            return f"JSON Decode Error: {e}"

    else:
        return "No matches found in the input file."

@app.route('/download')
def download():
    return send_file('output.csv', as_attachment=True)

@app.route('/download_json')
def download_json():
    return send_file('output.txt', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
