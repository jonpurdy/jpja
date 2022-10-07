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

# Jon
from jpja.timeline import generate_timeline
from jpja.classes import Issue
from jpja.functions import get_time_difference_from_strings
from jpja.functions import string_to_date
#from functions import compare_two_sentences
from jpja.functions import generate_nx_graph
from jpja.functions import plotly_graph
from jpja import jira 


###################
#     Options     #
###################


import argparse
parser = argparse.ArgumentParser()

# --domain "https://whatever.atlassian.net" --username "user@email.com" --token "jira_token"
parser.add_argument("--domain", help="Jira domain")
parser.add_argument("--username", help="Jira username")
parser.add_argument("--token", help="Jira token")

args = parser.parse_args()

# print( "Domain {} User {} Password {} ".format(
#         args.domain,
#         args.username,
#         args.token,
#         ))

headers = {"Accept": "application/json"}
USERNAME = args.username
TOKEN = args.token
AUTH = HTTPBasicAuth(USERNAME, TOKEN)
DOMAIN = args.domain

GET_IN_PROGRESS = False # if set to True, will break because auth details aren't passed
GROUP_NO_EPICS = False # if true, connects issues without an Epic to a "No Epic" node
MAKE_TIMELINE = True
MAKE_NETWORK_GRAPH = True

# need to get this from the Jira API, per instance so it will change
story_points_custom_field = "customfield_10016" 
epic_link_custom_field = "customfield_10014"


JQL_QUERY = "project IN (TEST) AND statuscategory NOT IN (Done)"

# end of JQL for everyone
JQL_END = " AND issuetype not in (subTaskIssueTypes(), Epic) ORDER BY project ASC, 'Epic Name' ASC, created ASC, issuetype ASC"
JQL = JQL_QUERY + JQL_END

# options: issuetype, priority
colorize_by = "issuetype"

###################
#   Note          #
###################

# if data isn't refreshing:
# delete all_issues.obj and all_epics.obj

###################
#   Let's start   #
###################

