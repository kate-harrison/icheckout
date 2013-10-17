Intelligent branch switching for git
====================================

Description
-----------
This script performs "intelligent checkout" of branches in git. When
switching from branch testA to branch testB, the following happens, in order:

  * Stashes any works in progress on testA
  * Checks out testB
  * Looks for an auto-stashed stash on testB; if found, it is applied and
     popped

This allows users to quickly switch between branches, keeping their
intermediate work without needing to commit it first. This is intended to
mimic the behavior a user would get from having a separate clone for each
branch and switching directories in order to switch branches.


Usage
-----
First, make sure that the script is executable ("chmod a+x icheckout.py").
After this, you can simply call <pre>./icheckout.py destination_branch</pre> You
should be able to use any other arguments normally used with 'git checkout'
as long as the branch name is the last argument to this script.


To make an alias (so you can use, for example, "git icheckout
destination_branch" instead), add the following lines to your .git/config:

    [alias]
       icheckout = !./icheckout.py

In my setup, icheckout.py is in the root folder of the repository. You may
prefer to store the script in your /usr/local/bin folder.


Bugs
----
I have not thoroughly tested this script. If you find any bugs, please report
them using the github issue tracker or fix them and issue a pull request.
