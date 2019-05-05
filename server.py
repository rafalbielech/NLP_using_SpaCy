from flask import Flask, render_template, request, jsonify
import socket
import sys
import datetime
from mainNLP import NLP
from send_request import POST_request
from flask_socketio import SocketIO, emit
from random import random
from time import sleep
from threading import Thread, Event


app = Flask(__name__)
socketio = SocketIO(app)

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def get_port_number():
    try:
        port_number = int(sys.argv[1])
        return port_number
    except Exception as e:
        print("Issue with the port number specified. {} is not an integer 0-65535\n{}".format(sys.argv[1], e))
        sys.exit()

################################################################################
@socketio.on('connect', namespace='/forward_doc_result')
def start_connect():
    print("Starting socket connection")

@app.route("/")
def hello():
    # render the main page
    return render_template("index.html")

@app.route('/query', methods=['POST'])
def form_post():
    response = request.get_json(force=True)
    # get the currentDT to figure out length of time taken for query parsing
    currentDT = datetime.datetime.now()
    print("Query: {}".format(response["message"]))
    # return result is a array of parsed query points
    return_result = nlp_eng.get_query_from_phrase(response["message"])
    # send that data to Solr
    ############ CHANGE this #####################
    ## RIGHT NOW just sending data to myself on port 9000, in future send it to SOLR on specific port
    print(send_data_conn.send_message(return_result ,"1.3"))
    ##############################################
    return jsonify("(Response: {} | Received: {} | Time elapsed: {} seconds)".format(return_result, currentDT.strftime("%Y-%m-%d %H:%M:%S"), nlp_eng.time_elapsed))

@app.route('/document_listener', methods=['POST'])
def get_index_result():
    # transform the request into a json object
    response = request.get_json(force=True)
    # socket is configured to accept "newdata", along with a json payload of document and time
    socketio.emit('newdata', {'document': response["document_list"], 'time': response["time_elapsed"]}, namespace='/forward_doc_result')
    return jsonify("Thanks!, received")



if __name__ == "__main__":
    port_number = get_port_number()
    ip_addr = get_ip_address()
    print("*******************************************************************")
    print("Connect to http://{}:{} to view the service".format(ip_addr, port_number))
    print("*******************************************************************")
    # initiate new NLP object
    nlp_eng = NLP()
    # initiate new POST connection with corresponding url, port, route
    ############ CHANGE this #####################
    ## RIGHT NOW just sending data to myself on port 9000, in future send it to SOLR on specific port
    send_data_conn = POST_request("127.0.0.1", "9000", "document_listener")
    #############################################
    # run the application
    socketio.run(app, host='0.0.0.0', port=port_number, debug=True)
################################################################################
