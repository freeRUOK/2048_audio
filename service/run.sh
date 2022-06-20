kill `ps uax | awk '/8890/{print $2}'`
nohup flask run -h 0.0.0.0 -p 8890 &

