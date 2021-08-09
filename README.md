https://scikit-learn.org/stable/tutorial/text_analytics/working_with_text_data.html

# phoenix

![Screenshot](src/Screenshot.png "Phoenix Screenshot")

Neural Network Bulletin Board System using SciKit-Learn

_Alpha Phase_

https://developer.atlassian.com/server/confluence/confluence-rest-api-examples/
https://developer.atlassian.com/cloud/jira/service-desk/rest/
https://docs.gitlab.com/ee/api/README.html

## Purpose

Seamless Collection and Search of Tickets, Hotfixes, Patches and Mini-Documentations. With close ties to [Petrus](https://github.com/Skadisson/petrus) and it's logic. Using [Jira Service Desk](https://docs.atlassian.com/jira-servicedesk/REST/3.9.1/) and [Confluence](https://docs.atlassian.com/ConfluenceServer/rest/7.0.3/) APIs.

## Goals

Versioning of content, authors and editors. Referencing towards Jira, Git and Confluence - basically building a connecting hub between those worlds. Everything combined and sorted under three aspects: 

### Popularity

How frequented is the entity, commit, documentation or ticket?

### Context 

What similar entities, commits, documentations or tickets exist?

### Relevancy

How relevant are the entities to a search request, commit, documentation or ticket?

## UI Flow

![alt text](src/ui_flow.png "UI Flow")

## Flow diagram

![alt text](src/flow_diagram.png "Flow Diagram")

## Wireframe

![alt text](src/wireframe.png "Wireframe")


___

pip list -l
<pre>
Package              Version
-------------------- -----------
atlassian-python-api 3.13.0
certifi              2021.5.30
cffi                 1.14.6
chardet              4.0.0
charset-normalizer   2.0.4
cryptography         3.4.7
Deprecated           1.2.12
dnspython            2.1.0
future               0.18.2
httplib2             0.19.1
idna                 3.2
joblib               1.0.1
mkl-fft              1.3.0
mkl-random           1.2.2
mkl-service          2.4.0
numpy                1.21.1
oauth2               1.9.0.post1
oauthlib             3.1.1
pip                  21.2.2
pycparser            2.20
pymongo              3.12.0
pyparsing            2.4.7
PyYAML               5.4.1
requests             2.26.0
requests-oauthlib    1.3.0
scikit-learn         0.24.2
scipy                1.7.1
setuptools           57.4.0
six                  1.16.0
threadpoolctl        2.2.0
tlslite              0.4.9
urllib3              1.26.6
Wand                 0.6.6
webscreenshot        2.94
Werkzeug             2.0.1
wheel                0.36.2
wincertstore         0.2
wrapt                1.12.1
</pre>

Use "pip list --outdated --format=columns" to check for outdated versions.