def main():
    exit()

    # all_epics_dict = jira.get_all_epics(AUTH, DOMAIN)

    # # just for testing, needed if we don't have story point or epic link custom field ID
    # # jira.get_story_points_custom_field_id(AUTH, DOMAIN, headers)
    # # exit()
    
    # everything = jira.load_issues(AUTH, DOMAIN, JQL)
    # print("This is the JQL STRING: ",JQL)

    # issue_list, issue_types_list, priorities_list = jira.get_issue_objects_list(everything, GET_IN_PROGRESS)


    # # this will print at the top if there are any duplicate issues
    # debug_find_duplicates(everything)

    # print("issue count: %s" % len(everything))


    # tab = PrettyTable()
    # #tab.set_style(MSWORD_FRIENDLY)
    # tab.field_names = ["Key", "Type", "Epic", "Summary", "Prio", "Assignee", "Created", "In Progress", "Resolution Date", "Days", "DIP", "SP", "DPP"]

    # timeline_list = []


    # # calculating days per point and adding to the table
    # # also creating the plotly timeline
    # #for x in issue_list:
    # for x in track(issue_list, description="Calculating DPP, adding to the table and plotly timeline..."):      

    #     # print("x.date_created: %s" % x.date_created)
    #     # print("x.date_completed: %s" % x.date_completed)

    #     # 2022-07-20
    #     # adding further calculations here
    #     days_since_created = get_time_difference_from_strings(x.date_created, x.date_completed).days

    #     try:
    #         if GET_IN_PROGRESS:
    #             days_in_progress = get_time_difference_from_strings(x.date_in_progress, x.date_completed).days
    #         else:
    #             days_in_progress = 0
    #     except Exception as e:
    #         print(e)
    #         days_in_progress = 0

    #     # added days per point in 2022
    #     try:
    #         # hack? added 2022-07-20 so that the Gantt charts work with in progress
    #         # so if GET_IN_PROGRESS, it calculates from date_in_progress, otherwise it does date_created
    #         if GET_IN_PROGRESS:
    #             days_per_point = round(days_in_progress / x.story_points, 1)
    #         else:
    #             days_per_point = round(days_since_created / x.story_points, 1)

    #         # the code from before adding GET_IN_PROGRESS
    #         #days_per_point = round(get_time_difference_from_strings(x.date_created, x.date_completed).days / x.story_points, 1)
    #     except:
    #         days_per_point = "n/a"

    #     tab.add_row([
    #          x.key, \
    #          x.issuetype, \
    #          x.epic, \
    #          x.summary[:30], \
    #          x.priority, \
    #          x.assignee, \
    #          x.date_created, \
    #          x.date_in_progress, \
    #          x.date_completed, \
    #          days_since_created, \
    #          days_in_progress, \
    #          x.story_points, \
    #          days_per_point
    #          ])


    #     if MAKE_TIMELINE:

    #         if colorize_by == "issuetype":
    #             resource = x.issuetype
    #         elif colorize_by == "priority":
    #             resource = x.priority

    #         # hack? added 2022-05-02
    #         # so that the Gantt charts work with in progress
    #         if GET_IN_PROGRESS:
    #             x.date_created = x.date_in_progress

    #         timeline_list.append(dict(
    #                   Start=x.date_created, \
    #                   Finish=x.date_completed, \
    #                   Resource=resource, \
    #                   Task=x.key + " " + x.summary[:25]
    #                   ))

    # # changing appearance of prettytables:
    # # https://ptable.readthedocs.io/en/latest/tutorial.html#changing-the-appearance-of-your-table-the-easy-way
    # #print(tab.get_string(sortby="Type"))


    # ##### table stuff
    # print(tab)

    # # write html table to file
    # f = open("export.html", "w")
    # f.write(tab.get_html_string())
    # f.close()


    # ###### plotly stuff 

    # if MAKE_TIMELINE:

    #     colors_by_issue_type = {}
    #     colors_by_priority = {}

    #     palette = sns.color_palette("husl", len(issue_types_list)).as_hex() # original
    #     x = 0
    #     for t in issue_types_list:
    #         colors_by_issue_type[t] = palette[x]
    #         x += 1

    #     print("colors_by_issue_type: %s" % colors_by_issue_type)

    #     # 2022-06-15 not needed anymore, just updated Task, Bug, Story, Epic
    #     # colors_by_issue_type = dict(Story='rgb(87, 191, 136)', \
    #     #                 Task='rgb(64, 145, 247)', \
    #     #                 Bug='rgb(229, 50, 86)', \
    #     #                 Epic='rgb(195, 63, 186)', \
    #     #                 )

    #     # overwriting the generated palette to match Jira
    #     # issue types colors
    #     colors_by_issue_type["Story"] = 'rgb(87, 191, 136)'
    #     colors_by_issue_type["Task"] = 'rgb(64, 145, 247)'
    #     colors_by_issue_type["Bug"] = 'rgb(229, 50, 86)'
    #     colors_by_issue_type["Epic"] = 'rgb(195, 63, 186)'

    #     print("colors_by_issue_type: %s" % colors_by_issue_type)

    #     #priority colors
    #     colors_by_priority["P1"] = '#FF0000'
    #     colors_by_priority["P2"] = '#FFA200'
    #     colors_by_priority["P3"] = '#FFFF00'
    #     colors_by_priority["P4"] = '#00FF33'
    #     colors_by_priority["np"] = '#777777'


    #     if colorize_by == "issuetype":
    #         colors = colors_by_issue_type
    #     elif colorize_by == "priority":
    #         colors = colors_by_priority
    #     else:
    #         print("Please set colorize_by variable.")
    #         exit()

    #     print("colorize_by: %s" % colorize_by)
    #     print("colors: %s" % colors)


    #     print("Generating timeline for all issues...")
    #     # colors = 0
    #     height = len(everything) * 20
    #     print("height: %s" % height)
    #     #height = 900
    #     generate_timeline(timeline_list, "timeline-all.html", colors, height)


    # # epic map generation
    # if MAKE_NETWORK_GRAPH:
    #     G, color_map = generate_nx_graph(all_epics_dict, issue_list, GROUP_NO_EPICS)
    #     plotly_graph(G, color_map)



def debug_find_duplicates(everything):

    dupes_dict = {}

    for i in everything:
        dupes_dict[i['key']] = 0

    for i in everything:
        dupes_dict[i['key']] += 1

    for d in dupes_dict:
        if dupes_dict[d] > 1:
            print(d, dupes_dict[d])


if __name__ == '__main__':
    main()