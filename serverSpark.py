from cf import ColaborativeFiltering
from flask import render_template
import json

from flask import Flask, request
import time, sys, os
from pyspark import SparkContext, SparkConf
import numpy as np

app = Flask(__name__)

@app.route("/logar/<user>", methods = ["GET"])
def logar(user):
  global users    
  uc = users.collect()

  if(uc.count(user) == 0):
    new_user = sc.parallelize([user]).map(lambda l: l)   
    users = users.union(new_user)
    uc = users.collect()   
    index = uc.index(user)
    np.savetxt('dataset/u.csv', uc, delimiter="\n", fmt="%s")

    return json.dumps([index,True])

  else:            
    return json.dumps([uc.index(user),False])


@app.route("/top/<user_id>/<count>", methods=["GET"])
def top_ratings(user_id, count=10): 
  return cf.get_itens(user_id,count)  

@app.route("/newRating/<user_id>/<item_id>", methods = ["GET"])
def add_ratings(user_id,item_id):    
  return cf.new_rating(user_id,item_id,1)

@app.route('/')
def index():
  return render_template('principal.html')  




def run_server(app):
  app.run(port=8081)


if __name__ == "__main__":
  # Init spark context and load libraries
  sc = SparkContext("local", "App Name", pyFiles=['serverSpark.py', 'cf.py'])

  global cf 
  cf = ColaborativeFiltering(sc, "/home/hugdiniz/Work/Workspace/recMusic/dataset/m.csv")
  global users
  users = sc.textFile("/home/hugdiniz/Work/Workspace/recMusic/dataset/u.csv")

  # start web server
  run_server(app)


  