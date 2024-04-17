query='query {
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
}'

# query='query {
#     repository(owner: \"saularraffi\", name: \"test\") {
#         id
#         nameWithOwner
#         description
#         url
#     }
# }'

query="$(echo $query)"

github_token=$(gh auth token)

curl -X POST https://api.github.com/graphql \
    -H "Authorization: bearer $github_token" \
    -H "Content-Type: application/json" \
    -d "{ \"query\": \"$query\"}"
    