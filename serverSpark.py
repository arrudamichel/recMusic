from cf import ColaborativeFiltering
from flask import render_template
import json

from flask import Flask, request
import time, sys, os
from pyspark import SparkContext, SparkConf
import numpy as np

app = Flask(__name__)

caminho = "/home/michel/Documentos/Spark/recMusic"
caminhoInterno = "/home/michel/Documentos/Spark/recMusic/"

@app.route("/logar/<user>", methods = ["GET"])
def logar(user):
  global users    
  uc = users.collect()

  if(uc.count(user) == 0):
    new_user = sc.parallelize([user]).map(lambda l: l)   
    users = users.union(new_user)
    uc = users.collect()   
    index = uc.index(user)    
    np.savetxt(caminhoInterno+'dataset/u.csv', uc, delimiter="\n", fmt="%s")

    return json.dumps([index,True])

  else:            
    return json.dumps([uc.index(user),False])


@app.route("/top/<user_id>", methods=["GET"])
def top_ratings(user_id):
  count=10
  lista = cf.get_itens(user_id,count)
  ci = itens.collect()
  saida = [ci[row[1]] for row in lista] 
  return json.dumps(saida)

@app.route("/newRating/<user_id>/<item_id>", methods = ["GET"])
def add_ratings(user_id,item_id):    
  return cf.new_rating(user_id,item_id,1)

@app.route("/knowUser/<stritens>/<user_id>", methods = ["GET"])
def know_user(stritens,user_id):
  
  new_itens = stritens.split(",")
  ci = itens.collect()
  indexs = [ci.index(ni) for ni in new_itens]    
  return cf.know_user(user_id,indexs,15000)


@app.route("/tops/", methods = ["GET"])
def tops():    
  lista = cf.getTopProduct()
  ci = itens.collect()
  saida = [ci[row[1]] for row in lista]
  return json.dumps(saida)

@app.route('/')
def index():
  return render_template('principal.html')  




def run_server(app):
  app.run(port=8083)


if __name__ == "__main__":
  # Init spark context and load libraries
  sc = SparkContext("local", "App Name", pyFiles=[caminhoInterno+'serverSpark.py', caminhoInterno+'cf.py'])

  global cf 
  #cf = ColaborativeFiltering(sc, "/home/hugdiniz/Work/Workspace/recMusic/dataset/m.csv")
  cf = ColaborativeFiltering(sc, caminho+"/dataset/m.csv")
  
  global users
  users = sc.textFile(caminho+"/dataset/u.csv")
  
  global itens
  itens = sc.textFile(caminho+"/dataset/v.csv")

  # start web server
  run_server(app)


  