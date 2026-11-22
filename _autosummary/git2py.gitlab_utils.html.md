# git2py.gitlab_utils

Stores to talk to gitlab, using requests.

### Example

```text
ogl = GitLabAccessor(base_url="http://...", project_name=None)

print(ogl.get_project_names())  # prints all project names
ogl.set_project("PROJECT_NAME")  # sets the project to "PROJECT_NAME"
print(
    ogl.get_branch_names()
)  # gets the branch names of current project (as set previously)
print(
    ogl.get_branch("master")
)  # gets a json of information about the master branch of current project.
```

### Functions

| `get_request_constructor`()   |    |
|-------------------------------|----|
| `mk_url_factory`(base_url)    |    |

### Classes

| `GitLabAccessor`([base_url, project_name, ...])                                                 |    |
|-------------------------------------------------------------------------------------------------|----|
| [`GitlabProjectReader`](#git2py.gitlab_utils.GitlabProjectReader)(base_url[, private_token]) |    |

### *class* git2py.gitlab_utils.GitlabProjectReader(base_url, private_token=None)

Bases: `KvReader`
