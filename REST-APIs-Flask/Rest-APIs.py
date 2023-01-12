import requests
#import pandas as pd
#import json
from datetime import datetime

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Date, DateTime, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from flask import Flask
from flask import request
from flask_restx import Resource, Api
from flask_restx import fields
#from flask_restx import inputs
from flask_restx import reqparse
from flask import send_file

import matplotlib.pyplot as plt
import numpy as np

app = Flask(__name__)
api = Api(app,
          version='1.0',
          default="Actors",  # Default namespace
          title="REST API for Actor/Actress",  # Documentation Title
          description="This is a REST API service through which actors can be fetched from TV MAJE API and stored locally in the database.\nSeveral operations can be performed on the database and the statistics of actors can be obtained through this service.")  # Documentation Description

class Actor(Base):
   __tablename__ = 'actors'
   
   id = Column(Integer, primary_key=True)
   name = Column(String)
   country = Column(String)
   birthday = Column(Date)
   deathday = Column(Date)
   gender = Column(String)
   last_update = Column(DateTime)

class Shows(Base):
   __tablename__ = 'shows'
   
   id = Column(Integer, primary_key=True)
   actor_id = Column(Integer)
   name = Column(String)

meta = MetaData()
actors_table = Table(
       'actors', meta, 
       Column('id', Integer, primary_key = True), 
       Column('name', String), 
       Column('country', String),
       Column('birthday', Date),
       Column('deathday', Date),
       Column('gender', String),
       Column('last_update', DateTime),
    )

shows_table = Table(
       'shows', meta, 
       Column('id', Integer, primary_key = True), 
       Column('actor_id', Integer), 
       Column('name', String), 
    )

actor_model = api.model('actor', {
    'name': fields.String(default= ""),
    'country': fields.String(default= ""),
    'birthday': fields.String(default= ""),
    'deathday': fields.String(default= ""),
    'gender': fields.String(default= ""),
    'shows': fields.String(default= "")
})


parser = reqparse.RequestParser()
parser.add_argument('name', type=str)

parser_retrieve = reqparse.RequestParser()
parser_retrieve.add_argument('order', type=str)
parser_retrieve.add_argument('page', type=int)
parser_retrieve.add_argument('size', type=int)
parser_retrieve.add_argument('filter', type=str)

