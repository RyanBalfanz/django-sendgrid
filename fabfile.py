import fabric

def release():
	fabric.operations.local("python setup.py sdist register upload")
