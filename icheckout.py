#!/usr/bin/env python


# # # DESCRIPTION # # #
# This script performs "intelligent checkout" of branches in git. When
# switching from branch testA to branch testB, the following happens, in order:
#   * Stashes any works in progress on testA
#   * Checks out testB
#   * Looks for an auto-stashed stash on testB; if found, it is applied and
#      popped
# This allows users to quickly switch between branches, keeping their
# intermediate work without needing to commit it first. This is intended to
# mimic the behavior a user would get from having a separate clone for each
# branch and switching directories in order to switch branches.

# # # USAGE # # #
# First, make sure that the script is executable ("chmod a+x icheckout.py").
# After this, you can simply call "./icheckout.py destination_branch". You
# should be able to use any other arguments normally used with 'git checkout'
# as long as the branch name is the last argument to this script.
#
#
# To make an alias (so you can use, for example, "git icheckout
# destination_branch" instead), add the following lines to your .git/config:
#
# [alias]
#     icheckout = !./icheckout.py
#
# In my setup, icheckout.py is in the root folder of the repository. You may
# prefer to store the script in your /usr/local/bin folder.



import sys
import re
import subprocess
import time

# Prefix to be used for the stash message (used to indicate that a stash was
# created by this script)
prefix = "ICHECKOUT_AUTOSTASH"

def getCurrentBranch():
	"""Determines the current branch name using the 'git branch' command. Looks
	for a line prefixed by an asterisk."""
	p = subprocess.Popen(["git", "branch", "--no-color"], stdout=subprocess.PIPE)
	branches = p.communicate()[0]
	potential_match = re.search("\* .*\n", branches)
	return branches[potential_match.start()+2:potential_match.end()-1]

def determineSavedStashNumber(branch_name):
	"""Looks for previously saved stashes via the 'git stash list' command.
		Checks the following for each line:
		
		* Non-empty string
		* Contains the autostash prefix
		* Contains the destination branch name
		* Contains the string 'stash@{'

		Returns None in the event of an error or if no applicable stash is
		found. Otherwise, returns the number corresponding to the stash.

		Note: always chooses the first stash that meets the above criteria.
	"""
	p = subprocess.Popen(["git", "stash", "list"], stdout=subprocess.PIPE)
	stash_list = p.communicate()[0]
	list_of_stashes = re.split("\n", stash_list)
	for stash_descr in list_of_stashes:
		if len(stash_descr) == 0:
			continue

		# Make sure it's an autostashed stash
		if re.search(prefix, stash_descr) is None:
			continue

		# Contains the prefix, need to check for the branch name
		if re.search(branch_name, stash_descr) is None:
			continue	# none for this branch

		# Contains the prefix and is for this branch -- time to extract the
		# stash number
		match = re.search("stash@{", stash_descr)
		if match is None:
			print "Error: could not determine stash number"
			return None
		else:
			try:
				return int(stash_descr[match.end():match.end()+1])
			except:
				return None
		
	return None		# never found a candidate stash



# Determine branches
from_branch = getCurrentBranch()
to_branch = sys.argv[-1]

# Check to make sure we're not already on that branch
if from_branch == to_branch:
	print "Already on '" + from_branch + "'"
	sys.exit()

# Tell the user what's happening
print "Intelligently moving from branch", from_branch, "to branch", to_branch

# Stash the current changes
stash_string = "\"" + prefix + " " + from_branch + " " + time.asctime() + "\""
subprocess.call(["git", "stash", "save", "--quiet", stash_string])

# Check out the new branch
subprocess.call( ["git", "checkout"] + sys.argv[1:] )

# Look for previous stashes for the new branch
num = determineSavedStashNumber(to_branch)
if num is None:
	print "Error: no stash applied for the destination branch"
	sys.exit()

# Apply the stash
stash_name = "stash@{" + str(num) + "}"
subprocess.call(["git", "stash", "apply", stash_name, "--quiet"])

# Drop the stash from the list now that it's been applied
subprocess.call(["git", "stash", "drop", stash_name, "--quiet"])