@api.route('/actors')
class AddActor(Resource):
    
    @api.doc(params={'name': "Name of an Actor (required*)\nIt takes as its input a string. Allowed characters are alphabets, numbers or space.\nAny non-allowed characters will be converted into space.\nExamples: 'Hugh Jackman', 'James Bond7', ' Br@d Pi!! '"})
    @api.response(201, 'Success: Actor has been added successfully to the database')
    @api.response(400, 'Error: Validation failed for the input name')
    @api.response(404, 'Error: Actor was not found on the TVMaze API')
    @api.doc(description="Description:\nSearch for an actor on TV Maje API using parameter name and store their details in the database.\n\nOperation Summary:\nname will be pre-processed and any non-allowed characters will be converted into space.\nAny additional spaces in the name will also be removed.\nThen the value of name will be used to query TV Maje API.\nAll the person names returned by TV Maje API will be lowercase matched to the input name.\nIf any match is found, then name will be stored in the database after capitalizing all its words.")
    @api.expect(parser)
    def post(self):
        
        args = parser.parse_args()
        name = args.get('name')
        
        if name is None:
            output = {"message": "Validation failed for name. Please enter some value for the name, it cannot be an empty string."}
            return output, 400
        
        name = str(name)
        
        status = 0
        for i in range(len(name)):
            if(name[i].isalnum()):
                status = 1                
        if status == 0:
            output = {"message": "Validation failed for name. Please enter some valid characters in the name."}
            return output, 400
            
        HOST_NAME, PORT = request.host.split(':')
        
        name = clean_name(name)
        
        if validate_existing_name(name, 0) == 0:
            output = {"message": "Validation failed for name. An actor already exists in database with the name '"+name+"' and names have to be unique."}
            return output, 400

        #print("Fetch the json")
        url = "https://api.tvmaze.com/search/people?q="
        resp = requests.get(url=url+name)
        
        if resp.status_code != 200:
            return {"message": "Unable to connect to TV Maje API and got the error code: {}".format(resp.status_code)}, resp.status_code
        
        json_obj = resp.json()
          
        if len(json_obj) == 0:
            output = {"message": "No actor found with name '"+name+"' on the TV Maje API."}
            return output, 404

        found_match = 0
        
        for i in range(len(json_obj)):
            if json_obj[i]['person']['name'] is not None:
                name_to_match = str(json_obj[i]['person']['name']).lower()
                if name_to_match == name.lower() and found_match == 0:
                    found_match = 1
            
                    p_id = json_obj[i]['person']['id']
                    
                    p_name = json_obj[i]['person']['name']
                    
                    if json_obj[i]['person']['country'] is not None:
                        p_country = json_obj[i]['person']['country']['name']
                    else:
                        p_country = None
                    
                    p_birthday = json_obj[i]['person']['birthday']        
                    if p_birthday != '' and p_birthday is not None:
                        p_birthday = datetime.strptime(p_birthday, '%Y-%m-%d').date()
                    
                    p_deathday = json_obj[i]['person']['deathday']
                    if p_deathday != '' and p_deathday is not None:
                        p_deathday = datetime.strptime(p_deathday, '%Y-%m-%d').date()
                    
                    p_gender = json_obj[i]['person']['gender']                
                    
                    actor_id, last_update = add_actor_to_db(p_name, p_country, p_birthday, p_deathday, p_gender, p_id)
                    
                    output = {"id": str(actor_id),
                              "last_update": str(last_update),
                                "_links": {
                                    "self": {
                                      "href": "http://"+HOST_NAME+":"+PORT+"/actors/"+str(actor_id)
                                    }
                                }   
                              }
                
                    return output, 201
        
        output = {"message": "No actor found with name '"+name+"' on the TV Maje API."}
        return output, 404


    @api.doc(params={'order': "Attributes of the actor used to sort the final results (optional, default value= '+id')\nIt takes as its input a comma separated string of allowed values.\nAllowed values are 'id', 'name', 'country', 'birthday', 'deathday' or 'last-update'.\nPut a minus sign (-) in front of the value to indicate descending order.\nYou may put a plus (+) in front of the value or just mention the value as it is to indicate ascending order.\nExamples: 'id', '+id, -name', ' country, - name, + id '"})
    @api.doc(params={'page': "Number of the page in the final results (optional, default value= 1)\nIt takes as its input a positive integer (greater than 0).\nExamples: 1, 3, 10"})
    @api.doc(params={'size': "Number of actor records shown in each page (optional, default value= 10)\nIt takes as its input a positive integer (greater than 0)\nExamples: 1, 5, 20"})
    @api.doc(params={'filter': "Attributes of the actor to show in the final results (optional, default value= 'id,name')\nIt takes as its input a comma separated string of allowed values.\nAllowed values are 'id', 'name', 'country', 'birthday', 'deathday' or 'last-update'.\nExamples: 'id', 'id, name', ' country, name, last-update '"})
    @api.response(200, 'Success: Actor details retrieved successfully from the database')
    @api.response(400, 'Error: Validation failed for the input parameters')
    @api.response(404, 'Error: No record found for the requested page and size')
    @api.doc(description="Description:\nRetrieve a page from the database containing the actors' details based on input parameters.\n\nOperation Summary:\nDatabase retrieval query is run on the basis of the four parameters: order, page, size and filter.\nAll four parameters are optional and their default values will be used if no value is provided.\nActor attributes will be shown and sorted based on filter and order.\nPage number and numbers of records to show in each page depends on page and size.\nAny additional spaces in the parameters order and filter will also be handled.")
    @api.expect(parser_retrieve)
    def get(self):
        args = parser_retrieve.parse_args()
        order = args.get('order')
        page = args.get('page')
        size = args.get('size')
        filter = args.get('filter')
        
        if order == '' or order is None:
            order = '+id'     
        else:
            order = str(order)
            order = order.split(',')
            for i in range(len(order)):
                order[i] = order[i].strip()
                while "  " in order[i]:
                    order[i] = order[i].replace("  ", " ")
                
                if order[i] not in ('id','name','country','birthday','deathday','last-update','+id','+name','+country','+birthday','+deathday','+last-update','+ id','+ name','+ country','+ birthday','+ deathday','+ last-update','-id','-name','-country','-birthday','-deathday','-last-update','- id','- name','- country','- birthday','- deathday','- last-update'):            
                    output = {"message": "Validation failed for parameter order. It only contains the list of attributes ('id', 'name', 'country', 'birthday', 'deathday' or 'last-update') and each attribute can be preceded by a + or -."}
                    return output, 400                
                
                while " " in order[i]:
                    order[i] = order[i].replace(" ", "")
                
                order[i] = order[i].replace("last-", "last_")
                
            order_dup = []
            for item in order:
                order_dup.append(item)
            for i in range(len(order_dup)):
                order_dup[i] = order_dup[i].replace("-", "")
                order_dup[i] = order_dup[i].replace("+", "")
                order_dup[i] = order_dup[i].strip()
            if len(order) != len(set(order_dup)):
                output = {"message": "Validation failed for parameter order. Please mention each attribute only once."}
                return output, 400 
                
            order = ",".join(order)
            
        if page == '' or page is None:
            page = 1     
        elif str(page).isnumeric() is False:
            output = {"message": "Validation failed for parameter page. Only positive Integer values are allowed for it."}
            return output, 400 
        elif page < 1:
            output = {"message": "Validation failed for parameter page. Only positive Integer values are allowed for it."}
            return output, 400 
        
        if size == '' or size is None:
            size = 10    
        elif str(size).isnumeric() is False:
            output = {"message": "Validation failed for parameter size. Only positive Integer values are allowed for it."}
            return output, 400 
        elif size < 1:
            output = {"message": "Validation failed for parameter size. Only positive Integer values are allowed for it."}
            return output, 400 
            
        if filter == '' or filter is None:
            filter = 'id,name'
        else:
            filter = str(filter)
            filter = filter.split(',')
            for i in range(len(filter)):
                filter[i] = filter[i].strip()
                while "  " in filter[i]:
                    filter[i] = filter[i].replace("  ", " ")
                
                if filter[i] not in ('id','name','country','birthday','deathday','last-update'):            
                    output = {"message": "Validation failed for parameter by. It only contains the list of attributes ('id', 'name', 'country', 'birthday', 'deathday' or 'last-update') and each of them should be separated by a comma."}
                    return output, 400
                
                filter[i] = filter[i].replace("-", "_")
            filter = ",".join(filter)
        
        
        output = dict()
        output["page"] = page
        output["page-size"] = size
        
        total = get_total_count()
        
        if total <= (page-1)*size:                        
            output["message"] = "No actor record found for the requested page and size. Please try reducing the page number or size and request the page again."
            return output, 404
        else:            
            
            output["actors"] = retrieve_actors(order, page, size, filter)        
            HOST_NAME, PORT = request.host.split(':')
            
            links = dict()
            links["self"] = {"href": "http://{}:{}/actors?order={}&page={}&size={}&filter={}".format(HOST_NAME, PORT, order, page, size, filter)
                             }
            if page > 1:            
                links["previous"] = {"href": "http://{}:{}/actors?order={}&page={}&size={}&filter={}".format(HOST_NAME, PORT, order, page-1, size, filter)
                                 }
            if total > page*size:            
                links["next"] = {"href": "http://{}:{}/actors?order={}&page={}&size={}&filter={}".format(HOST_NAME, PORT, order, page+1, size, filter)
                                 }
            
            output["_links"] = links
            
            return output, 200


