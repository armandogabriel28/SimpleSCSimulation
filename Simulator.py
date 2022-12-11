from SimLogic import SimObjects
from SimData import DemandData, StoreData, TransitTimeData


class Simulator:

	def __init__(self, inputFileName, warmUpDays, simDays):
		self.inputFileName = inputFileName  # set the file name for the input data
		self.warmUpDays = warmUpDays  # length of warm up period where results will be discarded
		self.simDays = simDays  # length of simulation where results will be reported

	def buildModel(self):
		SimObjects.resetObjects()  # reset the global simulation variables before building
		# create list of tables to read/process, StoreData must go before DemandData because DemandProduct object need a reference to the Store that will fulfill its demand
		dataTableList = [StoreData(), DemandData(), TransitTimeData()]
		for dataTable in dataTableList:
			dataTable.read(self.inputFileName)
			dataTable.buildSimObjects()

	def runSimulation(self):

		for day in range(self.simDays + self.warmUpDays):
			for custName, customer in SimObjects.customerLookup.items():
				customer.checkOrderReceipt()  # customer starts the day by checking if previous orders have been fulfilled
			for custName, customer in SimObjects.customerLookup.items():
				customer.placeOrder()  # customer finishes day by placing new orders
			for storeName, store in SimObjects.storeLookup.items():
				store.checkOrderReceipt()  # store starts day by checking if previous orders sent to supplier have been received
				store.fillOrders()  # store next attempts to fill backlogged orders and newly received orders
				store.placeReorder()  # store finishes day by placing new orders to supplier based on inventory levels
			SimObjects.currentTime += 1

	def generateOutput(self):

		leadTimeResultDict = {}
		totalOrders = 0
		totalQuantity = 0
		for customer in SimObjects.customerLookup.values():
			for demandProduct in customer.demandProductList:
				for order in demandProduct.closedOrders:
					if order.timeCreated >= self.warmUpDays:
						totalOrders += 1
						totalQuantity += order.quantity
						leadTime = order.timeOfReceipt - order.timeCreated
						if leadTime in leadTimeResultDict:
							resultValues = leadTimeResultDict[leadTime]
							resultValues[0] += 1
							resultValues[1] += order.quantity
						else:
							resultValues = [1, order.quantity]
							leadTimeResultDict[leadTime] = resultValues

		leadTimeResultList = [(leadTime, resultValues[0], resultValues[1]) for leadTime, resultValues in leadTimeResultDict.items()]
		leadTimeResultList.sort()
		print('Lead Time\t\t% of Orders\t\t% of Quantity')
		for (leadTime, orderCount, OrderQuantity) in leadTimeResultList:
			print('%d\t\t\t\t%.03f\t\t\t%.03f' % (leadTime, orderCount/totalOrders, OrderQuantity/totalQuantity))


if __name__ == "__main__":
	simulator = Simulator(inputFileName='SampleData.xlsx', warmUpDays=28, simDays=365)
	simulator.buildModel()
	simulator.runSimulation()
	simulator.generateOutput()
