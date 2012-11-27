class ArticleGroup():

    def __init__(self):
        self.keywords= None
        self.texts= {}

    @property
    def count_sources(self):
        return len(self.texts)

    @property
    def examples_per_source(self):
        if len(self.texts):
            return len(self.texts[0][1])
        else:
            return 0

    def add_example(ex, counter):

