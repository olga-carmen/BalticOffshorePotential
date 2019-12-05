import random, json
import psycopg2
from flask import Flask, render_template, request, redirect, Response, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/receiver', methods = ['POST'])
def worker():
    print("Sending POST request")
    data = request.get_json(force=True)
    wB = data[0]['wB']
    wS = data[1]['wS']
    wW = data[2]['wW']
    conn = psycopg2.connect("dbname='Baltic_project' \
                             host='localhost' \
                             user='postgres' \
                             password='postgres'")

    cur = conn.cursor()
    cur.execute("""UPDATE grid_data
                   SET fuzzyvalue = (bathmean * {}) + (shipmean * {}) + (windmean * {})
                   WHERE (pareasmean = 0 AND bufformean = 0);""".format(wB, wS, wW))

    conn.commit()

    cur.execute("""SELECT id, fuzzyvalue, ST_AsGeoJSON(geom)
                   FROM grid_data
                   ;""")

    rows = cur.fetchall()

    output = """{
      "type": "FeatureCollection",
      "features": ["""

    for row in rows:

        output = output + '''{
          "type": "Feature",
          "properties": {
              "id": '''+str(row[0])+''',
              "fuzzyvalue": '''+str(row[1])+'''},
          "geometry": '''+row[2]+'''
        },'''


    output = output[:-1] + """]
      }"""

    cur.close()
    conn.close()

    #print(output)

    #create an empty geojson file and overwrite it with the output
    f = open(r"C:\Users\apatsi19\Desktop\PROJECT\Web Application\static\output.geojson", "w+")
    f.write(output)
    f.close()


    return jsonify(output)
#    """Response(response=output, status=200, mimetype="application/json")"""


TEMPLATES_AUTO_RELOAD = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

if __name__ == "__main__":
    app.run(debug=True)