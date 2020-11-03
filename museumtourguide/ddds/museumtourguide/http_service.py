# -*- coding: utf-8 -*-

import json

from flask import Flask, request
from jinja2 import Environment
from urllib.request import Request, urlopen

app = Flask(__name__)
environment = Environment()


def jsonfilter(value):
    return json.dumps(value)


environment.filters["json"] = jsonfilter


def error_response(message):
    response_template = environment.from_string("""
    {
      "status": "error",
      "message": {{message|json}},
      "data": {
        "version": "1.0"
      }
    }
    """)
    payload = response_template.render(message=message)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


def query_response(value, grammar_entry):
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.1",
        "result": [
          {
            "value": {{value|json}},
            "confidence": 1.0,
            "grammar_entry": {{grammar_entry|json}}
          }
        ]
      }
    }
    """)
    payload = response_template.render(value=value, grammar_entry=grammar_entry)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


def multiple_query_response(results):
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.0",
        "result": [
        {% for result in results %}
          {
            "value": {{result.value|json}},
            "confidence": 1.0,
            "grammar_entry": {{result.grammar_entry|json}}
          }{{"," if not loop.last}}
        {% endfor %}
        ]
      }
    }
     """)
    payload = response_template.render(results=results)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


def validator_response(is_valid):
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.0",
        "is_valid": {{is_valid|json}}
      }
    }
    """)
    payload = response_template.render(is_valid=is_valid)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/dummy_query_response", methods=['POST'])
def dummy_query_response():
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.1",
        "result": [
          {
            "value": "dummy",
            "confidence": 1.0,
            "grammar_entry": null
          }
        ]
      }
    }
     """)
    payload = response_template.render()
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/action_success_response", methods=['POST'])
def action_success_response():
    response_template = environment.from_string("""
   {
     "status": "success",
     "data": {
       "version": "1.1"
     }
   }
   """)
    payload = response_template.render()
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response

# Harvard Museums

def get_data(painting_title, key="f315fe8e-b252-4a27-bdb3-0fb6dec18e67"):
    url = f"https://api.harvardartmuseums.org/object/{painting_title}?apikey={key}"
    request = Request(url)
    response = urlopen(request)
    data = response.read()
    return json.loads(data)

@app.route("/artist_name", methods=['POST'])
def artist_name():
    payload = request.get_json()
    painting_title = payload["context"]["facts"]["painting_to_search"]["grammar_entry"]
    data = get_data(painting_title)

    not_known = ["Unknown Artist", "Unidentified Artist"]
    # get artist name
    if data["people"][0]["displayname"] in not_known:
      artist_name = "unknown"
    else: # no data
      artist_name = data["people"][0]["displayname"]

    return query_response(value=artist_name, grammar_entry=None)

@app.route("/medium", methods=['POST'])
def medium():
    payload = request.get_json()
    painting_title = payload["context"]["facts"]["painting_to_search"]["grammar_entry"]
    data = get_data(painting_title)

    # get painting medium
    medium = data["medium"]

    return query_response(value=medium, grammar_entry=None)

@app.route("/dated", methods=['POST'])
def dated():
    payload = request.get_json()
    painting_title = payload["context"]["facts"]["painting_to_search"]["grammar_entry"]
    data = get_data(painting_title)

    # get date of creation
    if data["dated"] is None: # null 
      dated = "unknown"
    else:
      dated = data["dated"]

    return query_response(value=dated, grammar_entry=None)

@app.route("/display_category", methods=['POST'])
def display_category():
    payload = request.get_json()
    painting_title = payload["context"]["facts"]["painting_to_search"]["grammar_entry"]
    data = get_data(painting_title)

    # get date of creation
    if data["division"] is None: # null 
      display_category = "unknown"
    else:
      display_category = data["division"]

    return query_response(value=display_category, grammar_entry=None)

@app.route("/label_text", methods=['POST'])
def label_text():
    payload = request.get_json()
    painting_title = payload["context"]["facts"]["painting_to_search"]["grammar_entry"]
    data = get_data(painting_title)

    # get text beside painting in display
    if data["labeltext"] is None: # null 
      label_text = "unavailable"
    else:
      label_text = data["labeltext"]

    return query_response(value=label_text, grammar_entry=None)

@app.route("/provenance", methods=['POST'])
def provenance():
    payload = request.get_json()
    painting_title = payload["context"]["facts"]["painting_to_search"]["grammar_entry"]
    data = get_data(painting_title)

    # get history of ownership of painting
    if data["provenance"] is None: # null 
      provenance = "unavailable"
    else:
      provenance = data["provenance"]

    return query_response(value=provenance, grammar_entry=None)

@app.route("/visual_description", methods=['POST'])
def visual_description():
    payload = request.get_json()
    painting_title = payload["context"]["facts"]["painting_to_search"]["grammar_entry"]
    data = get_data(painting_title)

    # get visual description of painting
    if data["description"] is None: # null 
      visual_description = "unavailable"
    else:
      visual_description = data["description"]

    visual_description = visual_description.replace('"', "'")

    return query_response(value=visual_description, grammar_entry=None)

@app.route("/commentary", methods=['POST'])
def commentary():
    payload = request.get_json()
    painting_title = payload["context"]["facts"]["painting_to_search"]["grammar_entry"]
    data = get_data(painting_title)

    # get analysis/comments of painting
    if data["commentary"] is None: # null 
      commentary = "unavailable"
    else:
      commentary = data["commentary"]

    commentary = commentary.replace('"', "'")

    return query_response(value=commentary, grammar_entry=None)


# about the artist

@app.route("/birthplace", methods=['POST'])
def birthplace():
    payload = request.get_json()
    painting_title = payload["context"]["facts"]["painting_to_search"]["grammar_entry"]
    data = get_data(painting_title)

    # get birthplace of painting's artist
    if data["people"][0]["birthplace"] is None: # null 
      birthplace = "unknown"
    else:
      birthplace = data["people"][0]["birthplace"]

    return query_response(value=birthplace, grammar_entry=None)

@app.route("/culture", methods=['POST'])
def culture():
    payload = request.get_json()
    painting_title = payload["context"]["facts"]["painting_to_search"]["grammar_entry"]
    data = get_data(painting_title)

    # get nationality of painting's artist
    if data["people"][0]["culture"] is None: # null 
      culture = "unknown"
    else:
      culture = data["people"][0]["culture"]

    return query_response(value=culture, grammar_entry=None)

@app.route("/lifespan", methods=['POST'])
def lifespan():
    payload = request.get_json()
    painting_title = payload["context"]["facts"]["painting_to_search"]["grammar_entry"]
    data = get_data(painting_title)

    # get lifespan of painting's artist
    if data["people"][0]["displaydate"] is None: # null 
      lifespan = "unknown"
    else:
      lifespan = data["people"][0]["displaydate"]

    return query_response(value=lifespan, grammar_entry=None)


# get image url of painting

@app.route("/picture", methods=['POST'])
def picture():
    payload = request.get_json()
    painting_title = payload["context"]["facts"]["painting_to_search"]["grammar_entry"]
    data = get_data(painting_title)

    # get image url of painting
    if data["images"][0]["baseimageurl"] is None: # null 
      url_image = "unavailable"
    else:
      url_image = data["images"][0]["baseimageurl"]
    
    return query_response(value=url_image, grammar_entry=None)