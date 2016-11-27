.PHONY: all sdist wheel sign upload docs clean


all: clean sdist wheel docs

sdist:
	python setup.py sdist

wheel:
	python setup.py bdist_wheel

sign: sdist wheel
	for f in dist/*.gz dist/*.whl; do \
	    gpg --detach-sign --armor $$f; \
	done

upload: sign
	twine upload dist/*

docs:
	$(MAKE) -C docs html zip

clean:
	-rm -r build
	-rm -r dist
	-rm -r *.egg-info
	-$(MAKE) -C docs clean