@api.doc(params={'id': 'Database ID of an actor (required*)\nIt takes as its input a positive integer (greater than 0).\nExamples: 1, 5, 20'})
@api.route('/actors/<int:id>')
class ActorOperations(Resource):
    
    @api.response(200, 'Success: Actor retrieved successfully from the database')
    @api.response(400, 'Error: Validation failed for the input parameters')
    @api.response(404, 'Error: Actor was not found in the database')
    @api.doc(description="Description:\nRetrieve details of an actor from the database using the actor's ID.\n\nOperation Summary:\nSearch the database for actors based on provided actor's ID.\nIf a match is found then show all the details of that record.\nIt will also show the links for previous and next records (if they exists).")
    def get(self, id):

        actor_id = id
        if actor_id == '' or actor_id is None:
            output = {"message": "Please enter the value of parameter id."}
            return output, 400
        if str(actor_id).isnumeric() is False:
            output = {"message": "Validation failed for parameter id. Only positive Integer values are allowed for it."}
            return output, 400 
        actor_id = int(actor_id)
        if actor_id < 1:
            output = {"message": "Validation failed for parameter id. Only positive Integer values are allowed for it."}
            return output, 400 
        
        
        
        engine = create_engine('sqlite:///z5334390.db', echo = True)
    
        Session = sessionmaker(bind = engine)
        session = Session()
        
        result_actor = session.query(Actor).get(actor_id)
        
        if result_actor is None:
            output = {"message": "The actor with id "+ str(id) +" was not found in the database."}
            return output, 404
        else:
        
            HOST_NAME, PORT = request.host.split(':')
            
            if result_actor.birthday is None:
                actor_birthday = result_actor.birthday
            else:
                actor_birthday = str(result_actor.birthday)
                
            if result_actor.deathday is None:
                actor_deathday = result_actor.deathday
            else:
                actor_deathday = str(result_actor.deathday)
                
            result = session.query(Actor).filter(Actor.id < actor_id)
            prev_id = 0
            for row in result:
                if row.id > prev_id:
                    prev_id = row.id
                
            result = session.query(Actor).filter(Actor.id > actor_id)
            next_id = 9999999
            for row in result:
                if row.id < next_id:
                    next_id = row.id    
            
            links = dict()
            links['self'] = {"href": "http://"+HOST_NAME+":"+PORT+"/actors/"+str(actor_id)}
            if prev_id != 0:
                links['previous'] = {"href": "http://"+HOST_NAME+":"+PORT+"/actors/"+str(prev_id)}
            if next_id != 9999999:
                links['next'] = {"href": "http://"+HOST_NAME+":"+PORT+"/actors/"+str(next_id)}
            
            result = session.query(Shows).filter(Shows.actor_id == actor_id)
            shows_list = []
            for row in result:
                shows_list.append(row.name)
                
            output = {"id": actor_id,
                      "last-update": str(result_actor.last_update),
                      "name": result_actor.name,
                      "country": result_actor.country,
                      "birthday": actor_birthday,
                      "deathday": actor_deathday,
                       "shows": shows_list,              
                      "_links": links
                     }
        
            return output, 200


    @api.response(200, 'Success: Actor deleted successfully from the database')
    @api.response(400, 'Error: Validation failed for the input parameters')
    @api.response(404, 'Error: Actor was not found in the database')
    @api.doc(description="Description:\nDelete an actor from the database using the actor's ID.\n\nOperation Summary:\nSearch the database for actors based on provided actor's ID.\nIf a match is found then delete that record from the database.")
    def delete(self, id):
        
        actor_id = id
        if actor_id == '' or actor_id is None:
            output = {"message": "Please enter the value of parameter id."}
            return output, 400
        if str(actor_id).isnumeric() is False:
            output = {"message": "Validation failed for parameter id. Only positive Integer values are allowed for it."}
            return output, 400 
        actor_id = int(actor_id)
        if actor_id < 1:
            output = {"message": "Validation failed for parameter id. Only positive Integer values are allowed for it."}
            return output, 400 
        
        status = delete_actor(actor_id)        
        
        if status == 1:        
            output = {"message": "The actor with id "+ str(actor_id) +" has been removed from the database.",
                  "id": actor_id
                 }
            return output, 200
        elif status == 0:
            output = {"message": "The actor with id "+ str(actor_id) +" was not found in the database."}
            return output, 404 
        
        return {"message": "Unable to remove the actor with id "+ str(actor_id) +" from the database."}, 404


    @api.response(200, 'Success: Actor details updated successfully in the database')
    @api.response(400, 'Error: Validation failed for the input parameters')
    @api.response(404, 'Error: Actor was not found in the database')
    @api.doc(description="Description:\nUpdate details of an actor in the database using the actor's ID.\n\nOperation Summary:\nSearch the database for actors based on provided actor's ID.\nIf a match is found then update that record's attributes in the database based on provided details.\nParameters with values as blank ('') or just spaces (like '  ') will not be updated.\nname and gender will be stored with all words capitalized to keep data format consistent.\n\nRequired Parameters Format:\nname-\nIt accepts as its input a string and any character is allowed.\nExamples: 'James', 'Jack Black', ' Fight#r B@y '.\n\ncountry-\nIt takes as its input a string.\nCountry can only be changed to a country name that exists in database.\n\nbirthday and deathday-\nIt accepts dates only in format 'yyyy-mm-dd'.\nThese dates cannot be in future.\nExamples: '2022-03-02', '1992-01-26', '2003-06-04'.\n\ngender-\nAllowed values are 'Male', 'Female', 'Trans', 'Non-binary' or 'Other'\n\nshows-\nIt accepts a comma separated string of name of the shows.\nExamples: 'Boys', 'Lucifer, Supernatural', 'Black Mirror, Dexter, Big Bang Theory'")
    @api.expect(actor_model)
    def patch(self, id):
        
        actor_id = id
        if actor_id == '' or actor_id is None:
            output = {"message": "Please enter the value of parameter id."}
            return output, 400
        if str(actor_id).isnumeric() is False:
            output = {"message": "Validation failed for parameter id. Only positive Integer values are allowed for it."}
            return output, 400 
        actor_id = int(actor_id)
        if actor_id < 1:
            output = {"message": "Validation failed for parameter id. Only positive Integer values are allowed for it."}
            return output, 400 
        
        # get the payload and convert it to a JSON
        new_actor = request.json
        
        new_name = new_actor['name'].strip()
        if new_name == '':
            new_name = None
        else:
            while("  " in new_name):
                new_name = new_name.replace("  ", " ")
            new_name = new_name.split(' ')
            for i in range(len(new_name)):
                new_name[i] = new_name[i].capitalize()
            new_name = " ".join(new_name)
            
            if validate_existing_name(new_name, actor_id) == 0:
                output = {"message": "Validation failed for name. An actor already exists in database with the name "+new_name+" and names have to be unique."}
                return output, 400
        
        new_country = new_actor['country'].strip()
        if new_country == '':
            new_country = None
        else:
            validate_country = validate_existing_country(new_country)
            if validate_country != 1:
                output = {"message": "Validation failed for country. Country can only be changed if the provided country name already exists in database. Some valid country names are shown."}
                output["valid_countries"] = validate_country
                return output, 400
            
        new_birthday = new_actor['birthday'].strip()
        if new_birthday == '':
            new_birthday = None
        else:
            new_birthday = validate_date(new_birthday)         
            if new_birthday == 0:
                output = {"message": "Validation failed for birthday. Expected format is 'yyyy-dd-mm'."}
                return output, 400
            elif new_birthday == -1:
                output = {"message": "Validation failed for birthday. Birthday cannot be in future."}
                return output, 400
            
        new_deathday = new_actor['deathday'].strip()
        if new_deathday == '':
            new_deathday = None
        else:
            new_deathday = validate_date(new_deathday)             
            if new_deathday == 0:
                output = {"message": "Validation failed for deathday. Expected format is 'yyyy-dd-mm'."}
                return output, 400
            elif new_deathday == -1:
                output = {"message": "Validation failed for deathday. Deathday cannot be in future."}
                return output, 400
            
        new_gender = new_actor['gender'].strip()
        if new_gender == '':
            new_gender = None
        else:
            new_gender = new_gender.capitalize()
            if new_gender not in ('Male', 'Female', 'Trans', 'Non-binary', 'Other'):
                output = {"message": "Validation failed for gender parameter. Allowed values are: 'Male', 'Female', 'Trans', 'Non-binary', 'Other'."}
                return output, 400                
        
        new_shows = new_actor['shows']
        if new_shows == '':
            new_shows = None
        else:
            new_shows = new_actor['shows'].split(',')
            for i in range(len(new_shows)):
                new_shows[i] = new_shows[i].strip()
        
        output = update_actor(actor_id, new_name, new_country, new_birthday, new_deathday, new_gender, new_shows)
        
        if output == 0:
            output = {"message": "The actor with id "+ str(actor_id) +" was not found in the database."}
            return output, 404
        else:
            return output, 200
        


