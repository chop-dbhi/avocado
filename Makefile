docs:
	@sphinx-apidoc --force -o docs/api avocado
	@make -C docs -f Makefile html

.PHONY: docs
