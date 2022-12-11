import random

###
# global object allowing the simulation objects to communicate with each other
class SimObjects:
	currentTime = 0
	customerLookup = {} #dictionary of customers
	storeLookup = {} #dictionary of stores
	transitTimeLookup = {} #transition time dict
	totalDemand = 0

	@classmethod
	def resetObjects(cls):
		cls.currentTime = 0
		cls.customerLookup.clear()
		cls.storeLookup.clear()
		cls.transitTimeLookup.clear()


# represents an order between two entities
class OrderItem:

	def __init__(self, orderingEntityName, fulfillingEntityName, prodName, quantity, timeCreated=None, timeOfReceipt=None):
		self.orderingEntityName = orderingEntityName
		self.fulfillingEntityName = fulfillingEntityName
		self.prodName = prodName
		self.quantity = quantity
		self.timeCreated = timeCreated if timeCreated is not None else SimObjects.currentTime  # time the order is created
		self.timeOfReceipt = timeOfReceipt  # time that the order will be received by the ordering entity


class Customer:

	def __init__(self, custName):
		self.custName = custName
		self.demandProductList = []  # list of DemandProduct objects which the customer orders from a store

	def placeOrder(self):
		for demandProduct in self.demandProductList:
			demandProduct.placeOrder()

	def checkOrderReceipt(self):
		for demandProduct in self.demandProductList:
			demandProduct.checkOrderReceipt()


class DemandProduct:

	def __init__(self, custName, prodName, demandMin, demandMax, demandMode, assignedStore):
		self.custName = custName
		self.prodName = prodName
		self.demandMin = demandMin
		self.demandMax = demandMax
		self.demandMode = demandMode
		self.assignedStore = assignedStore  # the store that fulfills the demand for the customer's product
		self.incomingOrders = []  # list of orders placed by the customer for the product
		self.closedOrders = []  # list of orders that have been fulfilled and closed

	@staticmethod
	def triangleSample(minimum, maximum, mode):
		u = random.random()
		standardized_mode = (mode - minimum) / (maximum - minimum)
		if u < standardized_mode:
			return ((standardized_mode * u) ** 0.5) * (maximum - minimum) + minimum
		else:
			return (1 - ((1 - u) * (1 - standardized_mode)) ** 0.5) * (maximum - minimum) + minimum

	# generates a demand order
	def placeOrder(self):
		qty = self.triangleSample(self.demandMin, self.demandMax, self.demandMode)
		SimObjects.totalDemand += qty
		if qty > 0:
			newOrder = OrderItem(self.custName, self.assignedStore.storeName, self.prodName, qty)
			self.incomingOrders.append(newOrder)  # adds the generated order to the list of outstanding orders
			invProduct = [invProd for invProd in self.assignedStore.invProductList if invProd.prodName == self.prodName][0]
			invProduct.orderQueue.append(newOrder)  # adds the generated order to the order queue of the fulfilling store

	# evaluates the outstanding incoming orders to check if the order will be received by the next time period
	def checkOrderReceipt(self):
		# todo implement this method
		# iterates and processes self.incomingOrders
		# if the order has been received at start if the current time, remove the order from self.incomingOrders and add the order to self.closedOrders
		aux = self.incomingOrders[:]
		for order in aux:
			if order.timeOfReceipt >= SimObjects.currentTime:
				self.incomingOrders.remove(order)
				self.closedOrders.append(order)
		


class Store:

	def __init__(self, storeName):
		self.storeName = storeName
		self.invProductList = []  # list of InventoryProduct objects which the store stocks

	def fillOrders(self):
		for invProduct in self.invProductList:
			invProduct.fillOrders()

	def placeReorder(self):
		for invProduct in self.invProductList:
			invProduct.placeReorder()

	def checkOrderReceipt(self):
		for invProduct in self.invProductList:
			invProduct.checkOrderReceipt()


class InventoryProduct:

	def __init__(self, storeName, prodName, reorderPt, orderUpTo, minLeadTime, maxLeadTime):
		self.storeName = storeName
		self.prodName = prodName
		self.reorderPt = reorderPt
		self.orderUpTo = orderUpTo
		self.minLeadTime = minLeadTime
		self.maxLeadTime = maxLeadTime
		self.physicalInvLevel = orderUpTo  # the actual on-hand inventory level
		self.virtualInvLevel = orderUpTo  # the inventory level taking into consideration backorders and incoming orders
		self.incomingOrders = []  # list of orders placed by the store to its supplier for the product
		self.orderQueue = []  # list of backlogged orders that have not yet been filled, follows FIFO policy

	# processes the order queue and fills orders if possible
	def fillOrders(self):
		position = 0
		while position < len(self.orderQueue):
			order = self.orderQueue[position]
			if order.quantity <= self.physicalInvLevel:
				self.orderQueue.pop(position)  # remove the order from the queue if it's been filled
				# set receipt time as the current time + the transit time
				order.timeOfReceipt = SimObjects.currentTime + SimObjects.transitTimeLookup[(order.fulfillingEntityName, order.orderingEntityName)]
				self.physicalInvLevel -= order.quantity
				self.virtualInvLevel -= order.quantity
			else:
				position += 1

	# inventory follows an sS policy, when inventory falls below reorder point, order is placed to get inventory up to order up to quantity
	def placeReorder(self):
		if self.virtualInvLevel <= self.reorderPt:
			qty = self.orderUpTo - self.virtualInvLevel
			self.virtualInvLevel += qty
			leadTime = self.minLeadTime + random.random() * (self.maxLeadTime - self.minLeadTime)  # generate a random lead time from a uniform distribution
			# add replenishment order from dummy supplier and set time of receipt based on lead time
			self.incomingOrders.append(OrderItem(self.storeName, 'Supplier', self.prodName, qty, timeOfReceipt=SimObjects.currentTime+leadTime))

	# evaluates the outstanding incoming orders to check if the order will be received by the next time period
	def checkOrderReceipt(self):
		# todo implement this method
		# iterates and processes self.incomingOrders
		# if the order has been received at start if the current time, remove the order from self.incomingOrders and add the received quantity to the physical inventory
		aux = self.incomingOrders[:]
		for order in aux:
			if order.timeOfReceipt >= SimObjects.currentTime:
				self.incomingOrders.remove(order)
				self.physicalInvLevel += order.quantity
				
		
