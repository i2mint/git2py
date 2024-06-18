"""
Git tools.

Note: The intent of this package was to provide a simple, high-level interface to git. 
Namely to github and gitlab, allowing for easy access to the resources of these 
platforms, and that would be easy to extend to other platforms.

What ended up happening is that we accumulated some useful tools, but stopped 
development after our main purpose was acheived (migrating from gitlab to github).

We may pick this project up again in the future, but for now, it's in a state of
"good enough for now", and we're keeping it around to use the tools we've built.

You may want to check out some other projects that may have more active development:
- [hubcap](https://github.com/thorwhalen/hubcap): A mapping interface to github
- [ps](https://github.com/thorwhalen/ps): Call any available system command from python
- some bits of 
[wads](https://github.com/i2mint/wads/blob/b82a534bfc9c3f20713e0768291c67c9c2467e01/wads/util.py#L39) and 
[isee](https://github.com/i2mint/isee/blob/54fa4b2343cb2510f7a9cc34fe4e512ef6050795/isee/common.py#L17)

"""
from git2py import gitlab_utils
import hubcap as github
