from Grid import *
import Mapper

def test1():
	grid = Grid()
	grid.createPoints(100, 100)
	grid.createStations(100, "surface salinity", 500)

	analyzed_grid = Grid(analysis.Barnes(grid, "surface salinity", 5, 1, True))
	Mapper.map(analyzed_grid.getAttrList("surface salinity"))

def test2():
	grid = Grid()
	grid.createPoints(100, 100)
	grid.createStations(75, "surface salinity", 500)

	#creates 7 files (.4 <= gamma <= 1.0) each with 10 plots (1 <= alpha <= 10)
	for gamma in range(4,11):
		data_list = []
		titles    = []
		for alpha in range(1,11):
			analyzed_grid = Grid(analysis.Barnes(grid, "surface salinity", alpha, gamma*0.1, True))
			data_list.append((analyzed_grid.getAttrList("surface salinity")))
			titles.append("Interpolation with alpha = %s" % (alpha))
		Mapper.multiPlot(data_list, titles, "Gamma-%s.pdf" % (gamma))








if __name__ == "__main__":
	test2()