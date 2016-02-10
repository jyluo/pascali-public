import logging
import os
import sys
import platform
import pprint
import subprocess
import traceback


def run_checker(javac_commands,args):
	# checker-framework javac.
	javacheck = os.environ['JSR308']+"/checker-framework/checker/bin/javac"
	checker_command = []
	checker_command.extend([javacheck])

	for jc in javac_commands:
		pprint.pformat(jc)
		javac_switches = jc['javac_switches']
		cp = javac_switches['classpath']
		cmd = checker_command + ["-processor"]

		# ensure all args passed to the checker are appended as an element of the cmd argument list
		# otherwise it treats it as a single long string (the processor name argument)
		for arg in args.checker.split(' '):
			cmd = cmd + [arg]

		cmd = cmd + ["-classpath", cp]
		
		# ensure every java file is appended separately as an element of the cmd argument list
		# otherwise it treats the set of files as a single long string (file argument) and expects
		# to find 1 file with that long name
		for jf in jc['java_files']:
			cmd = cmd + [jf]
		
		print ("Running %s" % ' '.join(cmd))
		try:
			print (subprocess.check_output(cmd, stderr=subprocess.STDOUT))
		except subprocess.CalledProcessError as e:
			print e.output
