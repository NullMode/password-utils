#!/usr/bin/python
import os.path
import sys

# Check for request library support
try:
    import requests
except ImportError:
    print "[1] 'requests' library not installed! E.G pip install requests"
    sys.exit(1)


def run():
    if len(sys.argv) < 2 or len(sys.argv) > 2:
        print "[*] Usage: ./script <input file of hashes>"
        print "[*] Note:  Raw hashes only"
        sys.exit(1)
    elif not os.path.isfile(sys.argv[1]):
        print "[!] File could not be opened! Does it exist?"
        sys.exit(1)

    error = False

    try:
        with open(sys.argv[1]) as file_name:
            # For each hash in file do a request
            for hash_value in file_name:
                req = requests.get('https://api.leakdb.net/?j=%s' % hash_value.strip())
                result = req.json()
                if result['found'] == 'true':
                    print '%s:%s' % (hash_value.strip(), result['hashes'][0]['plaintext'])
    except IOError, e:
        print e
        error = True
        print "[!] File or communication error!"
    finally:
        if error:
            sys.exit(1)


if __name__ == "__main__":
    run()
