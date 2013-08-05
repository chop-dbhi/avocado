docs:
	@sphinx-apidoc --force -o docs/api avocado
	@make -C docs html

.PHONY: docs
