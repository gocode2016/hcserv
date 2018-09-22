class MongoDBTypeNotMatchException(Exception):

    def __init__(self, *args):
        super(MongoDBTypeNotMatchException, self).__init__(*args)


class MongoAssistInitialException(Exception):
    def __init__(self, *args):
        super(MongoAssistInitialException, self).__init__(*args)