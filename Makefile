.PHONY: full sdist wheel upload clean


full: clean sdist wheel

sdist:
	python setup.py sdist

wheel:
	python setup.py bdist_wheel

upload:
	twine upload dist/*

clean:
	-rm -r build
	-rm -r dist
	-rm -r src/django_otp.egg-info
