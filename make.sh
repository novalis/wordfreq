set -xeuo pipefail

function process() {
    file=$1
    curl http://storage.googleapis.com/books/ngrams/books/$file.gz |gzip -d| tr 'A-Z' 'a-z' | sort --buffer-size=19G > "$file.tr"
    mv "$file.tr" "$file"

    python filter2.py "popular-ngrams" "$file"
    rm "$file"
}

base="googlebooks-eng-all-1gram-20120701-"

for i in $(echo {a..z} {0..9})
do
    process "$base$i"
done

for n in 2 3
do
    base="googlebooks-eng-all-${n}gram-20120701-"

    for i in $(echo {a..z})
    do
	for j in $(echo {a..z})
	do
	    process "$base$i$j"
	done
    done


    for i in $(echo {0..9})
    do
	process "$base$i"
    done
done
