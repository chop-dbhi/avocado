DOCS_DIR = ./docs
PID_FILE = .watch-pid
SASS_DIR = ./docs/scss
CSS_DIR = ./docs/css

sass:
	@echo 'Compiling Sass...'
	@mkdir -p ${CSS_DIR}
	@`which sass` --scss --style=compressed ${SASS_DIR}:${CSS_DIR} -r ${SASS_DIR}/bourbon/lib/bourbon.rb --update

watch: unwatch
	@echo 'Watching in the background...'
	@`which sass` --scss --style=compressed ${SASS_DIR}:${CSS_DIR} \
		-r ${SASS_DIR}/bourbon/lib/bourbon.rb --watch &> /dev/null & echo $$! >> ${PID_FILE}

unwatch:
	@if [ -f ${PID_FILE} ]; then \
		echo 'Watchers stopped'; \
		for pid in `cat ${PID_FILE}`; do kill -9 $$pid; done; \
		rm ${PID_FILE}; \
	fi;

clean:
	@rm -rf ${CSS_DIR}

.PHONY: sass watch unwatch clean
