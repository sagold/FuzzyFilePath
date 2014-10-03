import inspect


class TestCase:
	def __init__(self, name):
		self.name = name
		self.tests = self.get_tests()
		self.length = len(self.tests)

	def get_tests(self):
		tests = []
		methods = inspect.getmembers(self, predicate=inspect.ismethod)
		for name, descr in methods:
			if "should" in name:
				tests.append(name)
		return tests