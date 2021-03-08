# Players-data-base-testing
**Test description:** This test will run in subproccess a Linux executable that implements a web server that, in turn, exposes an HTTP REST API on local port 8000. The API allows querying a database of players. It returns a simple JSON body that contains IDs and names of players.
In addition, test will find bugs in the API, according to this general test strategy:
- All ID's/names should have no empty or null values, each ID/name should not be associated with more that one companion.			
- Test will also self check if new unique name-ID pairs are are pulled from DB, and check for environmental issues.			
- Each test can be excuted seperatly by py.test.mark framwork or in one global run.
For more details and bug list: see **test_report.xlsx**

**File navigation:**
- server_api_test.py - the test.
- twtask - Linux executable.
- pytest.ini - pytest framwork configs.
- Dockerfile - file to build image for testing via docker.
- test_report.xlsx - file with testcases, reproduce and buglist
