#! python3
# Gets filepath from commandline.

import os


def getFilepath():

    while True:
        # Try to input filepath, keep trying until correct input
        # or 'quit' keyword.
        try:
            print('%s' % "Enter filepath. Relative paths to the cwd are acceptable.")
            print('%s' % "Enter 'quit' or 'q' to exit.")
            filepath = input()
            if filepath.startswith('q'):
                sys.exit()
                quit()
            elif not os.path.exists(filepath):
                raise IOError

        except IOError:
            print('%s' % "IOError. Enter real filepath")
            continue

        break

    return filepath

if __name__ == '__main__':
	import sys
	filepath = getFile()
	print('%s%s' % ('Filepath: ', filepath))
	sys.exit()
	quit()