#!/bin/bash

FILE=$1

if [[ -z "$FILE" ]]; then
    echo "Please specify a .pot file to convert a wordlist."
    exit 1;
fi

if [[ ! -f "$FILE"  ]]; then
    echo "The specified file does not exist!"
fi

NEW_FILENAME=$(echo $FILE | awk -F '/' '{print $NF}'  | sed s/pot/lst/)

cut -d":" -f2 $FILE | sort -u > $NEW_FILENAME

NEW_FILE_LOCATION=$(pwd)

echo "[*] New wordlist file created from "$FILE" !"
echo "[*] Stored in "$NEW_FILE_LOCATION"/"$NEW_FILENAME

exit 0