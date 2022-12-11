import pandas as pd

from SimLogic import SimObjects, Customer, DemandProduct, Store, InventoryProduct


# abstract class providing the structure for data tables and the generalize read method
class DataTable:

	def __init__(self):
		self.tableName = None
		self.keyNames = []
		self.keyToValues = {}

	def read(self, fileName):
		dataFrame = pd.read_excel(fileName, self.tableName)
		data = dataFrame.values.tolist()
		for row in data:
			keyTuple = tuple(row[:len(self.keyNames)])
			valueList = row[len(self.keyNames):]
			self.keyToValues[keyTuple] = valueList  # builds a dictionary mapping a tuple of the key values to the list of values for the row

	def buildSimObjects(self):
		pass


class DemandData(DataTable):

	def __init__(self):
		DataTable.__init__(self)
		self.tableName = 'Demand'
		self.keyNames = ['Customer', 'Product']
		self.fieldToIndex = {'DemandMin': 0, 'DemandMax': 1, 'DemandMode': 2, 'AssignedStore': 3}
		self.keyToValues = {}

	def buildSimObjects(self):
		SimObjects.customerLookup = {}
		for key, valueList in self.keyToValues.items():
			(custName, prodName) = key
			# get values from value list
			demandMin = valueList[self.fieldToIndex['DemandMin']]
			demandMax = valueList[self.fieldToIndex['DemandMax']]
			demandMode = valueList[self.fieldToIndex['DemandMode']]
			storeName = valueList[self.fieldToIndex['AssignedStore']]
			if custName in SimObjects.customerLookup:
				# if customer is already in dictionary, instantiate a new demand product and add it the customer's list
				SimObjects.customerLookup[custName].demandProductList.append(DemandProduct(custName, prodName, demandMin, demandMax, demandMode, SimObjects.storeLookup[storeName]))
			else:
				# if customer is not in dictionary, instantiate a customer, instantiate a demand product, add it the customer's list, add the customer to the dictionary
				customer = Customer(custName)
				customer.demandProductList.append(DemandProduct(custName, prodName, demandMin, demandMax, demandMode, SimObjects.storeLookup[storeName]))
				SimObjects.customerLookup[custName] = customer


class StoreData(DataTable):

	def __init__(self):

		DataTable.__init__(self)
		self.tableName = 'Store'
		self.keyNames = ['Store', 'Product']
		self.fieldToIndex = {'ReorderPoint': 0, 'OrderUpToQty': 1, 'MinLeadTime': 2, 'MaxLeadTime': 3}
		self.keyToValues = {}

	def buildSimObjects(self):
		SimObjects.storeLookup = {}
		for key, valueList in self.keyToValues.items():
			(storeName, prodName) = key
			# get values from value list
			reorderPt = valueList[self.fieldToIndex['ReorderPoint']]
			orderUpTo = valueList[self.fieldToIndex['OrderUpToQty']]
			minLeadTime = valueList[self.fieldToIndex['MinLeadTime']]
			maxLeadTime = valueList[self.fieldToIndex['MaxLeadTime']]
			if storeName in SimObjects.storeLookup:
				# if store is already in dictionary, instantiate a new inventory product and add it the store's list
				SimObjects.storeLookup[storeName].invProductList.append(InventoryProduct(storeName, prodName, reorderPt, orderUpTo, minLeadTime, maxLeadTime))
			else:
				# if store is not in dictionary, instantiate a store, instantiate an inventory product, add it the store's list, add the store to the dictionary
				store = Store(storeName)
				store.invProductList.append(InventoryProduct(storeName, prodName, reorderPt, orderUpTo, minLeadTime, maxLeadTime))
				SimObjects.storeLookup[storeName] = store


class TransitTimeData(DataTable):

	def __init__(self):
		DataTable.__init__(self)
		self.tableName = 'TransitTime'
		self.keyNames = ['Store', 'Customer']
		self.fieldToIndex = {'TransitTime': 0}
		self.keyToValues = {}

	def buildSimObjects(self):
		SimObjects.transitTimeLookup = {}
		for key, valueList in self.keyToValues.items():
			(storeName, custName) = key
			transitTime = valueList[self.fieldToIndex['TransitTime']]  # get value from value list
			SimObjects.transitTimeLookup[(storeName, custName)] = transitTime  # add the transit time to the lookup based off of the store and customer
