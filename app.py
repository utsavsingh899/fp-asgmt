from flask import Flask, render_template, request, url_for, send_file
import pandas as pd
import re


app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/upload', methods=['GET'])
def upload():
    return render_template('index.html')


@app.route('/options', methods=['POST'])
def filter():
    global df
    df = pd.read_excel(request.files.get('inputFile'))

    return render_template('options.html')


@app.route('/options/filter', methods=['POST'])
def download_filter():
    global df
    tests = df['Accepted Compound ID']

    if 'Rounded Retention Time (in min)' in df.columns:
        df = df.drop(
            columns=['Rounded Retention Time (in min)'])

    res = []
    for test in tests:
        x = re.findall("plasmalogen\Z", str(test))
        if x:
            res.append(True)
        else:
            res.append(False)
    df_pls = df[res]

    res = []
    for test in tests:
        x = re.findall("LPC\Z", str(test))
        y = re.findall("_LPC\Z", str(test))
        if x:
            res.append(True)
        elif y:
            res.append(True)
        else:
            res.append(False)
    df_LPC = df[res]

    res = []
    for test in tests:
        x = re.findall(" PC\Z", str(test))
        if x:
            res.append(True)
        else:
            res.append(False)
    df_PC = df[res]

    with pd.ExcelWriter('Filter_output.xlsx') as writer:
        df_pls.to_excel(writer, sheet_name='plasmalogen')
        df_LPC.to_excel(writer, sheet_name='LPC')
        df_PC.to_excel(writer, sheet_name='PC')

    return send_file('Filter_output.xlsx', as_attachment=True, attachment_filename='Filter_output.xlsx')


@app.route('/options/roundoff', methods=['POST'])
def download_roundoff():
    global df
    rounded_retention = df['Retention time (min)'].round()

    df_roundoff = df

    if 'Rounded Retention Time (in min)' in df_roundoff.columns:
        pass
    else:
        df_roundoff.insert(
            2, 'Rounded Retention Time (in min)', rounded_retention)

    with pd.ExcelWriter('Roundoff_output.xlsx') as writer:
        df_roundoff.to_excel(writer, sheet_name='Retention Time Roundoff')

    return send_file('Roundoff_output.xlsx', as_attachment=True, attachment_filename='Roundoff_output.xlsx')


@app.route('/options/mean', methods=['POST'])
def download_post():
    global df
    rounded_retention = df['Retention time (min)'].round()
    df_mean = df

    if 'Rounded Retention Time (in min)' in df_mean.columns:
        pass
    else:
        df_mean.insert(2, 'Rounded Retention Time (in min)', rounded_retention)

    df_mean = df_mean.drop(
        columns=['m/z', 'Retention time (min)', 'Accepted Compound ID'])

    df_mean = df_mean.groupby('Rounded Retention Time (in min)').mean()

    with pd.ExcelWriter('Mean_output.xlsx') as writer:
        df_mean.to_excel(writer, sheet_name='Mean')

    return send_file('Mean_output.xlsx', as_attachment=True, attachment_filename='Mean_output.xlsx')


if __name__ == '__main__':
    app.run(debug=True)
