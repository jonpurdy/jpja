import classes

def main():

    this_issue = classes.Issue(issuetype = "Story", \
          summary = "Test issue", \
          key = "TEST-1")

    this_issue.date_created = "2020-10-30"
    print("should be 2020-10-30: %s" % this_issue.date_created)

    this_issue.add_date_created("2020-11-01")
    print("should be 2020-10-30: %s" % this_issue.date_created)

    this_issue.add_date_created("2020-10-29")
    print("should be 2020-10-29: %s" % this_issue.date_created)

    this_issue.date_completed = "2020-12-01"
    print("should be 2020-12-01: %s" % this_issue.date_completed)

    this_issue.add_date_completed("2020-11-30")
    print("should be 2020-12-01: %s" % this_issue.date_completed)

    this_issue.add_date_completed("2020-12-02")
    print("should be 2020-12-02: %s" % this_issue.date_completed)

def test_add_date_created():

    this_issue = classes.Issue(issuetype = "Story", \
          summary = "Test issue", \
          first_linked_issue = "TEST-1")

    this_issue.date_created = "2020-10-30"
    assert this_issue.date_created == "2020-10-30"

    this_issue.add_date_created("2020-11-01")
    assert this_issue.date_created == "2020-10-30"

    this_issue.add_date_created("2020-10-29")
    assert this_issue.date_created == "2020-10-29"

def test_add_date_completed():

    this_issue = classes.Issue(issuetype = "Story", \
          summary = "Test issue", \
          first_linked_issue = "TEST-1")

    this_issue.date_completed = "2020-12-01"
    assert this_issue.date_completed == "2020-12-01"

    this_issue.add_date_completed("2020-11-30")
    assert this_issue.date_completed == "2020-12-01"

    this_issue.add_date_completed("2020-12-02")
    assert this_issue.date_completed == "2020-12-02"


if __name__ == '__main__':
    main()