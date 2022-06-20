import markdown

beginHtml = '''
<html>
<head>
<meta charset="UTF-8">
<title>2048音频版说明</title>
</head>
<body>
'''

endHtml = '''
</body>
</html>

'''

fp = open("readMe.md", encoding="UTF-8")
md = fp.read()
fp.close()
html = markdown.markdown(md)
fp = open("readMe.html", "wt", encoding="UTF-8")
fp.write(beginHtml + html + endHtml)
fp.close()
