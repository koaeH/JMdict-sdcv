LINK := "ftp://ftp.edrdg.org/pub/Nihongo/JMdict.gz"
BASE := $(shell date -- "+org.edrdg.jmdict-%Y%m%d")

REPO := ${HOME}/.stardict/dic

all:
	curl -s -o $(BASE).xml.z -- $(LINK)
	gzip --decompress --no-name $(BASE).xml.z
	python -BO kirke.py artifex $(BASE).xml
	python -BO kirke.py package $(BASE).o

install:
	@install -m 755 --directory $(REPO)
	tar -C $(REPO) -x -f $(BASE).tar.gz
