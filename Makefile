.PHONY: all sdist wheel sign upload clean


all: clean sdist wheel

sdist:
	python setup.py sdist

wheel:
	python setup.py bdist_wheel

sign: sdist wheel
	for f in dist/*.gz dist/*.whl; do \
	    gpg --detach-sign --armor $$f; \
	done

upload:
	twine upload dist/*

clean:
	-rm -r build
	-rm -r dist
	-rm -r *.egg-info