parser_stats = reqparse.RequestParser()
parser_stats.add_argument('format', type=str)
parser_stats.add_argument('by', type=str)
@api.route('/actors/statistics')
class ActorStats(Resource):
    
    
    @api.doc(params={'format': "Format of the output results (required*)\nIt takes as its input a string and allowed values are 'json' and 'image'.\nExamples: 'json', 'image', ' image '"})
    @api.doc(params={'by': "Attributes of the actor to get the statistics for (required*)\nIt takes as its input a comma separated string of allowed values.\nAllowed values are 'country', 'birthday', 'gender' or 'life_status'.\n Examples: 'country', 'gender, birthday', ' country , birthday , life_status '"})
    @api.response(200, 'Success: Actor details updated successfully in the database')
    @api.response(400, 'Error: Validation failed for the input parameters')
    @api.response(404, 'Error: No actor found in the database')
    @api.doc(description="Description:\nGet statistics of all the actors in the database based on country, birthday, gender or life status.\n\nOperation Summary:\nShows the percentage distribution of the actors based on parameters format and by and both are required.\nResults will include the total number of records in the database and the records updated in last 24 hours.\nStatistics can be obtained for any combination of attributes- 'country', 'birthday', 'gender' or 'life_status'\nand it will depend on the value of the parameter by.\nFinal results can be obtained in either json or image format.\nAny additional spaces in the parameters format and by will also be handled.")
    @api.expect(parser_stats)
    def get(self):        
        
        args = parser_stats.parse_args()
        format = args.get('format')
        
        if format == '' or format is None:
            return {"message": "Please enter the value of 'format' parameter. It takes values 'json' and 'image'."}, 400        
        format = str(format)
        format = format.lower().strip()
        if format not in ('json', 'image'):
            return {"message": "Please enter correct value for 'format' parameter. It only takes values 'json' and 'image'."}, 400
                
        by = args.get('by')
        if by == '' or by is None:
            return {"message": "Please enter the value of 'by' parameter. It takes values 'country', 'birthday', 'gender', 'life_status', and each value needs to be separated by a comma."}, 400        
        by = str(by)
        by = by.split(',')
        for i in range(len(by)):
            by[i] = by[i].strip().lower()
            if by[i] not in ('country', 'birthday', 'gender', 'life_status'):
                return {"message": "Please enter correct value for 'by' parameter. It only takes values 'country', 'birthday', 'gender', 'life_status', and each value needs to be separated by a comma."}, 400
        by = list(set(by))
        
        output = dict()
        
        total = get_total_count()
        output['total'] = total
        
        output['total-updated'] = get_last_24_hrs_count()        
        
        if total < 1:
            return {"message": "There is no actor in the database.", "total": total}, 404
        
        for attrs in by:
            if attrs == 'country':
                output['by-country'] = get_country_stats()
            if attrs == 'birthday':
                output['by-birthday'] = get_birthday_stats()
            if attrs == 'gender':
                output['by-gender'] = get_gender_stats()
            if attrs == 'life_status':
                output['by-life_status'] = get_life_status_stats()
                
        if format == 'json':
            return output, 200
        else:
            
            by_length = len(by)
            
            if by_length == 1:
                plt.figure(figsize=(12, 12))
            elif by_length == 2:
                plt.figure(figsize=(16, 8))
            else:
                plt.figure(figsize=(16, 16))
            
            plt.suptitle("Total: {}\nTotal Updated: {}".format(total, output['total-updated']))
            
            if by_length == 1:
                if by[0] == 'birthday':
                    months = np.array(list(output['by-birthday'].values()))    
                    months = np.flipud(months)
                    months_labels = list(output['by-birthday'].keys()) 
                    months_labels = np.flipud(months_labels)
                    
                    plt.xlabel('Percentage of Birthdays in Each Month')  
                    plt.ylabel('Months')  
                    plt.title('Percentage Distribution of Birthdays for Actors')
                    for i, v in enumerate(months):
                        plt.text(v + 0.2, i-0.2, str(v)+'%')
                    plt.barh(months_labels, months)
                    
                    plt.savefig('z5334390_distribution.jpg')
                    return send_file('z5334390_distribution.jpg')
                else:
                    countries = np.array(list(output["by-{}".format(by[0])].values()))    
                    country_labels = list(output["by-{}".format(by[0])].keys())
                    
                    plt.pie(countries, labels = country_labels, autopct='%1.2f%%')
                    plt.title("Percentage Distribution of {} for Actors".format(by[0].capitalize()))
                    
                    plt.savefig('z5334390_distribution.jpg')
                    return send_file('z5334390_distribution.jpg')
                    
            elif by_length == 2:
                if 'birthday' in by:
                    by.remove('birthday')
                    
                    plt.subplot(121) # for birthday
                    months = np.array(list(output['by-birthday'].values()))    
                    months = np.flipud(months)
                    months_labels = list(output['by-birthday'].keys()) 
                    months_labels = np.flipud(months_labels)
                    
                    plt.xlabel('Percentage of Birthdays in Each Month')  
                    plt.ylabel('Months')  
                    plt.title('Percentage Distribution of Birthdays for Actors')
                    for i, v in enumerate(months):
                        plt.text(v + 0.2, i-0.2, str(v)+'%')
                    plt.barh(months_labels, months)                    
              
                    plt.subplot(122) # for other
                    countries = np.array(list(output["by-{}".format(by[0])].values()))    
                    country_labels = list(output["by-{}".format(by[0])].keys())
                    
                    plt.pie(countries, labels = country_labels, autopct='%1.2f%%')
                    plt.title("Percentage Distribution of {} for Actors".format(by[0].capitalize()))
                    
                else:
                    plt.subplot(121) # for other
                    countries = np.array(list(output["by-{}".format(by[0])].values()))    
                    country_labels = list(output["by-{}".format(by[0])].keys())
                    
                    plt.pie(countries, labels = country_labels, autopct='%1.2f%%')
                    plt.title("Percentage Distribution of {} for Actors".format(by[0].capitalize()))
                    
                    plt.subplot(122) # for other
                    countries = np.array(list(output["by-{}".format(by[1])].values()))    
                    country_labels = list(output["by-{}".format(by[1])].keys())
                    
                    plt.pie(countries, labels = country_labels, autopct='%1.2f%%')
                    plt.title("Percentage Distribution of {} for Actors".format(by[1].capitalize()))
                    
                plt.savefig('z5334390_distribution.jpg') 
                return send_file('z5334390_distribution.jpg')
                
            elif by_length == 3:    
                if 'birthday' in by:
                    by.remove('birthday')
                    
                    plt.subplot(221) # for birthday
                    countries = np.array(list(output["by-{}".format(by[0])].values()))    
                    country_labels = list(output["by-{}".format(by[0])].keys())
                    
                    plt.pie(countries, labels = country_labels, autopct='%1.2f%%')
                    plt.title("Percentage Distribution of {} for Actors".format(by[0].capitalize()))                  
              
                    plt.subplot(222) # for other
                    countries = np.array(list(output["by-{}".format(by[1])].values()))    
                    country_labels = list(output["by-{}".format(by[1])].keys())
                    
                    plt.pie(countries, labels = country_labels, autopct='%1.2f%%')
                    plt.title("Percentage Distribution of {} for Actors".format(by[1].capitalize()))
                    
                    plt.subplot(223) # for birthday
                    months = np.array(list(output['by-birthday'].values()))    
                    months = np.flipud(months)
                    months_labels = list(output['by-birthday'].keys()) 
                    months_labels = np.flipud(months_labels)
                    
                    plt.xlabel('Percentage of Birthdays in Each Month')  
                    plt.ylabel('Months')  
                    plt.title('Percentage Distribution of Birthdays for Actors')
                    for i, v in enumerate(months):
                        plt.text(v + 0.2, i-0.2, str(v)+'%')
                    plt.barh(months_labels, months) 
                    
                else:
                    plt.subplot(221) # for other
                    countries = np.array(list(output["by-{}".format(by[0])].values()))    
                    country_labels = list(output["by-{}".format(by[0])].keys())
                    
                    plt.pie(countries, labels = country_labels, autopct='%1.2f%%')
                    plt.title("Percentage Distribution of {} for Actors".format(by[0].capitalize()))
                    
                    plt.subplot(222) # for other
                    countries = np.array(list(output["by-{}".format(by[1])].values()))    
                    country_labels = list(output["by-{}".format(by[1])].keys())
                    
                    plt.pie(countries, labels = country_labels, autopct='%1.2f%%')
                    plt.title("Percentage Distribution of {} for Actors".format(by[1].capitalize()))
                    
                    plt.subplot(223) # for other
                    countries = np.array(list(output["by-{}".format(by[2])].values()))    
                    country_labels = list(output["by-{}".format(by[2])].keys())
                    
                    plt.pie(countries, labels = country_labels, autopct='%1.2f%%')
                    plt.title("Percentage Distribution of {} for Actors".format(by[2].capitalize()))
                    
                plt.savefig('z5334390_distribution.jpg') 
                return send_file('z5334390_distribution.jpg')
            
            else:
                
                by.remove('birthday')
                    
                plt.subplot(221) # for birthday
                countries = np.array(list(output["by-{}".format(by[0])].values()))    
                country_labels = list(output["by-{}".format(by[0])].keys())
                    
                plt.pie(countries, labels = country_labels, autopct='%1.2f%%')
                plt.title("Percentage Distribution of {} for Actors".format(by[0].capitalize()))                  
              
                plt.subplot(222) # for other
                countries = np.array(list(output["by-{}".format(by[1])].values()))    
                country_labels = list(output["by-{}".format(by[1])].keys())
                    
                plt.pie(countries, labels = country_labels, autopct='%1.2f%%')
                plt.title("Percentage Distribution of {} for Actors".format(by[1].capitalize()))
                    
                plt.subplot(223) # for birthday
                months = np.array(list(output['by-birthday'].values()))    
                months = np.flipud(months)
                months_labels = list(output['by-birthday'].keys()) 
                months_labels = np.flipud(months_labels)
                
                plt.xlabel('Percentage of Birthdays in Each Month')  
                plt.ylabel('Months')  
                plt.title('Percentage Distribution of Birthdays for Actors')
                for i, v in enumerate(months):
                    plt.text(v + 0.2, i-0.2, str(v)+'%')
                plt.barh(months_labels, months)                  
              
                plt.subplot(224) # for other
                countries = np.array(list(output["by-{}".format(by[2])].values()))    
                country_labels = list(output["by-{}".format(by[2])].keys())
                    
                plt.pie(countries, labels = country_labels, autopct='%1.2f%%')
                plt.title("Percentage Distribution of {} for Actors".format(by[2].capitalize()))
                
                plt.savefig('z5334390_distribution.jpg') 
                return send_file('z5334390_distribution.jpg')


