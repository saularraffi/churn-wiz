import requests
import json
import os
import re

GH_TOKEN        = command_output = os.popen('gh auth token').read().strip()
GH_GRAPHQL_URL  = 'https://api.github.com/graphql'
REQUEST_HEADERS = { "Authorization": f"Bearer { GH_TOKEN }" }
OWNER           = "saularraffi"
REPO            = "test"
BRANCH          = "mybranch"

def getFileCommitHistoryQuery(filename):
    global OWNER
    global REPO
    global BRANCH

    return '''
        query {
            repository(owner: \"%s\", name: \"%s\") {
                object(expression: \"%s\") {
                    ... on Commit {
                        blame(path: \"%s\") {
                            ranges {
                                commit {
                                    committedDate
                                }
                                startingLine
                                endingLine
                            }
                        }
                    }
                }
            }
        }
    ''' % (OWNER, REPO, BRANCH, filename)

def fetchFileCommitHistory(query):
    response = requests.post(
        GH_GRAPHQL_URL,
        headers=REQUEST_HEADERS,
        json={'query': query}
    )

    commits = response.json()['data']['repository']['object']['blame']['ranges']

    commitHistory = []

    for commit in commits:
        date = commit['commit']['committedDate']
        startL = commit['startingLine']
        endL = commit['endingLine']
        commitHistory.append(f"({startL},{endL}) {date}")
    
    return commitHistory

def fetchFilesChanged(prNumber):
    url = f'https://api.github.com/repos/{OWNER}/{REPO}/pulls/{13}/files'
    response = requests.get(url, headers=REQUEST_HEADERS)
    if response.status_code == 200:
        files_changed = response.json()
        return [file["filename"] for file in files_changed]

def getPrDiffFiles(prNumber):
    url = f'https://api.github.com/repos/{OWNER}/{REPO}/pulls/{prNumber}/files'
    headers = {
        "Authorization": f"Bearer {GH_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return { 'error': f'{response.status_code} - {response.text}' }
    
    return { 'data': response.json() }

def splitHunks(patch):
    pattern = r"(@@ [^@]+ @@)"
    splitResult = re.split(pattern, patch)

    result = []
    for i in range(1, len(splitResult), 2):
        result.append(splitResult[i] + splitResult[i + 1])
    
    return result

def getValuesFromHunkHeader(hunkHeader):
    hunkParts = hunkHeader.split()
    originalInfo = hunkParts[1][1:]
    newInfo = hunkParts[2][1:]

    originalStart, originalCount = map(int, originalInfo.split(','))
    newStart, newCount = map(int, newInfo.split(','))

    return { 
        '-start': originalStart,
        '-count': originalCount,
        '+start': newStart,
        '+count': newCount 
    }

def getLinesChangedInPatch(patch):
    hunks = splitHunks(patch)

    linesChanged = []

    for hunk in hunks:
        lines = hunk.split('\n')
        hunkValues = getValuesFromHunkHeader(lines[0])

        changeEncountered = False
        start = offset = hunkValues['-start']
        lastChangedLine = 0

        for n, line in enumerate(lines[1:]):
            lineNumber = offset + n

            if line.startswith('-') and not changeEncountered:
                start = lineNumber

            if line.startswith('-'):
                changeEncountered = True
            
            if not line.startswith('-') and changeEncountered:
                linesChanged.append((start, lineNumber - 1))
                changeEncountered = False

    return linesChanged

def getLinesChangedInPr(prData):
    prData = getPrDiffFiles(41)

    if 'error' in prData.keys():
        return {}
    
    diffTable = {}

    for file in prData['data']:
        patch = file.get("patch", "")
        linesChanged = getLinesChangedInPatch(patch)
        diffTable[file['filename']] = linesChanged
    
    return diffTable

changeData = getLinesChangedInPr(41)
print(changeData)