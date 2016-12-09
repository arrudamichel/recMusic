from cf import ColaborativeFiltering

import json

from flask import Flask, request

app = Flask(__name__)

@app.route("/top/<user_id>/<count>", methods=["GET"])
def top_ratings(user_id, count=10): 
  return cf.get_itens(user_id,count)  

@app.route("/newRating/<user_id>/<item_id>", methods = ["GET"])
def add_ratings(user_id,item_id):    
  return cf.new_rating(user_id,item_id,1)

@app.route('/')
def index():
  return 'Index Page'

import time, sys, cherrypy, os
from pyspark import SparkContext, SparkConf


def run_server(app):
  app.run(port=8080)


if __name__ == "__main__":
  # Init spark context and load libraries
  sc = SparkContext("local", "App Name", pyFiles=['serverSpark.py', 'cf.py'])

  global cf 
  cf = ColaborativeFiltering(sc, "/home/hugdiniz/Work/Workspace/recMusic/dataset/m.csv")

  # start web server
  run_server(app)