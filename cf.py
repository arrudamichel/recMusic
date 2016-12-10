from pyspark.mllib.recommendation import ALS, MatrixFactorizationModel, Rating

class ColaborativeFiltering:

    def __train_model(self):       
        self.model = ALS.train(self.ratings, self.rank, self.iterations)


    def __init__(self, sc, dataset_path):        

        lines = sc.textFile(dataset_path)
        self.sc = sc
        
        self.itens = lines.map(lambda l: l.split(',')).map(lambda l: int(l[1])).distinct()
        self.ratings = lines.map(lambda l: l.split(',')).map(lambda l: Rating(int(l[0]), int(l[1]), float(l[2])))
        
        self.rank = 8       
        self.iterations = 10
        self.regularization_parameter = 0.1

        self.__train_model() 

    def new_rating(self, user_id,item_id, new_rating = 1):

        ri = self.ratings.filter(lambda l: l.user == user_id and l.product == item_id)
        if(ri.count() > 0):
            self.ratings = self.ratings.filter(lambda l: Rating(int(l.user), int(l.product), float(l.rating + new_rating)) if(l.user == user_id and l.product == item_id) else Rating(int(l.user), int(l.product), float(l.rating)))
        else:            
            new_ratings = self.sc.parallelize([[user_id,item_id,1]]).map(lambda l: Rating(int(l[0]), int(l[1]), float(l[2])))
            self.ratings = self.ratings.union(new_ratings)
            #rs = ratings.map(lambda l: int(l.user), int(l.product), float(l.rating))
            #np.savetxt('m.csv', rs.collect(), delimiter=",")

            new_itens = self.sc.parallelize([[item_id]]).map(lambda l: l)
            self.itens = self.itens.union(new_itens)  

        self.__train_model()

        return str(True)

    def get_itens(self, user_id, itens_count = 10):        
        predictions =  self.model.predictAll(self.itens.map(lambda r: ((user_id, r)))).map(lambda r: (r[2],(r[0], r[1])))
        return str(predictions.sortByKey(False).take(int(itens_count)))
