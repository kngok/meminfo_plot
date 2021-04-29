#!/usr/bin/env python3

import os
import sys
import cgi
import html
import pathlib
import tempfile
import base64

import cgitb
cgitb.enable()

html_head = """Content-Type: text/html

<!DOCTYPE html>
<html lang="ja">
  <head>
    <meta charset="UTF-8">
    <title>メモリ情報比較ツール</title>
    <style>
      dl.profile dt {{
        clear:left;
        position: relative;
        float: left;
        width: 10em;
        padding:5px 0px 0px 0px;
      }}
      dl.profile dd {{
        margin-left: 10em;
        width: 300px;
        padding: 5px 0px 5px 0px;
      }}
    </style>
  </head>
  <body>
    <h1>メモリ情報比較ツール</h1>

    <p>入力した 2 つのデータの変化割合をグラフ化します。<br>
       Linux の /proc/meminfo のフォーマットで入力してください。</p>

    <form action="meminfo_plot.cgi" method="post">
      <dl class="profile">
        <dt>縦軸の長さ</dt>
        <dd><input type="text" name="yaxis" value="{value_yaxis}"/></dd>

        <dt>グラフのタイトル</dt>
        <dd><input type="text" name="title" value="{value_title}"/></dd>
      </dl>

      <input type="submit" value="変換"/>
      <br><br>

      <div style="float:left; margin:5px">
        古いデータ<br>
        <textarea name="textarea_before" cols="50" rows="50">{value_textarea_before}</textarea>
      </div>

      <div style="float:left; margin:5px">
        新しいデータ<br>
        <textarea name="textarea_after" cols="50" rows="50">{value_textarea_after}</textarea>
      </div>

      <div style="clear:both;">
    </form>
"""
html_result = """
    <img src="data:image/png;base64,{img_data}" width="600">
"""

html_tail = """
  </body>
</html>
"""


def print_html(yaxis, title, textarea_before, textarea_after, msg=None):
    print(html_head.format(value_yaxis=yaxis, value_title=title,
                           value_textarea_before=textarea_before,
                           value_textarea_after=textarea_after))
    if msg:
        print(msg)
    print(html_tail)


def print_html_empty(yaxis, title, textarea_before, textarea_after):
    print_html(yaxis, title, textarea_before, textarea_after, None)


def print_html_error(yaxis, title, textarea_before, textarea_after):
    print_html(yaxis, title, textarea_before, textarea_after, '入力エラー')


def print_html_result(img_path, yaxis, title, textarea_before, textarea_after):
    img_data = image_file_to_base64(img_path)
    print_html(yaxis, title, textarea_before, textarea_after,
               html_result.format(img_data=img_data))


def create_tmpfile(write_data=None, suffix=None):
    with tempfile.NamedTemporaryFile(delete=False, dir="./data",
                                     suffix=suffix) as tf:
        if write_data:
            tf.write(write_data.encode())
        p = pathlib.Path(tf.name)
    return str(p.relative_to(p.cwd()))


def delete_tmpfile(files):
    for f in files:
        if os.path.exists(f):
            os.remove(f)


def delete_old_tmpfile(dir="./data", days=1):
    import datetime
    now = datetime.date.today()
    for f in os.listdir(dir):
        f = os.path.join(dir, f)
        mtime = datetime.date.fromtimestamp(os.stat(f).st_mtime)
        if (now - mtime).days >= days:
            os.remove(f)


def image_file_to_base64(path):
    with open(path, 'rb') as f:
        data = base64.b64encode(f.read())
    return data.decode('utf-8')


field = cgi.FieldStorage()

data_yaxis = field.getvalue('yaxis', '3.0')
data_title = field.getvalue('title', '')

text_before = field.getfirst('textarea_before', '')
data_before = html.escape(text_before).strip()

text_after = field.getfirst('textarea_after', '')
data_after = html.escape(text_after).strip()

if data_before == '' and data_after == '':  # empty input
    print_html_empty(data_yaxis, data_title, data_before, data_after)
    sys.exit()
elif data_before == '' or data_after == '':
    print_html_error(data_yaxis, data_title, data_before, data_after)
    sys.exit()

tmp_before = create_tmpfile(data_before)
tmp_after = create_tmpfile(data_after)
tmp_image = create_tmpfile(suffix=".png")

try:
    import meminfo_plot as mp
    df = mp.read_data(tmp_before, tmp_after)
    mp.plot(df, tmp_image, data_title, False, float(data_yaxis))
    print_html_result(tmp_image, data_yaxis, data_title, data_before, data_after)
except:
    print_html_error(data_yaxis, data_title, data_before, data_after)

delete_tmpfile([tmp_before, tmp_after])
delete_old_tmpfile()