def clean_name(name):
    for i in range(len(name)):
        if(name[i].isalnum() is False):
            name = name.replace(name[i], " ")
    
    while "  " in name:
        name = name.replace("  ", " ")
    name = name.strip()
    
    name = name.split(' ')
    for i in range(len(name)):
        name[i] = name[i].capitalize()
    name = " ".join(name)
            
    return name       


def create_db():
    engine = create_engine('sqlite:///z5334390.db', echo = True)
    meta.create_all(engine)  


def validate_existing_name(name, actor_id):
    engine = create_engine('sqlite:///z5334390.db', echo = True)    
    Session = sessionmaker(bind = engine)
    session = Session()
    result = session.query(Actor).all()
    
    for row in result:
        if row.name is not None:
            if row.name.lower() == name.lower() and actor_id != row.id:
                return 0
  
    return 1
    

def validate_existing_country(country):
    engine = create_engine('sqlite:///z5334390.db', echo = True)    
    Session = sessionmaker(bind = engine)
    session = Session()
    result = session.query(Actor).all()
    
    countries = set()
    
    for row in result:
        if row.country is not None:
            if row.country == country:
                return 1
            else:
                countries.add(row.country)
  
    return list(countries)
    

def add_actor_to_db(p_name, p_country, p_birthday, p_deathday, p_gender, p_id):
    engine = create_engine('sqlite:///z5334390.db', echo = True)
    #conn = engine.connect()    
    Session = sessionmaker(bind = engine)
    session = Session()
    
    curr_time = str(datetime.now())[:19]
    curr_time = datetime.strptime(curr_time, '%Y-%m-%d %H:%M:%S')
    
    actor = Actor(name = p_name, country= p_country, birthday= p_birthday, 
                  deathday= p_deathday, gender= p_gender, last_update=curr_time)
    
    session.add(actor)
    session.flush()
    actor_id = actor.id
    session.commit()
    
    resp = requests.get(url='https://api.tvmaze.com/people/'+str(p_id)+'/castcredits')
    if resp.status_code != 200:
            return {"message": "Unable to connect to TV Maje API and got the error code: {}".format(resp.status_code)}, resp.status_code
        
    data = resp.json()
    
    for i in range(len(data)):
        show_id = data[i]['_links']['show']['href'].split('/')[-1]
        resp = requests.get(url='https://api.tvmaze.com/shows/'+str(show_id))
        if resp.status_code != 200:
            return {"message": "Unable to connect to TV Maje API and got the error code: {}".format(resp.status_code)}, resp.status_code
        
        show_data = resp.json()
        show_name = show_data['name']
        add_shows_to_db(actor_id, show_name)
    
    return actor_id, curr_time
    
              
