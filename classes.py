from datetime import datetime

class Issue(object):
    """ An aggregate issue
        Basically, this should contain the details of the important parts of all
        related issues.
    """
    summary = ""
    assignee = ""
    date_created = ""
    date_completed = ""
    date_in_progress = ""
    story_points = 0
    key = ""
    epic = ""
    Priority = ""
    linked_issue_keys = []    # list of ids of all the issues that are aggregated
                          # NOT related issues, only the same issue on different
                          # platforms, QA, etc.

    def __init__(self, issuetype, summary, key):
        self.issuetype = issuetype
        self.summary = summary
        self.key = key

    def add_date_created(self, d):
        ''' Sets date_created ONLY IF the incoming date is earlier than existing date_created
        '''

        if self.date_created == "":
            self.date_created = d
        else:
            if datetime.strptime(d, "%Y-%m-%d") < datetime.strptime(self.date_created, "%Y-%m-%d"):
                self.date_created = d
            else:
                pass

    def add_date_completed(self, d):
        ''' Sets date_completed ONLY IF the incoming date is later than existing date_completed
        '''
        if self.date_completed == "":
            self.date_completed = d
        else:
            if datetime.strptime(d, "%Y-%m-%d") > datetime.strptime(self.date_completed, "%Y-%m-%d"):
                self.date_completed = d
            else:
                pass

    def add_date_in_progress(self, d):
        ''' Sets date_in_progress ONLY IF the incoming date is earlier than existing date_in_progress
        '''

        if self.date_in_progress == "":
            self.date_in_progress = d
        else:
            if datetime.strptime(d, "%Y-%m-%d") < datetime.strptime(self.date_created, "%Y-%m-%d"):
                self.date_in_progress = d
            else:
                pass
