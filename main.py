import requests
import os

GH_TOKEN = command_output = os.popen('gh auth token').read().strip()
GH_GRAPHQL_URL = 'https://api.github.com/graphql'

query='''
query {
  repository(owner: \"saularraffi\", name: \"test\") {
    object(expression: \"mybranch\") {
      ... on Commit {
        blame(path: \"README.md\") {
          ranges {
            commit {
              committedDate
              author {
                name
                email
              }
            }
            startingLine
            endingLine
          }
        }
      }
    }
  }
}
'''

response = requests.post(
    GH_GRAPHQL_URL,
    headers={'Authorization': f'bearer {GH_TOKEN}'},
    json={'query': query}
)

commits = response.json()['data']['repository']['object']['blame']['ranges']

for commit in commits:
    date = commit['commit']['committedDate']
    startL = commit['startingLine']
    endL = commit['endingLine']
    print("({},{}) {}".format(startL, endL, date))