def add_shows_to_db(actor_id, s_name):
    engine = create_engine('sqlite:///z5334390.db', echo = True)
    conn = engine.connect()
    
    ins = shows_table.insert().values(actor_id= actor_id, name = s_name)
    conn.execute(ins)
    

def delete_actor(actor_id):
    engine = create_engine('sqlite:///z5334390.db', echo = True)
    
    Session = sessionmaker(bind = engine)
    session = Session()
    
    result = session.query(Actor).get(actor_id)
    
    if result is not None:
        session.delete(result)
        session.commit()
    
        #delete all shows of the actor
        conn = engine.connect()
        stmt = shows_table.delete().where(shows_table.c.actor_id == actor_id)
        conn.execute(stmt)
        
        return 1        
    else:           
        return 0


def validate_date(input_date):
    try:
        datetime.strptime(input_date, '%Y-%m-%d')
    except ValueError:
        return 0
    
    input_date = datetime.strptime(input_date, '%Y-%m-%d').date()
    
    if datetime.now().date() < input_date:
        return -1
        
    return str(input_date)


def update_actor(id, name= None, country= None, birthday= None, deathday= None, gender= None, shows= None):
    engine = create_engine('sqlite:///z5334390.db', echo = True)
    
    Session = sessionmaker(bind = engine)
    session = Session()
     
    result = session.query(Actor).get(id)
    
    if result is None:
        return 0
    else:
        if name is not None:
            result.name = name
        if country is not None:
            result.country = country
        if birthday is not None:
            result.birthday = datetime.strptime(birthday, '%Y-%m-%d').date()
        if deathday is not None:
            result.deathday = datetime.strptime(deathday, '%Y-%m-%d').date()
        if gender is not None:
            result.gender = gender
            
        curr_time = str(datetime.now())[:19]
        result.last_update = datetime.strptime(curr_time, '%Y-%m-%d %H:%M:%S')
         
        session.commit()
    
        if shows is not None:
            conn = engine.connect()
            stmt = shows_table.delete().where(shows_table.c.actor_id == id)
            conn.execute(stmt)
            for show in shows:
                add_shows_to_db(id, show)
        
        
        HOST_NAME, PORT = request.host.split(':')
        output = {"id": id,
                  "last-update": str(result.last_update),
                    "_links": {
                        "self": {
                          "href": "http://"+HOST_NAME+":"+PORT+"/actors/"+str(id)
                        }
                    }
                 }
    
    return output


