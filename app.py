from flask import Flask,request
from flask import render_template
# loading the request and saving it for later
import requests
from requests.auth import HTTPBasicAuth
import json
import pickle 

# dates
import datetime
import dateutil.parser

# table generation
from prettytable import PrettyTable
from prettytable import MSWORD_FRIENDLY

# pretty printing and niceties
from pprint import pprint
from rich import print
from rich import inspect
from rich.progress import track
from time import sleep
import plotly.graph_objects as go
import sys

# colors
import seaborn as sns

# standard deviation and variance calculation
import statistics

# Jon
from timeline import generate_timeline
from classes import Issue
from functions import get_time_difference_from_strings
from functions import string_to_date
#from functions import compare_two_sentences
from functions import generate_nx_graph
from functions import plotly_graph
import jira 


###################
#     Options     #
###################


import argparse
parser = argparse.ArgumentParser()


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True



def debug_find_duplicates(everything):

    dupes_dict = {}

    for i in everything:
        dupes_dict[i['key']] = 0

    for i in everything:
        dupes_dict[i['key']] += 1

    for d in dupes_dict:
        if dupes_dict[d] > 1:
            print(d, dupes_dict[d])




@app.route("/",methods=['GET','POST'])
def index():
    if request.method == "POST":
        if request.form['action'] == "send_jql":
            # --domain "https://whatever.atlassian.net" --username "user@email.com" --token "jira_token"
            domain = request.form['domain']
            username = request.form['username']
            token = request.form['token']
            story_points_custom_field = request.form['spcustomfieldid']
            headers = {"Accept": "application/json"}
            print(request)

            USERNAME = username
            TOKEN = token
            AUTH = HTTPBasicAuth(USERNAME, TOKEN)
            DOMAIN = domain

                        
            GET_IN_PROGRESS = True # if set to True, will break because auth details aren't passed
            GROUP_NO_EPICS = False # if true, connects issues without an Epic to a "No Epic" node
            # MAKE_TIMELINE = True
            # MAKE_NETWORK_GRAPH = True
            # GET_ASSIGNEE_THROUGHPUT = True

            MAKE_TIMELINE = 'timeline' in request.form
            MAKE_NETWORK_GRAPH = 'network_graph' in request.form
            GET_ASSIGNEE_THROUGHPUT = 'assignee_throughput' in request.form

            # story_points_custom_field comes from request.form
            epic_link_custom_field = "customfield_10014"

            # write the last domain to a file
            # later on (in jira.py), if the last domain is different than current domain, delete epics.obj
            f = open("temp/last_domain.txt","w+")
            f.write(domain)
            f.close()

            # write the last time to a file
            # later on (in jira.py), if the last time is more than 1h old, delete epics.obj
            f = open("temp/last_time.txt","w+")
            f.write(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"))
            f.close()


            JQL = request.form['jql']
            #print(JQL)
            colorize_by = "issuetype"
            all_epics_dict = jira.get_all_epics(AUTH, DOMAIN)

            # just for testing, needed if we don't have story point or epic link custom field ID
            story_points_custom_field_id = jira.get_story_points_custom_field_id(AUTH, DOMAIN, headers)
            #print("story points custom field id = %s" % story_points_custom_field_id)

            print("This is the JQL STRING: ",JQL)
            everything = jira.load_issues(AUTH, DOMAIN, JQL)
            if len(everything) > 0:

                issue_list, issue_types_list, priorities_list = jira.get_issue_objects_list(everything, GET_IN_PROGRESS, AUTH, DOMAIN)


                # this will print at the top if there are any duplicate issues
                debug_find_duplicates(everything)

                print("issue count: %s" % len(everything))


                tab = PrettyTable()
                #tab.set_style(MSWORD_FRIENDLY)
                tab.field_names = ["Key", "Type", "Epic", "Summary", "Prio", "Assignee", "Created", "In Progress", "Resolution Date", "Days", "DIP", "SP", "DPP"]

                timeline_list = []


                # calculating days per point and adding to the table
                # also creating the plotly timeline
                #for x in issue_list:
                for x in track(issue_list, description="Calculating DPP, adding to the table and plotly timeline..."):      

                    # print("x.date_created: %s" % x.date_created)
                    # print("x.date_completed: %s" % x.date_completed)

                    # 2022-07-20
                    # adding further calculations here
                    days_since_created = get_time_difference_from_strings(x.date_created, x.date_completed).days

                    try:
                        if GET_IN_PROGRESS:
                            days_in_progress = get_time_difference_from_strings(x.date_in_progress, x.date_completed).days
                        else:
                            days_in_progress = 0
                    except Exception as e:
                        print(e)
                        days_in_progress = 0

                    # added days per point in 2022
                    try:
                        # hack? added 2022-07-20 so that the Gantt charts work with in progress
                        # so if GET_IN_PROGRESS, it calculates from date_in_progress, otherwise it does date_created
                        if GET_IN_PROGRESS:
                            days_per_point = round(days_in_progress / x.story_points, 1)
                        else:
                            days_per_point = round(days_since_created / x.story_points, 1)

                        # the code from before adding GET_IN_PROGRESS
                        #days_per_point = round(get_time_difference_from_strings(x.date_created, x.date_completed).days / x.story_points, 1)
                    except:
                        days_per_point = "n/a"

                    tab.add_row([
                        x.key, \
                        x.issuetype, \
                        x.epic, \
                        x.summary[:30], \
                        x.priority, \
                        x.assignee, \
                        x.date_created, \
                        x.date_in_progress, \
                        x.date_completed, \
                        days_since_created, \
                        days_in_progress, \
                        x.story_points, \
                        days_per_point
                        ])


                    if MAKE_TIMELINE:

                        if colorize_by == "issuetype":
                            resource = x.issuetype
                        elif colorize_by == "priority":
                            resource = x.priority

                        # hack? added 2022-05-02
                        # so that the Gantt charts work with in progress
                        if GET_IN_PROGRESS:
                            x.date_created = x.date_in_progress

                        timeline_list.append(dict(
                                Start=x.date_created, \
                                Finish=x.date_completed, \
                                Resource=resource, \
                                Task=x.key + " " + x.summary[:25]
                                ))

                # changing appearance of prettytables:
                # https://ptable.readthedocs.io/en/latest/tutorial.html#changing-the-appearance-of-your-table-the-easy-way
                #print(tab.get_string(sortby="Type"))


                ##### table stuff
                #print(tab)
                # disabled 2023-02-09

                # write html table to file instead of printing it
                f = open("templates/export.html", "w")
                f.write("{% extends 'default.html' %} {%block content%}")
                f.write(tab.get_html_string(attributes={"id":"this_table", "class":"html_table"}))
                f.write("{%endblock%}")
                f.close()



                ####
                # Assignee
                ####

                if GET_ASSIGNEE_THROUGHPUT:

                    intervals = []
                    field_names = ['assignee']
                    start_date = datetime.datetime(2022, 9, 27) # use this one
                    end_date = datetime.datetime(2023, 2, 14)
                    # start_date = datetime.datetime(2023, 1, 3) # debug
                    # end_date = datetime.datetime(2023, 2, 1)   # debug

                    start_date_temp = start_date
                    while start_date_temp <= end_date:
                        field_names.append(f'{start_date_temp.strftime("%Y-%m-%d")}')
                        start_date_temp += datetime.timedelta(days=14)

                    field_names.extend(["stdev", "variance"])    # using extend instead of append to append multiple elements

                    # debug to confirm start date is untouched
                    # print("start date: %s" % start_date)
                    # print("start date temp: %s" % start_date_temp)

                    tab_assignee_throughput = PrettyTable()
                    tab_assignee_throughput.field_names = field_names
                    
                    assignees_list = jira.get_assignees_as_objects(issue_list)

                    #for a in track(assignees_list, description="Getting throughput per assignee..."):
                    for a in assignees_list:
                        print(a.account_id + " - " + a.display_name)

                        while start_date <= end_date:
                            two_week_interval_jql = f'AND resolutiondate >= {start_date.strftime("%Y-%m-%d")} AND resolutiondate <= {(start_date + datetime.timedelta(days=13)).strftime("%Y-%m-%d")}'
                            intervals.append(two_week_interval_jql)
                            start_date += datetime.timedelta(days=14)

                        assignee_throughput_row = [a.display_name] # used to input into the table as a row for an assignee
                        for b in intervals:
                            this_jql = "assignee = %s AND issuetype NOT IN (Epic) %s ORDER BY created DESC" % (a.account_id, b)
                            result = jira.load_issues(AUTH, DOMAIN, this_jql)
                            issue_list1, issue_types_list1, priorities_list1 = jira.get_issue_objects_list(result, False)
                            print("%s: %s" % (a.display_name, len(issue_list1)))
                            assignee_throughput_row.append(len(issue_list1))

                        # calculate stdev and variance
                        stdev = round(statistics.stdev(assignee_throughput_row[1:]), 1)     # [1:] excludes the first element (a.display_name)
                        variance = round(statistics.variance(assignee_throughput_row[1:]), 1)
                        assignee_throughput_row.extend([stdev, variance])

                        tab_assignee_throughput.add_row(assignee_throughput_row)

                    print(tab_assignee_throughput)

                    # write table to file
                    f = open("templates/assignee_throughput.html", "w")
                    f.write("{% extends 'default.html' %} {%block content%}")
                    f.write(tab_assignee_throughput.get_html_string(attributes={"id":"this_table", "class":"html_table"}))
                    f.write("{%endblock%}")
                    f.close()



                ###### plotly stuff 

                if MAKE_TIMELINE:

                    colors_by_issue_type = {}
                    colors_by_priority = {}

                    palette = sns.color_palette("husl", len(issue_types_list)).as_hex() # original
                    x = 0
                    for t in issue_types_list:
                        colors_by_issue_type[t] = palette[x]
                        x += 1

                    print("colors_by_issue_type: %s" % colors_by_issue_type)

                    # 2022-06-15 not needed anymore, just updated Task, Bug, Story, Epic
                    # colors_by_issue_type = dict(Story='rgb(87, 191, 136)', \
                    #                 Task='rgb(64, 145, 247)', \
                    #                 Bug='rgb(229, 50, 86)', \
                    #                 Epic='rgb(195, 63, 186)', \
                    #                 )

                    # overwriting the generated palette to match Jira
                    # issue types colors
                    colors_by_issue_type["Story"] = 'rgb(87, 191, 136)'
                    colors_by_issue_type["Task"] = 'rgb(64, 145, 247)'
                    colors_by_issue_type["Bug"] = 'rgb(229, 50, 86)'
                    colors_by_issue_type["Epic"] = 'rgb(195, 63, 186)'

                    print("colors_by_issue_type: %s" % colors_by_issue_type)

                    #priority colors
                    colors_by_priority["P1"] = '#FF0000'
                    colors_by_priority["P2"] = '#FFA200'
                    colors_by_priority["P3"] = '#FFFF00'
                    colors_by_priority["P4"] = '#00FF33'
                    colors_by_priority["np"] = '#777777'


                    if colorize_by == "issuetype":
                        colors = colors_by_issue_type
                    elif colorize_by == "priority":
                        colors = colors_by_priority
                    else:
                        print("Please set colorize_by variable.")
                        exit()

                    print("colorize_by: %s" % colorize_by)
                    print("colors: %s" % colors)


                    print("Generating timeline for all issues...")
                    # colors = 0
                    height = len(everything) * 20
                    print("height: %s" % height)
                    #height = 900
                    generate_timeline(timeline_list, "templates/timeline-all.html", colors, height)


                # epic map generation
                if MAKE_NETWORK_GRAPH:
                    G, color_map = generate_nx_graph(all_epics_dict, issue_list, GROUP_NO_EPICS)
                    plotly_graph(G, color_map)


                colorize_by = "issuetype"
                return render_template("export.html")
           
            else:
                message = "Getting back an empty list. Check the query to make sure it returns at least one result (result containing at least one Jira issue)."
                print(message)
                return render_template("error.html", message=message)
                
    else:
        return render_template("index.html")


@app.route('/timeline_all',methods=['GET'])
def timeline_all():
    return render_template("timeline-all.html")

@app.route('/results',methods=['GET'])
def results():
    return render_template("results.html")

@app.route('/assignee_throughput',methods=['GET'])
def assignee_throughput():
    return render_template("assignee_throughput.html")

@app.route('/get_story_points_custom_field_id',methods=['GET', 'POST'])
def story_points_custom_field():
    if request.method == "POST":
        # if working correct, request.form should have print an ImmutableMultiDict with values
        print(request.form)

        domain = request.form['domain']
        username = request.form['username']
        token = request.form['token']

        # probably not needed since I prepopulate the form
        if not domain:
            return "domain empty"
        if not username:
            return "username empty"
        if not token:
            return "token empty"

        headers = {"Accept": "application/json"}

        auth = HTTPBasicAuth(username, token)
        story_points_custom_field_id = jira.get_story_points_custom_field_id(auth, domain, headers)

        return story_points_custom_field_id

    else:
        return render_template("get_sp_custom_field_id.html")

@app.errorhandler(Exception)          
def basic_error(e):          
    return "%s: %s" % (type(e).__name__, str(e))   

if __name__ == '__main__':
    app.run(debug=True)