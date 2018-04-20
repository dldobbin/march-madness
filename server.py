from flask import Flask, render_template, request
import comparator

app = Flask(__name__)

@app.template_global(name='zip')
def _zip(*args, **kwargs):
	return zip(*args, **kwargs)

@app.route('/', methods=['GET'])
def index():
	year = request.args['year'] if 'year' in request.args else '2018'
	tourney = comparator.NCAA(year)
	prediction = tourney.chalk() if 'chalk' in request.args else tourney.sim()
	return render_template("index.html", year=int(year), actual=tourney.results, prediction=prediction['outcome'], score=prediction['score'])

if __name__ == '__main__':
	app.run(debug=True)