def retrieve_actors(order= '+id', page= 1, size= 10, filter= 'id,name'):
    engine = create_engine('sqlite:///z5334390.db', echo = True)
    
    Session = sessionmaker(bind = engine)
    session = Session()
     
    attrs = filter.split(',')
    for i in range(len(attrs)):
        attrs[i] = attrs[i].strip()
     
    order_by = order.split(',')
    for i in range(len(order_by)):
        order_by[i] = order_by[i].strip()
        if order_by[i][0] == '-':
            order_by[i] = order_by[i].replace('-', ' ')
            order_by[i] = order_by[i] + ' desc '
        else:
            order_by[i] = order_by[i].replace('+', ' ')
            order_by[i] = order_by[i] + ' asc '
    
    order_by = ','.join(order_by)
    
    result = session.query(Actor).from_statement(text("SELECT * FROM actors order by "+order_by)).all()
    
    actors_list = []
    
    count = 0
    for row in result:
        count = count+1
        
        if count > size*(page-1) and count <= size*page:
            data = dict()
            if 'id' in attrs:
                data['id'] = row.id
            if 'name' in attrs:
                data['name'] = row.name
            if 'country' in attrs:
                data['country'] = row.country
            if 'birthday' in attrs:
                data['birthday'] = row.birthday
                if row.birthday is not None:
                    data['birthday'] = str(row.birthday)
            if 'deathday' in attrs:
                data['deathday'] = row.deathday
                if row.deathday is not None:
                    data['deathday'] = str(row.deathday)
            if 'last-update' in attrs or 'last_update' in attrs:
                data['last-update'] = str(row.last_update)
            
            actors_list.append(data)
        
    return actors_list


