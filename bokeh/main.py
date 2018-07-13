import bokeh.plotting
import bokeh.io
import pandas


d = pandas.read_csv('adbe.csv', parse_dates = ['Date'])



print(d)

f = bokeh.plotting.figure(width = 500, height = 250, x_axis_type = 'datetime', responsive = True)
f.line(d['Date'], d['Close'])


outFile = bokeh.io.output_file("Line.html")
bokeh.io.show(f)