def get_total_count():
    
    engine = create_engine('sqlite:///z5334390.db', echo = True)    
    Session = sessionmaker(bind = engine)
    session = Session()
    result = session.query(Actor).count()
    return result


def get_last_24_hrs_count():
    
    engine = create_engine('sqlite:///z5334390.db', echo = True)    
    Session = sessionmaker(bind = engine)
    session = Session()
    result = session.query(Actor).all()
    
    count = 0
    for row in result:
        if (datetime.now() - row.last_update).days < 1:
            count += 1
            
    return count


def get_country_stats():    
    
    engine = create_engine('sqlite:///z5334390.db', echo = True)    
    Session = sessionmaker(bind = engine)
    session = Session()
    
    result = session.query(Actor).all()
    
    country_stats = dict()
    total = 0
    for row in result:
        total += 1
        if row.country is None:
            if 'Unknown' in country_stats.keys():
                country_stats['Unknown'] += 1
            else:                
                country_stats['Unknown'] = 1
        else:
            if row.country in country_stats.keys():
                country_stats[row.country] += 1
            else:                
                country_stats[row.country] = 1
    
    for key in country_stats.keys():
        country_stats[key] = (country_stats[key] / total) * 100
        country_stats[key] = float('{0:.2f}'.format(country_stats[key]))
        
    return country_stats


def get_birthday_stats():    
    
    engine = create_engine('sqlite:///z5334390.db', echo = True)    
    Session = sessionmaker(bind = engine)
    session = Session()
    result = session.query(Actor).all()
    
    birthday_stats = dict()
    birthday_stats['January'] = 0
    birthday_stats['February'] = 0
    birthday_stats['March'] = 0
    birthday_stats['April'] = 0
    birthday_stats['May'] = 0
    birthday_stats['June'] = 0
    birthday_stats['July'] = 0
    birthday_stats['August'] = 0
    birthday_stats['September'] = 0
    birthday_stats['October'] = 0
    birthday_stats['November'] = 0
    birthday_stats['December'] = 0
    
    months = dict()
    months[1] = 'January'
    months[2] = 'February'
    months[3] = 'March'
    months[4] = 'April'
    months[5] = 'May'
    months[6] = 'June'
    months[7] = 'July'
    months[8] = 'August'
    months[9] = 'September'
    months[10] = 'October'
    months[11] = 'November'
    months[12] = 'December'
    
    total = 0
    
    for row in result:
        total += 1
        if row.birthday is not None:
            birthday_stats[months[row.birthday.month]] += 1
        else:
            if 'Unknown' in birthday_stats.keys():
                birthday_stats['Unknown'] += 1
            else:
                birthday_stats['Unknown'] = 1
    
    for key in birthday_stats.keys():
        birthday_stats[key] = (birthday_stats[key] / total) * 100
        birthday_stats[key] = float('{0:.2f}'.format(birthday_stats[key]))
        
    return birthday_stats


def get_gender_stats():    
    
    engine = create_engine('sqlite:///z5334390.db', echo = True)    
    Session = sessionmaker(bind = engine)
    session = Session()
    result = session.query(Actor).all()
    
    gender_stats = dict()
    total = 0
    for row in result:
        total += 1
        if row.gender is None:
            if 'Unknown' in gender_stats.keys():
                gender_stats['Unknown'] += 1
            else:                
                gender_stats['Unknown'] = 1
        else:
            if row.gender in gender_stats.keys():
                gender_stats[row.gender] += 1
            else:                
                gender_stats[row.gender] = 1
    
    for key in gender_stats.keys():
        gender_stats[key] = (gender_stats[key] / total) * 100
        gender_stats[key] = float('{0:.2f}'.format(gender_stats[key]))
        
    return gender_stats


def get_life_status_stats():    
    
    engine = create_engine('sqlite:///z5334390.db', echo = True)    
    Session = sessionmaker(bind = engine)
    session = Session()
    result = session.query(Actor).all()
    
    life_stats = dict()
    total = 0
    life_stats['Alive'] = 0
    life_stats['Deceased'] = 0
    for row in result:
        total += 1
        if row.deathday is None or row.deathday == '':
            life_stats['Alive'] += 1
        else:
            life_stats['Deceased'] += 1
    
    for key in life_stats.keys():
        life_stats[key] = (life_stats[key] / total) * 100
        life_stats[key] = float('{0:.2f}'.format(life_stats[key]))
        
    return life_stats


if __name__ == '__main__':

    create_db()   
    
    # run the application
    app.run(debug=True)